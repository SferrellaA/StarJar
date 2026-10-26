from starjar.mode import Profile, Snapshot, decide, names_to_delete
from starjar.wifi import add_open_ap_command, delete_command
import pytest


def _snap(**kwargs) -> Snapshot:
    defaults = dict(
        associated_name=None,
        activating_name=None,
        visible_ssids=frozenset(),
        profiles=(),
    )
    defaults.update(kwargs)
    return Snapshot(**defaults)


def test_associated_operator_is_diagnostic_even_with_a_leftover_attempt():
    snapshot = _snap(
        associated_name="Bench",
        visible_ssids=frozenset({"BenchWiFi"}),
        profiles=(
            Profile("Bench", "BenchWiFi", True),
            Profile("starjar-attempt-OLDSSID", "OLDSSID", False),
        ),
    )
    assert decide(snapshot) == "diagnostic"
    assert names_to_delete(snapshot.profiles) == ["starjar-attempt-OLDSSID"]


def test_still_associating_is_not_settled_by_a_timeout():
    snapshot = _snap(
        activating_name="Bench",
        visible_ssids=frozenset({"BenchWiFi"}),
        profiles=(Profile("Bench", "BenchWiFi", True),),
    )
    assert decide(snapshot) == "settling"
    assert decide(snapshot, timed_out=True) == "settling"


def test_no_configured_ssid_in_the_scan_is_challenge():
    snapshot = _snap(
        visible_ssids=frozenset({"Cafe"}),
        profiles=(Profile("Bench", "BenchWiFi", True),),
    )
    assert decide(snapshot) == "challenge"
    assert decide(snapshot, timed_out=True) == "challenge"


def test_attempt_profile_does_not_count_as_operator():
    snapshot = _snap(
        associated_name="starjar-attempt-AB12CD34",
        visible_ssids=frozenset({"AB12CD34"}),
        profiles=(Profile("starjar-attempt-AB12CD34", "AB12CD34", False),),
    )
    assert decide(snapshot) == "challenge"
    assert snapshot.profiles[0].autoconnect is False


def test_visible_operator_ssid_waits_until_timeout_if_not_associating():
    snapshot = _snap(
        visible_ssids=frozenset({"BenchWiFi"}),
        profiles=(Profile("Bench", "BenchWiFi", True),),
    )
    assert decide(snapshot) == "settling"
    assert decide(snapshot, timed_out=True) == "challenge"


def test_open_ap_command_has_no_password_and_does_not_touch_ethernet():
    command = add_open_ap_command("AB12CD34")
    assert command[command.index("ifname") + 1] == "wlan0"
    assert command[command.index("autoconnect") + 1] == "no"
    assert command[command.index("con-name") + 1] == "starjar-attempt-AB12CD34"
    joined = " ".join(command).lower()
    assert "psk" not in joined
    assert "password" not in joined
    assert "eth0" not in joined
    with pytest.raises(ValueError):
        add_open_ap_command("AB12CD34", iface="eth0")
    with pytest.raises(ValueError):
        delete_command("Bench")
    assert delete_command("starjar-attempt-AB12CD34")[:3] == [
        "nmcli",
        "connection",
        "delete",
    ]
