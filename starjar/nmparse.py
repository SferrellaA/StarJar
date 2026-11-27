"""Parse nmcli text into a mode snapshot. No radio calls."""

from __future__ import annotations

from starjar.mode import Profile, Snapshot


def split_terse(line: str) -> list[str]:
    """Split an nmcli -t line. Colons in values are escaped as \\:."""

    parts: list[str] = []
    buf: list[str] = []
    escaped = False
    for char in line.rstrip("\n"):
        if escaped:
            buf.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == ":":
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(char)
    parts.append("".join(buf))
    return parts


def parse_connections(text: str) -> list[tuple[str, str, bool]]:
    rows: list[tuple[str, str, bool]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        name, kind, autoconnect = split_terse(line)[:3]
        rows.append((name, kind, autoconnect == "yes"))
    return rows


def parse_devices(text: str) -> list[tuple[str, str, str, str]]:
    rows: list[tuple[str, str, str, str]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        fields = split_terse(line)
        while len(fields) < 4:
            fields.append("")
        device, kind, state, connection = fields[:4]
        rows.append((device, kind, state, connection))
    return rows


def parse_ssids(text: str) -> frozenset[str]:
    found: set[str] = set()
    for line in text.splitlines():
        if not line.strip():
            continue
        ssid = split_terse(line)[0].strip()
        if ssid:
            found.add(ssid)
    return frozenset(found)


def wlan_state(devices: list[tuple[str, str, str, str]]) -> tuple[str | None, str | None]:
    """Return (associated profile, activating profile) for wlan0 only."""

    for device, _kind, state, connection in devices:
        if device != "wlan0":
            continue
        name = connection or None
        if state == "connected" or state.startswith("connected"):
            return name, None
        if state.startswith("disconnected") or state in {"unavailable", "unmanaged", "failed"}:
            return None, None
        return None, name
    return None, None


def snapshot_from(
    connections: list[tuple[str, str, bool]],
    devices: list[tuple[str, str, str, str]],
    visible: frozenset[str],
    ssids: dict[str, str | None],
) -> Snapshot:
    profiles: list[Profile] = []
    for name, kind, autoconnect in connections:
        if kind not in {"wifi", "802-11-wireless"}:
            continue
        profiles.append(Profile(name, ssids.get(name) or None, autoconnect))
    associated, activating = wlan_state(devices)
    return Snapshot(
        associated_name=associated,
        activating_name=activating,
        visible_ssids=visible,
        profiles=tuple(profiles),
    )
