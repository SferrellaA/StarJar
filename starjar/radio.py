"""wlan0 client commands. The human creates the open network. Never ethernet."""

from __future__ import annotations

import os
import signal
import subprocess
from collections.abc import Callable

from starjar.mode import ATTEMPT_PREFIX, Profile, Snapshot, is_attempt
from starjar.nmparse import parse_connections, parse_devices, parse_ssids, snapshot_from
from starjar.secrets import TOKEN_ALPHABET

# usb0 is the operator shell. eth0 is the same rule. Never name them here as a target.
_FORBIDDEN = {"usb0", "eth0", "eth1", "lo"}


class RadioError(RuntimeError):
    """nmcli failed. The message must not include an attempt secret or argv."""


def add_open_client_command(sid: str, iface: str = "wlan0") -> list[str]:
    _wlan_sid(sid, iface)
    return [
        "nmcli",
        "connection",
        "add",
        "type",
        "wifi",
        "ifname",
        iface,
        "con-name",
        f"{ATTEMPT_PREFIX}{sid}",
        "autoconnect",
        "no",
        "ssid",
        sid,
        "wifi.mode",
        "infrastructure",
    ]


def modify_open_client_command(name: str) -> list[str]:
    if not is_attempt(name):
        raise ValueError("refusing to modify a non-attempt profile")
    return [
        "nmcli",
        "connection",
        "modify",
        name,
        "connection.autoconnect",
        "no",
        "connection.interface-name",
        "wlan0",
        "802-11-wireless.mode",
        "infrastructure",
    ]


def clear_security_command(name: str) -> list[str]:
    """Drop WEP/WPA settings. key-mgmt none is WEP, not an open network."""

    if not is_attempt(name):
        raise ValueError("refusing to modify a non-attempt profile")
    return [
        "nmcli",
        "connection",
        "modify",
        name,
        "remove",
        "802-11-wireless-security",
    ]


def up_command(name: str, iface: str = "wlan0") -> list[str]:
    if iface != "wlan0":
        raise ValueError("refusing to touch a non-wlan interface")
    if not is_attempt(name):
        raise ValueError("refusing to bring up a non-attempt profile")
    return ["nmcli", "connection", "up", name, "ifname", iface]


def assert_safe(argv: list[str]) -> None:
    if not argv or argv[0] != "nmcli":
        raise ValueError("refusing")
    for arg in argv:
        if arg in _FORBIDDEN:
            raise ValueError("refusing to touch ethernet")
    if "ifname" in argv:
        iface = argv[argv.index("ifname") + 1]
        if iface != "wlan0":
            raise ValueError("refusing to touch a non-wlan interface")
    if argv[1:3] in ([
        ["connection", "delete"],
        ["connection", "modify"],
        ["connection", "up"],
    ]):
        name = argv[3]
        if not is_attempt(name):
            raise ValueError("refusing to change a non-attempt profile")


def collect_snapshot(run: Callable[[list[str]], str], rescan: bool = False) -> Snapshot:
    if rescan:
        try:
            run(["nmcli", "device", "wifi", "rescan", "ifname", "wlan0"])
        except RadioError:
            pass
    connections = parse_connections(
        run(["nmcli", "-t", "-f", "NAME,TYPE,AUTOCONNECT", "connection", "show"])
    )
    devices = parse_devices(
        run(["nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device", "status"])
    )
    visible = parse_ssids(
        run(["nmcli", "-t", "-f", "SSID", "device", "wifi", "list", "ifname", "wlan0"])
    )
    ssids: dict[str, str | None] = {}
    for name, kind, _auto in connections:
        if kind not in {"wifi", "802-11-wireless"}:
            continue
        ssid = run(["nmcli", "-g", "802-11-wireless.ssid", "connection", "show", name]).strip()
        ssids[name] = ssid or None
    return snapshot_from(connections, devices, visible, ssids)


def ensure_client(run: Callable[[list[str]], str], sid: str) -> str:
    name = f"{ATTEMPT_PREFIX}{sid}"
    listed = run(["nmcli", "-t", "-f", "NAME", "connection", "show"])
    names = [split_name(line) for line in listed.splitlines() if line.strip()]
    if name not in names:
        run(add_open_client_command(sid))
    run(modify_open_client_command(name))
    return name


def split_name(line: str) -> str:
    from starjar.nmparse import split_terse

    return split_terse(line)[0]


HELPER = "/usr/local/sbin/starjar-radio"
HELPER_VERBS = ("snapshot", "delete-attempts", "ensure", "up", "joined")


def parse_helper_snapshot(text: str) -> Snapshot:
    """Helper output uses 'attempt' instead of the SID."""

    associated = None
    activating = None
    visible: set[str] = set()
    profiles: list[Profile] = []
    for line in text.splitlines():
        parts = line.split("\t")
        if not parts or not parts[0]:
            continue
        kind = parts[0]
        if kind == "associated" and len(parts) > 1:
            associated = _attempt_label(parts[1])
        elif kind == "activating" and len(parts) > 1:
            activating = _attempt_label(parts[1])
        elif kind == "visible" and len(parts) > 1 and parts[1]:
            visible.add(parts[1])
        elif kind == "profile" and len(parts) >= 4:
            profiles.append(Profile(parts[1], parts[2] or None, parts[3] == "yes"))
    return Snapshot(associated, activating, frozenset(visible), tuple(profiles))


def _attempt_label(value: str) -> str | None:
    if value in {"", "none"}:
        return None
    if value == "attempt":
        return f"{ATTEMPT_PREFIX}"
    return value


class RadioHelper:
    """sudo verbs only. The SID stays in the root helper, not in the sudo log."""

    def __init__(self, path: str = HELPER):
        self.path = path

    def snapshot(self) -> Snapshot:
        return parse_helper_snapshot(self._text("snapshot", 25))

    def delete_attempts(self) -> None:
        self._text("delete-attempts", 20)

    def ensure(self) -> None:
        self._text("ensure", 20)

    def up(self) -> bool:
        return self._code("up", 20) == 0

    def joined(self) -> bool:
        return self._code("joined", 15) == 0

    def _text(self, verb: str, timeout: float) -> str:
        code, out = self._exec(verb, timeout)
        if code != 0:
            raise RadioError("radio helper failed")
        return out

    def _code(self, verb: str, timeout: float) -> int:
        code, _out = self._exec(verb, timeout)
        return code

    def _exec(self, verb: str, timeout: float) -> tuple[int, str]:
        if verb not in HELPER_VERBS:
            raise RadioError("radio helper failed")
        proc = subprocess.Popen(
            ["sudo", "-n", self.path, verb],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        try:
            out, _ = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            _kill(proc)
            raise RadioError("radio helper failed") from None
        return proc.returncode or 0, out.decode("utf-8", "replace")


def _wlan_sid(sid: str, iface: str) -> None:
    if iface != "wlan0":
        raise ValueError("refusing to touch a non-wlan interface")
    if not sid or any(char not in TOKEN_ALPHABET for char in sid):
        raise ValueError("sid")


class Nmcli:
    """sudo -n nmcli. stderr is discarded so a failure cannot reach the journal."""

    def __call__(self, argv: list[str], timeout: float = 20) -> str:
        assert_safe(argv)
        proc = subprocess.Popen(
            ["sudo", "-n", *argv],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        try:
            out, _ = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            _kill(proc)
            raise RadioError("nmcli timed out") from None
        if proc.returncode != 0:
            raise RadioError("nmcli failed")
        return out.decode("utf-8", "replace")


def _kill(proc: subprocess.Popen[bytes]) -> None:
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.communicate(timeout=5)
