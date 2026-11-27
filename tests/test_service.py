from starjar.mode import Profile, Snapshot
from starjar.service import command_result, phase1_still, radio_wanted, scrub, wait_for_mode


def test_scrub_removes_attempt_secrets():
    assert scrub("wlan0 connect attempt failed", ("AB12CD34", "Q7K2")) == (
        "wlan0 connect attempt failed"
    )
    assert "AB12CD34" not in scrub("saw AB12CD34", ("AB12CD34", "Q7K2"))
    assert "Q7K2" not in scrub("code Q7K2", ("AB12CD34", "Q7K2"))


def test_only_phase1_brings_up_the_client():
    assert radio_wanted("phase1") is True
    assert radio_wanted("phase1-dry") is False
    assert radio_wanted("phase2") is False
    assert radio_wanted("idle") is False
    assert radio_wanted("victory") is False


def test_a_stage_change_cancels_an_in_flight_hunt():
    assert phase1_still("phase1", 3, 3) is True
    assert phase1_still("idle", 4, 3) is False
    assert phase1_still("phase1", 4, 3) is False
    assert phase1_still("phase2", 3, 3) is False


def test_status_has_no_secret_fields():
    stage, payload = command_result("status", "challenge", "phase1", False)
    assert stage == "phase1"
    assert payload == {
        "ok": True,
        "mode": "challenge",
        "stage": "phase1",
        "associated": False,
    }
    assert "sid" not in payload
    assert "code" not in payload
    stage, payload = command_result("phase2", "diagnostic", "idle", False)
    assert stage == "phase2"
    assert payload["stage"] == "phase2"
    assert radio_wanted(stage) is False


def test_visible_operator_ssid_is_not_settled_by_the_short_timeout():
    clock = {"now": 0.0}

    def collect():
        return Snapshot(
            associated_name=None,
            activating_name="Bench",
            visible_ssids=frozenset({"BenchWiFi"}),
            profiles=(Profile("Bench", "BenchWiFi", True),),
        )

    def sleep(_seconds: float) -> None:
        clock["now"] += 1

    def monotonic() -> float:
        return clock["now"]

    assert wait_for_mode(collect, sleep, monotonic, timeout=3, cap=2) == "diagnostic"
    assert clock["now"] >= 5


def test_absent_operator_ssid_is_challenge_without_waiting():
    def collect():
        return Snapshot(
            associated_name=None,
            activating_name=None,
            visible_ssids=frozenset({"Cafe"}),
            profiles=(Profile("Bench", "BenchWiFi", True),),
        )

    assert wait_for_mode(collect, lambda _s: None, lambda: 0.0) == "challenge"
