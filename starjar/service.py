"""Boot the jar. A restart rereads /run/starjar and does not roll a new attempt."""

from __future__ import annotations

import json
import os
import signal
import socket
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

from aiohttp import web

from starjar.config import load_config
from starjar.ipc import COMMANDS, CONTROL_SOCKET
from starjar.ledpipe import SocketStrip
from starjar.leds import DOT_COLOR, DASH_COLOR, OFF, paint
from starjar.mode import association_in_progress, decide
from starjar.morse import WORD_GAP, Signal, encode, iter_signals, phase_one_phrase
from starjar.radio import RadioError, RadioHelper
from starjar.secrets import Attempt, load_or_create
from starjar.web import AppState, make_app

UNIT_S = 0.25
SETTLE_S = 45
ACTIVATING_CAP_S = 180


def scrub(message: str, secrets: tuple[str, ...]) -> str:
    clean = message
    for secret in secrets:
        if secret:
            clean = clean.replace(secret, "[redacted]")
    return clean


def radio_wanted(stage: str) -> bool:
    return stage == "phase1"


def wait_for_mode(collect, sleep, monotonic, timeout: float = SETTLE_S, cap: float = ACTIVATING_CAP_S) -> str:
    """diagnostic or challenge. Still activating after the short timeout is not settled."""

    start = monotonic()
    while True:
        snapshot = collect()
        elapsed = monotonic() - start
        decision = decide(snapshot, timed_out=elapsed >= timeout)
        if decision != "settling":
            return decision
        if association_in_progress(snapshot) and elapsed >= timeout + cap:
            return "diagnostic"
        sleep(1)


def command_result(cmd: str, mode: str, stage: str, associated: bool) -> tuple[str, dict]:
    if cmd == "status":
        return stage, _status(True, mode, stage, associated)
    if cmd not in COMMANDS:
        return stage, {"ok": False}
    return cmd, _status(True, mode, cmd, associated)


def _status(ok: bool, mode: str, stage: str, associated: bool) -> dict:
    return {"ok": ok, "mode": mode, "stage": stage, "associated": associated}


@dataclass
class Box:
    mode: str
    stage: str
    associated: bool
    attempt: Attempt
    web: AppState
    stop: threading.Event = field(default_factory=threading.Event)
    changed: threading.Event = field(default_factory=threading.Event)
    generation: int = 0
    resume: str = "idle"
    lock: threading.Lock = field(default_factory=threading.Lock)

    def secrets(self) -> tuple[str, str]:
        return (self.attempt.sid, self.attempt.code)

    def set_stage(self, stage: str) -> None:
        with self.lock:
            if stage == "leds" and self.stage != "leds":
                self.resume = self.stage
            self.stage = stage
            self.generation += 1
            self.web.stage = stage
            self.changed.set()

    def set_associated(self, associated: bool) -> None:
        with self.lock:
            self.associated = associated

    def snapshot(self) -> tuple[str, str, bool, int]:
        with self.lock:
            return self.mode, self.stage, self.associated, self.generation

    def wait(self, timeout: float) -> None:
        self.changed.wait(timeout)


def main() -> None:
    config_path = Path(os.environ.get("STARJAR_CONFIG", "config.toml"))
    if not config_path.is_file():
        config_path = Path("config.example.toml")
    config = load_config(config_path)
    attempt_dir = config.attempt
    if not attempt_dir.is_dir():
        _log("attempt directory is missing")
        raise SystemExit(1)
    helper = RadioHelper()
    try:
        helper.delete_attempts()
    except RadioError:
        _log("could not delete an attempt profile")
    # /run/starjar/hold keeps the bench dark. Unplug clears it. make jar sets it.
    held = (attempt_dir / "hold").is_file()
    if held:
        mode = "challenge"
    else:
        try:
            mode = wait_for_mode(helper.snapshot, time.sleep, time.monotonic)
        except RadioError:
            _log("could not read the radio")
            mode = "challenge"
    _log(f"mode {mode}")
    rng_mod = __import__("random")
    attempt = load_or_create(attempt_dir, rng_mod.SystemRandom())
    stage = "idle" if held or mode == "diagnostic" else "phase1"
    web_state = AppState(
        www=config.www,
        challenge_tree=config.challenge_tree,
        trivia=config.trivia,
        scoreboard=config.scoreboard,
        attempt=attempt,
        stage=stage,
    )
    box = Box(
        mode=mode,
        stage=web_state.stage,
        associated=False,
        attempt=attempt,
        web=web_state,
    )
    strip = SocketStrip(config.led_count)
    paint(strip, OFF)
    strip.show()
    _start_web(web_state, config.host, config.port)
    control = threading.Thread(target=_control, args=(box,), name="control", daemon=True)
    control.start()
    morse = threading.Thread(target=_morse, args=(box, strip), name="morse", daemon=True)
    morse.start()
    radio = threading.Thread(target=_radio, args=(box, helper), name="radio", daemon=True)
    radio.start()
    _install_stop(box)
    _log("ready")
    while not box.stop.wait(3600):
        pass
    paint(strip, OFF)
    strip.show()


def _start_web(state: AppState, host: str, port: int) -> None:
    def run() -> None:
        web.run_app(make_app(state), host=host, port=port, access_log=None, handle_signals=False)

    threading.Thread(target=run, name="web", daemon=True).start()


def _control(box: Box, path: Path = CONTROL_SOCKET) -> None:
    if path.exists():
        path.unlink()
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(str(path))
    os.chmod(path, 0o660)
    sock.listen(4)
    sock.settimeout(0.5)
    try:
        while not box.stop.is_set():
            try:
                conn, _ = sock.accept()
            except TimeoutError:
                continue
            with conn:
                _one_command(conn, box)
    finally:
        sock.close()


def _one_command(conn: socket.socket, box: Box) -> None:
    try:
        data = b""
        conn.settimeout(2)
        while b"\n" not in data and len(data) < 1024:
            chunk = conn.recv(256)
            if not chunk:
                break
            data += chunk
        cmd = json.loads(data.decode("ascii")).get("cmd", "")
        mode, stage, associated, _gen = box.snapshot()
        new_stage, payload = command_result(str(cmd), mode, stage, associated)
        if cmd != "status" and payload.get("ok") and new_stage != stage:
            box.set_stage(new_stage)
            payload = _status(True, mode, new_stage, associated)
        conn.sendall((json.dumps(payload) + "\n").encode("ascii"))
    except Exception:
        try:
            conn.sendall(b'{"ok":false}\n')
        except OSError:
            pass


def _radio(box: Box, helper: RadioHelper) -> None:
    while not box.stop.is_set():
        _mode, stage, _associated, _gen = box.snapshot()
        if not radio_wanted(stage):
            box.wait(0.5)
            continue
        try:
            helper.ensure()
            if helper.joined():
                box.set_associated(True)
                box.set_stage("phase2")
                continue
            helper.up()
            if helper.joined():
                box.set_associated(True)
                box.set_stage("phase2")
                continue
        except RadioError:
            _log("wlan0 connect attempt failed", box.secrets())
        box.wait(2)


def _morse(box: Box, strip: SocketStrip) -> None:
    while not box.stop.is_set():
        _mode, stage, _associated, gen = box.snapshot()
        if stage in {"phase1", "phase1-dry"}:
            signals = iter_signals(phase_one_phrase(box.attempt.sid))
            signals.append(Signal(False, WORD_GAP))
            _play(signals, strip, box, gen)
        elif stage == "phase2":
            signals = encode(box.attempt.code) + [Signal(False, WORD_GAP)]
            _play(signals, strip, box, gen)
        elif stage == "leds":
            _self_test(strip, box, gen)
            box.set_stage(box.resume or "idle")
        else:
            paint(strip, OFF)
            strip.show()
            box.wait(0.5)


def _play(signals, strip: SocketStrip, box: Box, gen: int) -> None:
    def sleep_units(units: int) -> None:
        remaining = units * UNIT_S
        while remaining > 0:
            if box.stop.is_set() or box.generation != gen:
                raise _Cut
            step = min(0.05, remaining)
            time.sleep(step)
            remaining -= step

    try:
        from starjar.leds import play

        play(signals, strip, sleep_units)
    except _Cut:
        return


def _self_test(strip: SocketStrip, box: Box, gen: int) -> None:
    for color in (DOT_COLOR, DASH_COLOR, OFF):
        if box.stop.is_set() or box.generation != gen:
            return
        paint(strip, color)
        strip.show()
        time.sleep(0.4)


def _log(message: str, secrets: tuple[str, ...] = ()) -> None:
    print(scrub(message, secrets), file=sys.stderr, flush=True)


class _Cut(Exception):
    pass


def _install_stop(box: Box) -> None:
    def _stop(_signum, _frame) -> None:
        box.stop.set()

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
