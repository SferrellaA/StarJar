#!/usr/bin/env python3
"""Play one Morse letter at a time on the jar, and print the expected mark here.

The strip runs this checkout's encode() and play() over the USB shell. Space
advances. Ctrl+C exits 1. Finishing the alphabet exits 0.

Usage: uv run scripts/morse-visual.py
       uv run scripts/morse-visual.py --print-only
       uv run scripts/morse-visual.py --letters SOS
"""

from __future__ import annotations

import argparse
import base64
import io
import os
import selectors
import shlex
import signal
import subprocess
import sys
import tarfile
import termios
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
# Repo root on the laptop. Next to this file after the bundle is copied to the jar.
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from starjar.morse import WORD_GAP, Signal, encode, format_step  # noqa: E402
from starjar.secrets import TOKEN_ALPHABET  # noqa: E402

DEST = "/tmp/starjar-morse-visual"
SSH = ROOT / "scripts" / "starjar-ssh"
DEFAULT_HOSTS = ("169.254.55.1", "10.55.0.1")


def main(argv: list[str] | None = None) -> int:
    args = _parse(argv)
    if args.play:
        return _play_remote(args)
    letters = _letters(args.letters)
    if args.print_only:
        for letter in letters:
            print(format_step(letter), flush=True)
        return 0
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("morse-visual needs this terminal", file=sys.stderr)
        return 1
    try:
        return _watch(args, letters)
    except KeyboardInterrupt:
        print("\nfailed", flush=True)
        return 1


def _parse(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Watch the jar spell one letter at a time.")
    parser.add_argument("--letters", default=TOKEN_ALPHABET, help="letters to step through")
    parser.add_argument("--unit-ms", type=int, default=250)
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument("--pin", type=int, default=18)
    parser.add_argument("--order", default="RGB")
    parser.add_argument("--print-only", action="store_true", help="print the expected marks and exit")
    parser.add_argument("--play", default="", help=argparse.SUPPRESS)
    parser.add_argument("--path", default="", help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def _letters(raw: str) -> str:
    letters = "".join(char for char in raw.upper() if not char.isspace())
    if not letters:
        raise SystemExit("letters must be Morse characters, one at a time")
    try:
        for letter in letters:
            format_step(letter)
    except KeyError as exc:
        raise SystemExit(f"not a Morse letter: {exc}") from exc
    return letters


def _watch(args: argparse.Namespace, letters: str) -> int:
    env = _cached_env()
    _upload(env)
    print("Manual Morse check. The strip runs encode() and play() on the jar.", flush=True)
    print("Dots are gold, dashes are blue. Each letter repeats after a word gap.", flush=True)
    print(f"unit {args.unit_ms} ms, pin {args.pin}, {args.count} pixels.", flush=True)
    print("space = next letter, ctrl-c = fail", flush=True)
    fd = sys.stdin.fileno()
    saved = termios.tcgetattr(fd)
    attrs = termios.tcgetattr(fd)
    attrs[3] = attrs[3] & ~(termios.ICANON | termios.ECHO)
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    player: subprocess.Popen[bytes] | None = None
    pid: int | None = None
    try:
        for index, letter in enumerate(letters):
            print(format_step(letter), flush=True)
            player, pid = _start_letter(env, args, letter)
            _discard_typed()
            _wait_space()
            _stop_player(env, player, pid)
            player, pid = None, None
            if index == len(letters) - 1:
                print("passed", flush=True)
                return 0
        return 0
    except KeyboardInterrupt:
        print("\nfailed", flush=True)
        return 1
    except _Failed as exc:
        print(f"failed: {exc}", flush=True)
        return 1
    finally:
        termios.tcsetattr(fd, termios.TCSANOW, saved)
        if player is not None:
            _stop_player(env, player, pid)


def _discard_typed() -> None:
    fd = sys.stdin.fileno()
    sel = selectors.DefaultSelector()
    sel.register(fd, selectors.EVENT_READ)
    try:
        while sel.select(0):
            if not os.read(fd, 1024):
                break
    finally:
        sel.unregister(fd)
        sel.close()


def _wait_space() -> None:
    while True:
        key = os.read(sys.stdin.fileno(), 1)
        if not key:
            raise _Failed("terminal closed")
        if key == b" ":
            _drain_repeat()
            return


def _drain_repeat() -> None:
    fd = sys.stdin.fileno()
    sel = selectors.DefaultSelector()
    sel.register(fd, selectors.EVENT_READ)
    try:
        while sel.select(0.05):
            extra = os.read(fd, 32)
            if not extra or b" " not in extra:
                break
    finally:
        sel.unregister(fd)
        sel.close()


def _start_letter(
    env: dict[str, str], args: argparse.Namespace, letter: str
) -> tuple[subprocess.Popen[bytes], int]:
    script = f"{DEST}/morse-visual.py"
    command = " ".join(
        [
            "sudo",
            "-n",
            "python3",
            "-u",
            shlex.quote(script),
            "--play",
            shlex.quote(letter),
            "--path",
            shlex.quote(DEST),
            "--unit-ms",
            str(args.unit_ms),
            "--count",
            str(args.count),
            "--pin",
            str(args.pin),
            "--order",
            shlex.quote(args.order),
        ]
    )
    proc = subprocess.Popen(
        [str(SSH), command],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        start_new_session=True,
    )
    assert proc.stdout is not None
    line = _readline(proc, 20)
    if not line.startswith("READY "):
        _stop_player(env, proc, None)
        err = _stderr(proc)
        raise _Failed(err or line or "strip did not start")
    try:
        pid = int(line.split()[1])
    except (IndexError, ValueError) as exc:
        _stop_player(env, proc, None)
        raise _Failed(line) from exc
    return proc, pid


def _readline(proc: subprocess.Popen[bytes], timeout: float) -> str:
    assert proc.stdout is not None
    sel = selectors.DefaultSelector()
    sel.register(proc.stdout, selectors.EVENT_READ)
    try:
        if not sel.select(timeout):
            return ""
        return proc.stdout.readline().decode("ascii", "replace").strip()
    finally:
        sel.close()


def _stop_player(env: dict[str, str], proc: subprocess.Popen[bytes], pid: int | None) -> None:
    if pid is not None:
        try:
            subprocess.run(
                [str(SSH), f"sudo -n kill -TERM {pid}"],
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=15,
                check=False,
            )
        except subprocess.TimeoutExpired:
            pass
    if proc.poll() is None:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait(timeout=5)


def _stderr(proc: subprocess.Popen[bytes]) -> str:
    if proc.stderr is None:
        return ""
    try:
        data = proc.stderr.read()
    except Exception:
        return ""
    return data.decode("utf-8", "replace").strip()


def _cached_env() -> dict[str, str]:
    hosts = os.environ.get("STARJAR_SSH_HOSTS", " ".join(DEFAULT_HOSTS)).split()
    errors: list[str] = []
    for host in hosts:
        env = os.environ.copy()
        env["STARJAR_SSH_HOSTS"] = host
        result = subprocess.run(
            [str(SSH), "true"],
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=20,
            check=False,
        )
        if result.returncode == 0:
            return env
        err = result.stderr.decode("utf-8", "replace").strip()
        if err:
            errors.append(err)
    detail = errors[-1] if errors else "wired ssh failed"
    raise _Failed(detail)


def _upload(env: dict[str, str]) -> None:
    payload = base64.b64encode(_bundle()).decode("ascii")
    command = (
        f"rm -rf {shlex.quote(DEST)} && mkdir -p {shlex.quote(DEST)} && "
        f"tr -d '\\r' | base64 -d | tar -xz -C {shlex.quote(DEST)}"
    )
    result = subprocess.run(
        [str(SSH), command],
        env=env,
        input=payload.encode("ascii"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
    )
    if result.returncode != 0:
        err = result.stderr.decode("utf-8", "replace").strip()
        raise _Failed(err or "could not copy the morse player to the jar")


def _bundle() -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        tar.add(ROOT / "starjar", arcname="starjar", filter=_skip_cache)
        tar.add(Path(__file__), arcname="morse-visual.py")
    return buf.getvalue()


def _skip_cache(info: tarfile.TarInfo) -> tarfile.TarInfo | None:
    if "__pycache__" in info.name or info.name.endswith(".pyc"):
        return None
    return info


def _play_remote(args: argparse.Namespace) -> int:
    if args.path:
        sys.path.insert(0, args.path)
    _add_user_site()
    from starjar.leds import OFF, open_strip, play

    letter = args.play
    format_step(letter)
    unit_s = args.unit_ms / 1000
    stop = False

    def _stop(_signum, _frame) -> None:
        nonlocal stop
        stop = True

    for sig in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(sig, _stop)

    def sleep_units(units: int) -> None:
        remaining = units * unit_s
        while remaining > 0:
            if stop:
                raise SystemExit(0)
            step = min(0.05, remaining)
            time.sleep(step)
            remaining -= step

    strip = None
    try:
        strip = open_strip(args.count, args.pin, args.order)
        print(f"READY {os.getpid()}", flush=True)
        signals = encode(letter) + [Signal(False, WORD_GAP)]
        while not stop:
            play(signals, strip, sleep_units)
    finally:
        if strip is not None:
            strip.fill(OFF)
            strip.show()
    return 0


def _add_user_site() -> None:
    import site

    homes = [Path("/home/star")]
    if Path.home() not in homes:
        homes.append(Path.home())
    for home in homes:
        lib = home / ".local" / "lib"
        if not lib.is_dir():
            continue
        for path in sorted(lib.glob("python*/site-packages")):
            site.addsitedir(str(path))


class _Failed(Exception):
    pass


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except _Failed as exc:
        print(f"failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
