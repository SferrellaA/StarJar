"""Attempt secrets. /run only. Unplug is the reset. No password."""

from __future__ import annotations

import os
import shutil
import string
from dataclasses import dataclass
from pathlib import Path
from random import Random

TOKEN_ALPHABET = string.ascii_uppercase + string.digits
SID_LENGTH = 8
CODE_LENGTH = 4


class AttemptPathError(ValueError):
    pass


class IncompleteAttempt(RuntimeError):
    pass


@dataclass(frozen=True)
class Attempt:
    sid: str
    code: str


def assert_attempt_dir(path: Path) -> Path:
    resolved = Path(path).resolve()
    run = Path("/run")
    if resolved == run or run not in resolved.parents:
        raise AttemptPathError(str(resolved))
    return resolved


def new_sid(rng: Random) -> str:
    while True:
        sid = "".join(rng.choice(TOKEN_ALPHABET) for _ in range(SID_LENGTH))
        if any(char.isdigit() for char in sid):
            return sid


def new_code(rng: Random, sid: str) -> str:
    while True:
        code = "".join(rng.choice(TOKEN_ALPHABET) for _ in range(CODE_LENGTH))
        if any(char.isdigit() for char in code) and code != sid:
            return code


def load_or_create(directory: Path, rng: Random) -> Attempt:
    directory = assert_attempt_dir(directory)
    sid_path = directory / "sid"
    code_path = directory / "code"
    if sid_path.exists() or code_path.exists():
        return _read(directory)
    directory.mkdir(parents=True, mode=0o700, exist_ok=True)
    os.chmod(directory, 0o700)
    attempt = Attempt(new_sid(rng), "")
    attempt = Attempt(attempt.sid, new_code(rng, attempt.sid))
    _write_new(sid_path, attempt.sid)
    _write_new(code_path, attempt.code)
    return attempt


def reset_attempt(directory: Path) -> None:
    directory = assert_attempt_dir(directory)
    if not directory.exists():
        return
    for child in list(directory.iterdir()):
        if child.is_symlink() or not child.is_dir():
            child.unlink()
        else:
            shutil.rmtree(child)
    directory.rmdir()


def _write_new(path: Path, value: str) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(fd, (value + "\n").encode("ascii"))
    finally:
        os.close(fd)


def _read(directory: Path) -> Attempt:
    sid_path = directory / "sid"
    code_path = directory / "code"
    if not sid_path.is_file() or not code_path.is_file():
        raise IncompleteAttempt(directory.name)
    try:
        sid = sid_path.read_text(encoding="ascii").strip()
        code = code_path.read_text(encoding="ascii").strip()
    except (OSError, UnicodeError) as exc:
        raise IncompleteAttempt(directory.name) from exc
    if not _valid(sid, SID_LENGTH) or not _valid(code, CODE_LENGTH) or code == sid:
        raise IncompleteAttempt(directory.name)
    return Attempt(sid, code)


def _valid(value: str, length: int) -> bool:
    return (
        len(value) == length
        and all(char in TOKEN_ALPHABET for char in value)
        and any(char.isdigit() for char in value)
    )
