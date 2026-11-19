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
    # Main first. A crash before the backup write keeps the new file.
    # A torn main falls back to the previous backup.
    _atomic_write(path, payload)
    _atomic_write(_backup(path), payload)


def load_public(path: Path) -> list[dict]:
    last_error: Exception | None = None
    for candidate in (path, _backup(path)):
        if not candidate.is_file():
            continue
        try:
            data = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            last_error = exc
            continue
        if not isinstance(data, list):
            return []
        return [_public(entry) for entry in data if isinstance(entry, dict)]
    if last_error is not None:
        raise last_error
    return []


def _backup(path: Path) -> Path:
    return path.with_name(path.name + ".bak")


def _atomic_write(path: Path, payload: str) -> None:
    temporary = path.with_name(path.name + ".tmp")
    data = payload.encode("utf-8")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    try:
        view = memoryview(data)
        while view:
            written = os.write(fd, view)
            view = view[written:]
        os.fsync(fd)
    finally:
        os.close(fd)
    os.chmod(temporary, 0o644)
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def _public(entry: dict) -> dict:
    return {"initials": str(entry.get("initials", "")), "time": entry.get("time")}
