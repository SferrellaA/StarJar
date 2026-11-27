"""Root LED helper. Colors in, pixels out. No attempt secrets."""

from __future__ import annotations

import os
import socket
import sys
import time
from pathlib import Path


def main() -> int:
    _add_user_site()
    from starjar.leds import OFF, open_strip, paint

    path = Path(os.environ.get("STARJAR_LED_SOCKET", "/run/starjar/leds.sock"))
    count, pin, order = _settings()
    try:
        strip = open_strip(count, pin, order)
    except Exception as exc:
        print(f"led driver unavailable: {type(exc).__name__}", file=sys.stderr)
        return 1
    paint(strip, OFF)
    strip.show()
    if not _wait_dir(path.parent):
        print("attempt directory is missing", file=sys.stderr)
        return 1
    if path.exists():
        path.unlink()
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(str(path))
    os.chown(path, 0, _star_gid())
    os.chmod(path, 0o660)
    sock.listen(1)
    try:
        while True:
            conn, _ = sock.accept()
            with conn:
                _frames(conn, strip, paint)
    finally:
        paint(strip, OFF)
        strip.show()
        sock.close()
    return 0


def _frames(conn: socket.socket, strip, paint) -> None:
    buf = b""
    while True:
        try:
            chunk = conn.recv(64)
        except OSError:
            return
        if not chunk:
            return
        buf += chunk
        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            color = _color(line)
            if color is None:
                continue
            paint(strip, color)
            strip.show()


def _color(line: bytes) -> tuple[int, int, int] | None:
    parts = line.split()
    if len(parts) != 3:
        return None
    try:
        values = tuple(int(part) for part in parts)
    except ValueError:
        return None
    if any(value < 0 or value > 255 for value in values):
        return None
    return values  # type: ignore[return-value]


def _settings() -> tuple[int, int, str]:
    count = int(os.environ.get("STARJAR_LED_COUNT", "50"))
    pin = int(os.environ.get("STARJAR_LED_PIN", "18"))
    order = os.environ.get("STARJAR_LED_ORDER", "RGB")
    config_path = os.environ.get("STARJAR_CONFIG", "")
    if not config_path or not Path(config_path).is_file():
        return count, pin, order
    from starjar.config import load_config

    config = load_config(Path(config_path))
    return config.led_count, config.led_pin, config.led_order


def _wait_dir(path: Path) -> bool:
    for _ in range(50):
        if path.is_dir():
            return True
        time.sleep(0.1)
    return False


def _star_gid() -> int:
    import grp

    try:
        return grp.getgrnam("star").gr_gid
    except KeyError:
        return 0


def _add_user_site() -> None:
    import site

    lib = Path("/home/star/.local/lib")
    if not lib.is_dir():
        return
    for path in sorted(lib.glob("python*/site-packages")):
        site.addsitedir(str(path))


if __name__ == "__main__":
    raise SystemExit(main())
