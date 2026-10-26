"""Mode follows the radio. Attempt profiles are not operator networks."""

from dataclasses import dataclass

ATTEMPT_PREFIX = "starjar-attempt-"


@dataclass(frozen=True)
class Profile:
    name: str
    ssid: str | None
    autoconnect: bool


@dataclass(frozen=True)
class Snapshot:
    associated_name: str | None
    activating_name: str | None
    visible_ssids: frozenset[str]
    profiles: tuple[Profile, ...]


def is_attempt(name: str | None) -> bool:
    return bool(name) and name.startswith(ATTEMPT_PREFIX)


def operator_profiles(snapshot: Snapshot) -> tuple[Profile, ...]:
    return tuple(profile for profile in snapshot.profiles if not is_attempt(profile.name))


def names_to_delete(profiles: tuple[Profile, ...] | list[Profile]) -> list[str]:
    return [profile.name for profile in profiles if is_attempt(profile.name)]


def _operator_names(snapshot: Snapshot) -> set[str]:
    return {profile.name for profile in operator_profiles(snapshot)}


def operator_ssid_visible(snapshot: Snapshot) -> bool:
    return any(
        profile.ssid is not None and profile.ssid in snapshot.visible_ssids
        for profile in operator_profiles(snapshot)
    )


def associated_operator(snapshot: Snapshot) -> bool:
    name = snapshot.associated_name
    return bool(name) and not is_attempt(name) and name in _operator_names(snapshot)


def association_in_progress(snapshot: Snapshot) -> bool:
    name = snapshot.activating_name
    if not name or is_attempt(name) or name not in _operator_names(snapshot):
        return False
    return operator_ssid_visible(snapshot)


def decide(snapshot: Snapshot, timed_out: bool = False) -> str:
    """diagnostic, challenge, or settling.

    A timeout is not settled while association to an operator profile is still
    in progress. Attempt profiles never count as operator networks.
    """

    if associated_operator(snapshot):
        return "diagnostic"
    if not operator_ssid_visible(snapshot):
        return "challenge"
    if association_in_progress(snapshot) or not timed_out:
        return "settling"
    return "challenge"
