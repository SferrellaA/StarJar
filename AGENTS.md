# StarJar

Heritage-room CTF on a Raspberry Pi Zero W. Art piece in front, puzzle behind it.
The plan is `TODO.md`. Read it before editing. Do not implement it unless this
session was asked to. Do not revive the ESP32 / Plasma design from the sketches.

## Facts that are easy to "fix" and must not be fixed

- Phase one is an open network. No password. Morse is `SID IS`, a pause, then the generated SID. Spell `SID`, not `SSID`. The second part is the token, not the word SID again.
- Mode follows the radio. Associated to a NetworkManager profile a person created from a shell: diagnostic. Not associated, and no such SSID in the scan: challenge. There is no home-SSID constant and no jumper.
- Profiles named `starjar-attempt-*` are the phase-one hunt. They do not count as operator networks. Never set them autoconnect. Delete leftovers before the mode check.
- Attempt secrets live in `/run/starjar` only. Unplug is the reset. The scoreboard is the exception: it persists on disk, outside the web jail, and must survive unplug. The backup is there because the plug can tear the main file. Read it if the main file is missing or corrupt. Fsync before rename. Do not "simplify" that away.
- Stage 3 trivia is a config file, not strings in Python. Commit `trivia.example.toml` with the schema and placeholders only. The live set is `/var/lib/starjar/trivia.toml` (or the path in `config.toml`), outside the web jail, and gitignored. Swapping it is a file replace, not a code change. Answers are not in the repo and must not be added. The player is supposed to ask whoever keeps the room.
- Brython stays. Self-host the JS. Do not load it from a CDN. Do not gitignore it again.
- The strip data pin is GPIO 18 (PWM), already wired, with 5V and ground. Do not migrate it to SPI. `rpi_ws281x` is the driver. SPI was enabled earlier by mistake. It is not the data path.
- No PHP, no player shell, no command injection, no webshell. File reads stay inside the challenge tree after a realpath check. A sloppy server is the puzzle. A path onto the Pi is a different project.
- `test13.py` has a dead router password. Cut it when retiring the old sketches. Do not restore it. Do not rewrite history for it unless asked.
- Figures are Brython generators in `challenge_tree/images/*.py`. The page fetches them through `/get/images` and draws the SVG they return. They are a red herring, not a secret. An empty images directory must not crash the page. Do not replace them with raster stand-ins. `scripts/figures.md` is what each picture is supposed to look like. `scripts/render-figures.sh` renders a gallery for that check.
- The Pi is armv6 (Raspbian 13) with system Python 3.13. uv cannot install its own CPython there. Stay on 3.13. aiohttp stays pinned to the trixie package (3.11.16) so the Pi does not need a source build. That package is already installed. Do not pip or uv install aiohttp on the board, and do not remove it to "match" a venv.

## TODO

When an item in `TODO.md` is done, delete it. Do not mark it complete, check it off, or leave it as a record of finished work.

## Git

The user controls git. Do not commit, stage, push, tag, rebase, reset, or otherwise change git state unless this session was asked to.

## Bench

- SSH host `starjar`, user `star`, key auth. Password auth is off. `sudo -n` works. Wired shell from WSL or a Linux host is `scripts/starjar-shell`. `scripts/starjar-ssh` is the same script with a remote command. That is the shell. Do not add another one. WSL cannot see the USB NIC, so the script uses Windows `ssh.exe` and the Windows key `%USERPROFILE%\.ssh\starjar`, not the WSL home. On Linux it configures the gadget NIC and must not add a default route. Key is `~/.ssh/starjar`, not in git. Pi addresses are `10.55.0.1` and `169.254.55.1`.
- On this Windows host the gadget is the UsbNcm adapter (last seen as "Ethernet 3"). It often has only a link-local address. The name and that address can change. Do not hardcode them. Ping from the Pi to the Windows address can fail while SSH from Windows to the Pi still works. Windows firewall drops inbound, including ICMP. Do not treat that as a dead cable.
- Do not give the Pi a route with Windows Internet Connection Sharing. ICS rewrites the shared adapter, usually to `192.168.137.1`, and drops this SSH session. `New-NetNat` needs an elevated Windows shell. This session was not admin. Do not add a default route on the WSL side via the gadget.
- Apt sources are HTTP, not HTTPS. With no upstream route, run a localhost HTTP proxy on Windows and `ssh -R 127.0.0.1:8888:127.0.0.1:8888` to the Pi, then `Acquire::http::Proxy=http://127.0.0.1:8888`. A one-connection proxy needs `Acquire::Queue-Mode=access`. Stop both when the install is done. Do not leave the proxy listening.
- No RTC. NTP is enabled and cannot sync without a route. A reboot loses the clock. Apt then rejects signatures as "Not live until ...". Set UTC with `sudo -n date -u -s` from the host before apt. Do not disable signature checks to get past that.
- Do not assume the bench SSID is visible. A saved operator profile may exist while `wlan0` is disconnected and that SSID is absent from the scan. USB is the reliable shell. Do not join a neighbor network that happens to be visible. Do not delete operator profiles. Do not dump NetworkManager secrets. A phase-one hunt still disconnects Wi-Fi and drops SSH unless ethernet is up.
- Diagnostic stage jumps are shell commands, not a LAN page. See `TODO.md`. `jump phase1-dry` and `jump phase2` must be possible without leaving the operator network. `jump phase1` will kill the SSH session. Warn before running it.
- Do not reboot the Pi unless asked. Do not install PHP or a second web server.
- Do not print the SID or the phase-two code to the journal or to the USB gadget serial. `serial-getty` on `ttyGS0` is up.

## Libraries

The 10 MB ESP32 limit is gone. Bottle, MicroPython `network`, and Pimoroni Plasma were storage compromises. Replace them. Prefer one pinned async stack that can serve the vendored Brython files and share in-memory attempt state with the LEDs. Stdlib or aiohttp. Not Flask, FastAPI, or Microdot.

`rpi_ws281x` needs root or `CAP_SYS_RAWIO`. Do not solve that by running the web process as root.

## Tests

Old files under `tests/` are hardware sketches. New tests are pytest, no GPIO, and run on the laptop. LED checks are manual, on the Pi, in diagnostic mode.

This laptop is WSL and has no `/run/user/$UID`. Attempt tests still have to live under `/run`. `writable_run_dir()` in `tests/conftest.py` is that directory. Do not point them at `/tmp` or the WSL runtime dir.

## Repo

Project skills, if any are written later, go in this repo's `.pi/skills/`. Do not install them into `~/.pi/agent/skills/`.
