"""Boot decision and attempt reload. A restart must not roll a new attempt."""

from pathlib import Path
from random import Random

from starjar.mode import Profile, Snapshot, decide, names_to_delete
from starjar.secrets import Attempt, load_or_create


def profiles_to_delete(profiles: tuple[Profile, ...] | list[Profile]) -> list[str]:
    return names_to_delete(profiles)


def boot_mode(snapshot: Snapshot, timed_out: bool = False) -> str:
    return decide(snapshot, timed_out=timed_out)


def prepare_attempt(directory: Path, rng: Random) -> Attempt:
    return load_or_create(directory, rng)
