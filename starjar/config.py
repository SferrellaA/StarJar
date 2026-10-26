"""config.toml holds paths and LED count. It does not hold attempt secrets."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from starjar.scoreboard import DEFAULT_SCOREBOARD


@dataclass(frozen=True)
class Config:
    led_count: int
    led_pin: int
    led_order: str
    attempt: Path
    trivia: Path
    scoreboard: Path
    challenge_tree: Path
    www: Path
    host: str
    port: int


def load_config(path: Path, base: Path | None = None) -> Config:
    data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    leds = data.get("leds") or {}
    paths = data.get("paths") or {}
    web = data.get("web") or {}
    root = base if base is not None else Path(path).parent

    def relative(key: str, default: str) -> Path:
        raw = Path(str(paths.get(key, default)))
        if raw.is_absolute():
            return raw
        return root / raw

    return Config(
        led_count=int(leds.get("count", 50)),
        led_pin=int(leds.get("pin", 18)),
        led_order=str(leds.get("order", "RGB")),
        attempt=Path(str(paths.get("attempt", "/run/starjar"))),
        trivia=Path(str(paths.get("trivia", "/var/lib/starjar/trivia.toml"))),
        scoreboard=Path(str(paths.get("scoreboard", DEFAULT_SCOREBOARD))),
        challenge_tree=relative("challenge_tree", "challenge_tree"),
        www=relative("www", "www"),
        host=str(web.get("host", "0.0.0.0")),
        port=int(web.get("port", 8080)),
    )
