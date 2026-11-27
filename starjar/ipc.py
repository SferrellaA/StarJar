"""Local sockets. Payloads are colors and stage names, never attempt secrets."""

from __future__ import annotations

import json
import socket
from pathlib import Path

CONTROL_SOCKET = Path("/run/starjar/control.sock")
LED_SOCKET = Path("/run/starjar/leds.sock")

COMMANDS = ("idle", "phase1-dry", "phase1", "phase2", "victory", "leds", "status")

PHASE1_WARNING = (
    "phase1 disconnects wlan0. This SSH session dies unless ethernet is up."
)


def request(cmd: str, path: Path = CONTROL_SOCKET, timeout: float = 5) -> dict:
    if cmd not in COMMANDS:
        raise ValueError(cmd)
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect(str(path))
        sock.sendall((json.dumps({"cmd": cmd}) + "\n").encode("ascii"))
        data = b""
        while b"\n" not in data and len(data) < 1024:
            chunk = sock.recv(256)
            if not chunk:
                break
            data += chunk
    finally:
        sock.close()
    payload = json.loads(data.decode("ascii"))
    if not isinstance(payload, dict):
        raise RuntimeError("control socket")
    return payload
