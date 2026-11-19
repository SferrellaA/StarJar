"""Laptop pytest helpers. Attempt state still has to live under /run."""

import os
from pathlib import Path


def writable_run_dir() -> Path:
    user_runtime = Path(f"/run/user/{os.getuid()}")
    if user_runtime.is_dir() and os.access(user_runtime, os.W_OK):
        return user_runtime
    # WSL has no logind runtime dir. /run/lock is sticky and writable.
    private = Path("/run/lock") / f"starjar-pytest-{os.getuid()}"
    private.mkdir(mode=0o700, exist_ok=True)
    os.chmod(private, 0o700)
    return private
