import json
import os
from pathlib import Path

import pytest

from starjar.scoreboard import DEFAULT_SCOREBOARD, load_public, save
from starjar.secrets import AttemptPathError, reset_attempt


def test_default_path_is_outside_run_and_the_jail():
    assert DEFAULT_SCOREBOARD == Path("/var/lib/starjar/scoreboard.json")
    assert Path("/run") not in DEFAULT_SCOREBOARD.parents
    assert "challenge_tree" not in DEFAULT_SCOREBOARD.parts


def test_atomic_write_backup_and_reset_does_not_delete_it(tmp_path: Path):
    board = tmp_path / "scoreboard.json"
    save(board, [{"initials": "AL", "time": 12, "sid": "NOPE"}])
    assert not (board.parent / (board.name + ".tmp")).exists()
    stored = json.loads(board.read_text(encoding="utf-8"))
    assert stored == [{"initials": "AL", "time": 12}]
    assert "sid" not in board.read_text(encoding="utf-8")
    backup = Path(str(board) + ".bak")
    assert backup.read_text(encoding="utf-8") == board.read_text(encoding="utf-8")
    assert load_public(board) == stored

    attempt = Path(f"/run/user/{os.getuid()}") / f"starjar-board-{os.getpid()}"
    attempt.mkdir(mode=0o700)
    (attempt / "sid").write_text("AB12CD34\n", encoding="ascii")
    reset_attempt(attempt)
    assert board.exists()
    assert backup.exists()
    with pytest.raises(AttemptPathError):
        reset_attempt(board)
