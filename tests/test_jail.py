from pathlib import Path

import pytest

from starjar.jail import JailError, resolve_inside


def test_rejects_dotdot_absolute_and_outside_symlink(tmp_path: Path):
    root = tmp_path / "challenge_tree"
    root.mkdir()
    (root / "note.txt").write_text("inside", encoding="utf-8")
    outside = tmp_path / "secret.toml"
    outside.write_text("prompt = \"no\"\n", encoding="utf-8")
    (root / "leak").symlink_to(outside)
    nested = root / "images"
    nested.mkdir()
    (nested / "up").symlink_to(outside)

    with pytest.raises(JailError):
        resolve_inside(root, "../secret.toml")
    with pytest.raises(JailError):
        resolve_inside(root, "images/../../secret.toml")
    with pytest.raises(JailError):
        resolve_inside(root, str(outside))
    with pytest.raises(JailError):
        resolve_inside(root, "/etc/passwd")
    with pytest.raises(JailError):
        resolve_inside(root, "leak")
    with pytest.raises(JailError):
        resolve_inside(root, "images/up")

    assert resolve_inside(root, "note.txt").read_text(encoding="utf-8") == "inside"
    inside_link = root / "alias.txt"
    inside_link.symlink_to(root / "note.txt")
    assert resolve_inside(root, "alias.txt").read_text(encoding="utf-8") == "inside"


def test_missing_file_is_not_an_escape(tmp_path: Path):
    root = tmp_path / "challenge_tree"
    (root / "images").mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        resolve_inside(root, "images/nope.png")
