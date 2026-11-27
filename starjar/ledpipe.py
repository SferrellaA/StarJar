"""Send colors to the LED helper. The helper never sees Morse text."""

from __future__ import annotations

import socket
import threading

from starjar.ipc import LED_SOCKET


class SocketStrip:
    """setPixelColor/show, same shape play() already uses."""

    def __init__(self, count: int, path=LED_SOCKET):
        self._count = count
        self._path = path
        self._color = (0, 0, 0)
        self._sock: socket.socket | None = None
        self._lock = threading.Lock()

    def numPixels(self) -> int:
        return self._count

    def setPixelColor(self, _index: int, packed: int) -> None:
        self._color = ((packed >> 16) & 255, (packed >> 8) & 255, packed & 255)

    def show(self) -> None:
        red, green, blue = self._color
        line = f"{red} {green} {blue}\n".encode("ascii")
        with self._lock:
            try:
                self._send(line)
            except OSError:
                self._close()

    def _send(self, line: bytes) -> None:
        if self._sock is None:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect(str(self._path))
            self._sock = sock
        assert self._sock is not None
        self._sock.sendall(line)

    def _close(self) -> None:
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
