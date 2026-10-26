"""File reads stay inside the challenge tree after a realpath check."""

from pathlib import Path, PurePosixPath


class JailError(Exception):
    pass


def resolve_inside(root: Path, requested: str) -> Path:
    if not isinstance(requested, str) or requested == "" or "\x00" in requested:
        raise JailError("empty")
    normalized = requested.replace("\\", "/")
    if normalized.startswith("/") or normalized.startswith("~"):
        raise JailError("absolute")
    pure = PurePosixPath(normalized)
    if pure.is_absolute():
        raise JailError("absolute")
    parts = pure.parts
    if not parts or any(part in ("..", ".", "") for part in parts):
        raise JailError("dotdot")

    root_real = root.resolve()
    current = root_real
    for part in parts:
        nxt = current / part
        try:
            if nxt.is_symlink() or nxt.exists():
                target = nxt.resolve()
            else:
                if not _inside(root_real, current):
                    raise JailError("escape")
                raise FileNotFoundError(part)
        except JailError:
            raise
        except FileNotFoundError:
            raise
        except OSError as exc:
            raise JailError("unreadable") from exc
        if not _inside(root_real, target):
            raise JailError("symlink" if nxt.is_symlink() else "escape")
        current = target
    if not current.exists():
        raise FileNotFoundError(requested)
    if not _inside(root_real, current):
        raise JailError("escape")
    return current


def _inside(root: Path, path: Path) -> bool:
    return path == root or root in path.parents
