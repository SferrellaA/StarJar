# StarJar

A jar in the unit heritage room. It looks like an art piece. A phone can solve it.

The plan and the constraints are `TODO.md`. Do not treat this file as a walkthrough.

## Laptop

Python 3.13, same as the Pi. uv manages this checkout. It cannot install its own CPython on the Pi (armv6).

```sh
uv sync
make
```

`make` and `make help` explain the commands. `make test` runs the unit tests, and the jar tests too if the jar is plugged in. `make build` installs the jar and enables the boot service. `make demo` walks a challenge. `make shell` opens the USB shell. `make clean` removes build artifacts here, and on the jar if it is plugged in.


`scripts/serve-local.py` serves that same site on `127.0.0.1:8080` so a failing website test can be opened in a browser. It is a laptop fixture, not the jar.

`scripts/morse-visual.py` plays one letter at a time on the strip and prints the expected mark in this terminal. Space advances. Ctrl+C fails the check. It needs the USB shell.

## Pi

Wired shell, from WSL or a Linux machine: `scripts/starjar-shell`. On WSL it calls Windows `ssh.exe`, because WSL cannot see the USB NIC. On Linux it brings that NIC up and does not add a default route. User `star`, key `~/.ssh/starjar` (not in git). `scripts/starjar-ssh` is the same script, for a remote command. `scripts/starjar-usb-gadget.sh` is the Pi-side unit; it is already installed there.

Raspbian 13, system Python 3.13. aiohttp is the trixie package, `python3-aiohttp` 3.11.16, already installed. Do not `uv python install` there, and do not pip a newer aiohttp over it.

The board has no RTC. Until it has a route, NTP cannot run, and a reboot leaves the clock where it was. Apt will refuse repository signatures if the clock is behind. Set UTC before installing. There is no default route on the USB gadget. Do not share that adapter with Windows Internet Connection Sharing. That rewrites the address and drops the shell.

Joke figures are generators in `challenge_tree/images/`. Preview them with `scripts/render-figures.sh`. The visual spec is `scripts/figures.md`. An empty images directory is still fine.

The live trivia file is `/var/lib/starjar/trivia.toml`, or the path in `config.toml`. It is not in git. `trivia.example.toml` is the schema and placeholders only.
