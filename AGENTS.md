# StarJar

Heritage-room CTF on a Raspberry Pi Zero W. Art piece in front, puzzle behind it.
The plan is `TODO.md`. Read it before editing. Do not implement it unless this
session was asked to. Do not revive the ESP32 / Plasma design from the sketches.

## Facts that are easy to "fix" and must not be fixed

- Phase one is an open network. No password. Morse is `SID IS`, a pause, then the generated SID. Spell `SID`, not `SSID`. The second part is the token, not the word SID again.
- Mode follows the radio. Associated to a NetworkManager profile a person created from a shell: diagnostic. Not associated, and no such SSID in the scan: challenge. There is no home-SSID constant and no jumper.
- Profiles named `starjar-attempt-*` are the phase-one hunt. They do not count as operator networks. Never set them autoconnect. Delete leftovers before the mode check.
- Attempt secrets live in `/run/starjar` only. Unplug is the reset. The scoreboard is the exception: it persists on disk, outside the web jail, and must survive unplug.
- Stage 3 trivia is a config file, not strings in Python. Commit `trivia.example.toml` with the schema and placeholders only. The live set is `/var/lib/starjar/trivia.toml` (or the path in `config.toml`), outside the web jail, and gitignored. Swapping it is a file replace, not a code change. Answers are not in the repo and must not be added. The player is supposed to ask whoever keeps the room.
- Brython stays. Self-host the JS. Do not load it from a CDN. Do not gitignore it again.
- The strip data pin is GPIO 18 (PWM), already wired, with 5V and ground. Do not migrate it to SPI. `rpi_ws281x` is the driver. SPI was enabled earlier by mistake. It is not the data path.
- No PHP, no player shell, no command injection, no webshell. File reads stay inside the challenge tree after a realpath check. A sloppy server is the puzzle. A path onto the Pi is a different project.
- `test13.py` has a dead router password. Cut it when retiring the old sketches. Do not restore it. Do not rewrite history for it unless asked.
- Figures are missing on purpose. The operator will supply new ones. Do not generate stand-in memes and commit them. An empty images directory must not crash the page.
- The Pi is armv6 (Raspbian 13) with system Python 3.13. uv cannot install its own CPython there. Stay on 3.13. aiohttp stays pinned to the trixie package (3.11.16) so the Pi does not need a source build.

## TODO

When an item in `TODO.md` is done, delete it. Do not mark it complete, check it off, or leave it as a record of finished work.

## Git

The user controls git. Do not commit, stage, push, tag, rebase, reset, or otherwise change git state unless this session was asked to.

## Bench

- SSH host `starjar`, user `star`, key auth. Password auth is off. `sudo -n` works.
- The Pi is on the bench Wi-Fi. A phase-one hunt disconnects that link and drops SSH unless ethernet is up.
- Diagnostic stage jumps are shell commands, not a LAN page. See `TODO.md`. `jump phase1-dry` and `jump phase2` must be possible without leaving the operator network. `jump phase1` will kill the SSH session. Warn before running it.
- Do not reboot the Pi unless asked. Do not install PHP or a second web server.
- Do not print the SID or the phase-two code to the journal or to the USB gadget serial. `serial-getty` on `ttyGS0` is up.

## Libraries

The 10 MB ESP32 limit is gone. Bottle, MicroPython `network`, and Pimoroni Plasma were storage compromises. Replace them. Prefer one pinned async stack that can serve the vendored Brython files and share in-memory attempt state with the LEDs. Stdlib or aiohttp. Not Flask, FastAPI, or Microdot.

`rpi_ws281x` needs root or `CAP_SYS_RAWIO`. Do not solve that by running the web process as root.

## Tests

Old files under `tests/` are hardware sketches. New tests are pytest, no GPIO, and run on the laptop. LED checks are manual, on the Pi, in diagnostic mode.

## Repo

Project skills, if any are written later, go in this repo's `.pi/skills/`. Do not install them into `~/.pi/agent/skills/`.
