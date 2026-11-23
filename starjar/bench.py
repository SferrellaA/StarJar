"""Laptop copy of the site, for debugging the tests. Not the jar."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from random import Random

from aiohttp import web

from starjar.secrets import Attempt, load_or_create
from starjar.web import SHOW_ERRORS, AppState, make_app

# Obvious fixture. Not an attempt secret, and not written on the Pi.
LOCAL_SID = "LOCAL1A2"
LOCAL_CODE = "L0C1"


def prepare_local(root: Path, attempt_dir: Path, scoreboard: Path) -> AppState:
    root = Path(root)
    _write_fixture(attempt_dir)
    attempt = load_or_create(attempt_dir, Random(0))
    if attempt != Attempt(LOCAL_SID, LOCAL_CODE):
        raise RuntimeError("local fixture was not reread")
    return AppState(
        www=root / "www",
        challenge_tree=root / "challenge_tree",
        trivia=root / "trivia.example.toml",
        scoreboard=scoreboard,
        attempt=attempt,
    )


def serve_local(state: AppState, host: str = "127.0.0.1", port: int = 8080) -> None:
    app = make_app(state)
    app[SHOW_ERRORS] = True
    print(f"local site http://{host}:{port}", flush=True)
    print(f"fixture code {state.attempt.code} (not the jar)", flush=True)
    print("ctrl-c stops", flush=True)
    web.run_app(app, host=host, port=port)


def _write_fixture(directory: Path) -> None:
    directory.mkdir(parents=True, mode=0o700, exist_ok=True)
    os.chmod(directory, 0o700)
    for name, value in (("sid", LOCAL_SID), ("code", LOCAL_CODE)):
        path = directory / name
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            os.write(fd, (value + "\n").encode("ascii"))
        finally:
            os.close(fd)
        os.chmod(path, 0o600)
    # load_or_create checks the shape. Fail here if the fixture drifted.
    loaded = Attempt(LOCAL_SID, LOCAL_CODE)
    if loaded.sid == loaded.code:
        raise RuntimeError("fixture sid and code must differ")


def main(argv: list[str] | None = None) -> int:
    from tests.conftest import writable_run_dir

    root = Path(__file__).resolve().parents[1]
    args = list(sys.argv[1:] if argv is None else argv)
    port = 8080
    if args:
        port = int(args[0])
    attempt = writable_run_dir() / "starjar-local"
    scoreboard = writable_run_dir() / "starjar-local-scoreboard.json"
    serve_local(prepare_local(root, attempt, scoreboard), port=port)
    return 0
