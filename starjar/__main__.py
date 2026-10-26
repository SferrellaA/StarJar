"""Serve the challenge. Does not print attempt secrets."""

import os
import random
from pathlib import Path

from aiohttp import web

from starjar.config import load_config
from starjar.secrets import load_or_create
from starjar.web import AppState, make_app


def main() -> None:
    config_path = Path(os.environ.get("STARJAR_CONFIG", "config.toml"))
    if not config_path.is_file():
        config_path = Path("config.example.toml")
    config = load_config(config_path)
    attempt = load_or_create(config.attempt, random.SystemRandom())
    state = AppState(
        www=config.www,
        challenge_tree=config.challenge_tree,
        trivia=config.trivia,
        scoreboard=config.scoreboard,
        attempt=attempt,
    )
    web.run_app(make_app(state), host=config.host, port=config.port, access_log=None)


if __name__ == "__main__":
    main()
