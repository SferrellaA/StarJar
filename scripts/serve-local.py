#!/usr/bin/env python3
"""Serve the challenge site on 127.0.0.1 so the website tests are easier to debug.

Does not talk to the Pi. Attempt files stay under /run, same rule as the tests.
Usage: uv run scripts/serve-local.py [port]
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from starjar.bench import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
