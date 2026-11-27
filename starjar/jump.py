"""Diagnostic stage jump. A shell command, not a page."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from starjar.ipc import COMMANDS, PHASE1_WARNING, request


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1 or args[0] not in COMMANDS:
        names = " ".join(COMMANDS)
        print(f"usage: jump {names}", file=sys.stderr)
        return 2
    cmd = args[0]
    if cmd == "phase1":
        print(PHASE1_WARNING, file=sys.stderr)
        hold = Path("/run/starjar/hold")
        if hold.is_file():
            hold.unlink()
    try:
        payload = request(cmd)
    except OSError:
        print("starjar is not running", file=sys.stderr)
        return 1
    if not payload.get("ok"):
        print("jump refused", file=sys.stderr)
        return 1
    # Status is stage and association, not the SID or the code.
    if cmd == "status":
        print(json.dumps(payload), flush=True)
    else:
        print(payload.get("stage", ""), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
