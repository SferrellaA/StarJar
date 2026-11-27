"""Root radio helper. sudo logs the verb, not the attempt."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from starjar.mode import ATTEMPT_PREFIX, is_attempt
from starjar.nmparse import parse_connections, parse_devices, parse_ssids, wlan_state
from starjar.radio import (
    RadioError,
    add_open_client_command,
    assert_safe,
    clear_security_command,
    modify_open_client_command,
    up_command,
)
from starjar.secrets import assert_attempt_dir
from starjar.wifi import delete_command

ATTEMPT_DIR = Path("/run/starjar")


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        return 2
    try:
        if args[0] == "snapshot":
            sys.stdout.write(snapshot_text())
            return 0
        if args[0] == "delete-attempts":
            delete_attempts()
            return 0
        if args[0] == "ensure":
            ensure()
            return 0
        if args[0] == "up":
            return up()
        if args[0] == "joined":
            return 0 if joined() else 1
    except Exception:
        print("radio helper failed", file=sys.stderr)
        return 1
    return 2


def snapshot_text() -> str:
    secret = _sid()
    _quiet(["nmcli", "device", "wifi", "rescan", "ifname", "wlan0"], timeout=15)
    connections = parse_connections(
        _out(["nmcli", "-t", "-f", "NAME,TYPE,AUTOCONNECT", "connection", "show"])
    )
    devices = parse_devices(
        _out(["nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device", "status"])
    )
    visible = parse_ssids(
        _out(["nmcli", "-t", "-f", "SSID", "device", "wifi", "list", "ifname", "wlan0"])
    )
    associated, activating = wlan_state(devices)
    lines = [
        f"associated\t{_public_name(associated)}",
        f"activating\t{_public_name(activating)}",
    ]
    for ssid in sorted(visible):
        if secret and ssid == secret:
            continue
        lines.append(f"visible\t{ssid}")
    for name, kind, autoconnect in connections:
        if kind not in {"wifi", "802-11-wireless"} or is_attempt(name):
            continue
        ssid = _out(["nmcli", "-g", "802-11-wireless.ssid", "connection", "show", name]).strip()
        lines.append(f"profile\t{name}\t{ssid}\t{'yes' if autoconnect else 'no'}")
    return "\n".join(lines) + "\n"


def delete_attempts() -> None:
    listed = parse_connections(
        _out(["nmcli", "-t", "-f", "NAME,TYPE,AUTOCONNECT", "connection", "show"])
    )
    for name, _kind, _auto in listed:
        if is_attempt(name):
            _quiet(delete_command(name), timeout=15)


def ensure() -> None:
    sid = _sid()
    if not sid:
        raise RadioError("radio helper failed")
    name = f"{ATTEMPT_PREFIX}{sid}"
    listed = _out(["nmcli", "-t", "-f", "NAME", "connection", "show"])
    names = [line.split(":", 1)[0] for line in listed.splitlines() if line.strip()]
    if name not in names:
        _quiet(add_open_client_command(sid), timeout=15)
    _quiet(modify_open_client_command(name), timeout=15)
    # An existing profile may still be WEP. Open means no security setting.
    _quiet(clear_security_command(name), timeout=15)


def up() -> int:
    sid = _sid()
    if not sid:
        return 1
    return _quiet(up_command(f"{ATTEMPT_PREFIX}{sid}"), timeout=12)


def joined() -> bool:
    devices = parse_devices(
        _out(["nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device", "status"])
    )
    associated, _activating = wlan_state(devices)
    return is_attempt(associated)


def _sid() -> str:
    path = ATTEMPT_DIR / "sid"
    try:
        assert_attempt_dir(ATTEMPT_DIR)
        value = path.read_text(encoding="ascii").strip()
    except (OSError, UnicodeError, ValueError):
        return ""
    return value


def _public_name(name: str | None) -> str:
    if not name:
        return "none"
    if is_attempt(name):
        return "attempt"
    return name


def _out(argv: list[str], timeout: float = 20) -> str:
    assert_safe(argv)
    proc = subprocess.Popen(
        argv,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    try:
        out, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        _kill(proc)
        raise RadioError("radio helper failed") from None
    if proc.returncode != 0:
        raise RadioError("radio helper failed")
    return out.decode("utf-8", "replace")


def _quiet(argv: list[str], timeout: float) -> int:
    assert_safe(argv)
    proc = subprocess.Popen(
        argv,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    try:
        return proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        _kill(proc)
        return 1


def _kill(proc: subprocess.Popen[bytes]) -> None:
    import os
    import signal

    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait(timeout=3)


if __name__ == "__main__":
    raise SystemExit(main())
