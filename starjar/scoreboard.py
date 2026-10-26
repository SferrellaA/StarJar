"""Persistent scoreboard. Not attempt state, and not inside the jail."""

from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_SCOREBOARD = Path("/var/lib/starjar/scoreboard.json")


def save(path: Path, entries: list[dict]) -> None:
    public = [_public(entry) for entry in entries]
    payload = json.dumps(public, indent=2) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(payload, encoding="utf-8")
    os.chmod(temporary, 0o644)
    os.replace(temporary, path)
    path.with_name(path.name + ".bak").write_text(payload, encoding="utf-8")


def load_public(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        return []
    return [_public(entry) for entry in data if isinstance(entry, dict)]


def _public(entry: dict) -> dict:
    return {"initials": str(entry.get("initials", "")), "time": entry.get("time")}
