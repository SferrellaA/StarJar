# StarJar TODO

Plan for the Pi port. Do not treat the old ESP32 / Plasma sketches as the design.
Last hardware note: the Pi already has `python3-bottle`, `python3-spidev`, and a
user-site `rpi-ws281x` 5.0.0. SPI was enabled in `/boot/firmware/config.txt` and
has not been rebooted in. The strip is not on SPI. Leave that config alone
unless it gets in the way.

## What this is

A jar in the unit heritage room. It looks like an art piece. It is a CTF that
a phone can solve, with a sniffer as an alternate path for phase one.
Stage 3 is configurable trivia, not questions baked into Python. The point is
still to make the player talk to whoever keeps the room. Do not put answers
in the repo or on the Pi.

Unplugging resets the attempt. The scoreboard does not reset.

## Hardware

- Raspberry Pi Zero W, hostname `jar`, SSH host `starjar` (`~/.ssh/config`), user `star`, key only.
- Strip is already wired: 5V, ground, and data on IO18 (GPIO 18, PWM). Not GPIO 10.
- Drive it with `rpi_ws281x` on PWM pin 18. Do not switch the design to SPI.
- Onboard analog audio uses that PWM channel. If pixels are garbage, try `dtparam=audio=off` before blaming the strip. Confirm on the bench.
- `rpi_ws281x` usually wants root or `CAP_SYS_RAWIO`. Do not run the web process as root to get that. Split a small LED helper, or grant the capability to the LED process only.
- LED count is still the old guess of 50. Make it config. Count the strip before calling the self-test done.
- External 5V is already how it is wired. Do not power the strip from the Pi's 5V pin.

## Boot mode

The trigger is association, not a named home network and not a jumper.

Operator-configured networks are NetworkManager profiles a person created from
a shell. Phase-one attempt profiles do not count. Name them `starjar-attempt-*`,
`autoconnect no`, never save them as a normal connection, and delete any
leftovers at the start of boot before the mode check.

Boot order:

1. Delete leftover `starjar-attempt-*` profiles.
2. Wait until NetworkManager has settled. Either it associated to an operator profile, or a scan shows none of those SSIDs. A short timeout is not "settled" if a configured SSID is visible and association is still in progress. Starting too early would drop a good link and enter challenge mode on the bench.
3. Associated to an operator profile: diagnostic mode.
4. Otherwise: challenge mode. No button. In the heritage room the saved bench SSID is simply not there, so this is the exhibit path.

Challenge mode may drop `wlan0`. Never touch ethernet. A USB ethernet dongle can keep SSH up during a hunt later. Not required.

## Diagnostic mode

SSH stays up. The web stage can bind on the LAN for testing. LEDs idle unless a jump says otherwise. Do not print attempt secrets to the journal or to the USB gadget serial.

Stage jump is a shell command, not a page on the LAN. A player who can see the jar must not get a stage select because diagnostic was left on.

- `jump idle` — art / status only.
- `jump phase1-dry` — Morse the phase-one phrase on the strip. Do not leave the operator network.
- `jump phase1` — real hunt. This disconnects `wlan0` and kills this SSH session unless ethernet is up. Say so before doing it.
- `jump phase2` — web stage up on the current network, Morse the phase-two code. Do not drop Wi-Fi.
- `jump victory` — trivia / scoreboard page, no radio change.
- `jump leds` — LED self-test.

## Challenge mode

Generate the attempt in `/run/starjar` (tmpfs) only. A crash may reread that directory. A power loss must not. Do not write the SID, the phase-two code, or the hidden path to the SD card.

Phase one is an open network. No password. One random SID, 8 characters, `[A-Z0-9]`, at least one digit (hotspot and SSID validators are picky, and 8 keeps a later password possible without another migration). Morse, in a loop, while probing:

`SID IS` — pause — `<the generated SID>`

The second part is the token, not the letters S-I-D again. The pause is a word gap or longer, so the two parts do not run together. Spell it `SID`, not `SSID`. That is the puzzle text. Do not "correct" it.

Standard Morse timing. No plaintext in logs. Probe requests are the sniffer path. An open network has no handshake and no PSK to crack. Seeing the SID is the whole phase-one secret.

Phone hotspot caveat, do not silently undo the open-network choice: stock iOS and many Android hotspots refuse an open AP and demand an 8-character WPA password. A spare router or a laptop AP can host an open SID. A phone may not. Recorded so the next session does not rediscover it mid-debug.

On association, start phase two immediately and switch Morse to the phase-two code. That code is short, Morse-safe, and not the SID. A debug route must not return it.

## Phase two

Not married to Bottle. It was a stand-in for Microdot on an ESP32 with 10 MB of storage. That limit is gone. Use a current library that is easy to run with the holes explicit.

Bias: one process that can serve static files and share the in-memory attempt with the LED loop. No debug mode. No extra server-side interpreter. Pin dependencies. Avoid a stack that is heavy on a 512 MB Zero W. Stdlib or aiohttp are both acceptable. Flask or FastAPI are not worth it here. Do not keep Bottle for compatibility.

The page stays Brython. Part of the challenge is "what am I looking at?" and then noticing it is just Python in the page. Self-host `brython.js` and `brython_stdlib.js`. Do not load them from a CDN. They were gitignored for the ESP32. Stop ignoring them, vendor a pinned release, and commit the files. Recovering the old blobs from git history is fine if the version is known. Otherwise pin a current release and record the version.

The joke page is the existing "stop doing X" copypasta. There is no generator to check in. The format reference is the text pattern, not an image macro:

- https://knowyourmeme.com/memes/stop-doing-math
- https://gist.github.com/wassname/b2fb9087f2d954261524f9e0d5d50ff8 (examples an LLM wrote, not a renderer)

New figures are the operator's job. The old ones were gitignored and are not in the working tree. The page must tolerate an empty images directory. Do not invent replacement memes and commit them.

Sloppy on purpose, jailed for real. Several ways through, none of them a shell:

- View source shows Brython and names a list endpoint.
- Directory listing of the challenge tree.
- A backup or editor-swap file in that tree that shows the routes, including the secret path.
- `robots.txt` overshares.
- A debug route that says the jar is spelling the code, and does not contain it.
- The secret path accepts only the code on the LEDs.

`realpath` the file reads. Reject `..`, absolute paths, and symlinks that leave the challenge tree. An open read would expose NetworkManager profiles and `/home/star/.ssh` to whoever is on the attempt network. Wrong guesses get a taunt, not a traceback.

No PHP. No player shell, command injection, webshell, or sudo. That idea belonged to a different CTF.

After the code is accepted, render stage 3 from a trivia file. Swapping the
set later is a file replace and a service restart, not a code change. No
answer key in that file. No graybeard PIN unless the operator later asks for
one, and then it stays out of git.

Schema, committed as `trivia.example.toml`: a title, a short prompt ("ask
someone who was there"), and an ordered list of questions. Placeholder text
only. The unit's real questions are not committed.

The service reads the live file from a path in `config.toml`, default
`/var/lib/starjar/trivia.toml`, outside the challenge tree. The sloppy reader
must not be able to reach it. Missing or unreadable file: show the prompt
without questions, and do not crash the attempt. Restart picks up a new file.
Unplug does not delete it.

## Scoreboard

Persistent across unplug. Initials and time. Atomic write (temp file, then rename) plus a backup, because the reset method is pulling the plug. Store it outside the challenge tree, for example `/var/lib/starjar/scoreboard.json`. A public route may return those fields. The sloppy file reader must not be how it is served, and must not be able to reach it.

Attempt secrets and the scoreboard are different state. Do not put them in the same file.

## Tests

Tests are pytest, no GPIO, and they run on the laptop. LED self-test stays manual, on the Pi, via `jump leds`.

## Later

Read-only root is still worth doing before the jar lives in the heritage room. It is an image change, not a puzzle change. Not this pass.

## Order of work

1. LED and Wi-Fi adapters, and `deploy/starjar.service` with `Restart=on-failure`. A restart rereads `/run/starjar` and does not roll a new attempt.
2. Diagnostic jumps on the bench, including a phase-two test that does not drop SSH.
3. A real phase-one hunt only after that is boring. It will disconnect the bench Wi-Fi.

## Out of scope

- PHP, shells, or any path onto the Pi.
- CDN Brython.
- Trivia answers, or a hardcoded question list.
- Persisting the SID or the phase-two code.
- Resetting the scoreboard on unplug.
- SPI as the data pin.
- Rewriting git history.
