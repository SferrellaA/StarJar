# StarJar

A jar in the unit heritage room. It looks like an art piece. A phone can solve it.

The plan and the constraints are `TODO.md`. Do not treat this file as a walkthrough.

## Laptop

Python 3.13, same as the Pi. uv manages this checkout. It cannot install its own CPython on the Pi (armv6).

```sh
uv sync
uv run pytest
```

## Pi

Raspbian 13, system Python 3.13. aiohttp is pinned to the trixie package, `python3-aiohttp` 3.11.16, so the board does not compile it. Do not `uv python install` there.

Figures, if any, go in `challenge_tree/images/`. An empty directory is fine. Do not generate stand-ins.

The live trivia file is `/var/lib/starjar/trivia.toml`, or the path in `config.toml`. It is not in git. `trivia.example.toml` is the schema and placeholders only.
