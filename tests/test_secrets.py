import os
import random
from pathlib import Path

import pytest

from starjar.secrets import (
    CODE_LENGTH,
    SID_LENGTH,
    TOKEN_ALPHABET,
    Attempt,
    AttemptPathError,
    IncompleteAttempt,
    load_or_create,
    new_code,
    new_sid,
    reset_attempt,
)


def test_token_rules_and_no_password_field():
    rng = random.Random(1)
    for _ in range(30):
        sid = new_sid(rng)
        code = new_code(rng, sid)
        assert len(sid) == SID_LENGTH
        assert len(code) == CODE_LENGTH
        assert all(char in TOKEN_ALPHABET for char in sid + code)
        assert any(char.isdigit() for char in sid)
        assert any(char.isdigit() for char in code)
        assert code != sid
    attempt = Attempt(sid="AB12CD34", code="Q7K2")
    assert not hasattr(attempt, "password")
    assert "password" not in attempt.__dataclass_fields__


def test_attempt_state_refused_outside_run(tmp_path: Path):
    with pytest.raises(AttemptPathError):
        load_or_create(tmp_path / "starjar", random.Random(0))
    with pytest.raises(AttemptPathError):
        load_or_create(Path("/tmp/starjar-not-run"), random.Random(0))


def test_restart_rereads_and_reset_removes_only_the_attempt(tmp_path: Path):
    directory = Path(f"/run/user/{os.getuid()}") / f"starjar-pytest-{os.getpid()}"
    reset_attempt(directory)
    rng = random.Random(2)
    first = load_or_create(directory, rng)
    second = load_or_create(directory, random.Random(99))
    assert second == first
    names = {path.name for path in directory.iterdir()}
    assert names == {"sid", "code"}
    assert "password" not in names
    assert (directory / "sid").read_text(encoding="ascii").strip() == first.sid
    scoreboard = tmp_path / "scoreboard.json"
    scoreboard.write_text('[{"initials":"AL","time":3}]\n', encoding="utf-8")
    reset_attempt(directory)
    assert not directory.exists()
    assert scoreboard.read_text(encoding="utf-8").startswith("[")
    with pytest.raises(AttemptPathError):
        reset_attempt(scoreboard)


def test_partial_attempt_is_not_replaced(tmp_path: Path):
    directory = Path(f"/run/user/{os.getuid()}") / f"starjar-partial-{os.getpid()}"
    directory.mkdir(mode=0o700, exist_ok=True)
    (directory / "sid").write_text("AB12CD34\n", encoding="ascii")
    try:
        with pytest.raises(IncompleteAttempt):
            load_or_create(directory, random.Random(0))
        assert not (directory / "code").exists()
    finally:
        reset_attempt(directory)
