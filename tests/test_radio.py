import pytest

from starjar.mode import ATTEMPT_PREFIX
from starjar.radio import (
    RadioError,
    add_open_client_command,
    assert_safe,
    collect_snapshot,
    modify_open_client_command,
    up_command,
)
from starjar.wifi import add_open_ap_command


def test_client_command_joins_an_open_network_and_does_not_host_one():
    command = add_open_client_command("AB12CD34")
    assert command[command.index("ifname") + 1] == "wlan0"
    assert command[command.index("autoconnect") + 1] == "no"
    assert command[command.index("wifi.mode") + 1] == "infrastructure"
    assert command[command.index("con-name") + 1] == f"{ATTEMPT_PREFIX}AB12CD34"
    assert "ap" not in command
    assert "key-mgmt" not in command
    joined = " ".join(command).lower()
    assert "psk" not in joined
    assert "password" not in joined
    assert "usb0" not in joined
    assert "eth0" not in joined
    with pytest.raises(ValueError):
        add_open_client_command("AB12CD34", iface="eth0")
    with pytest.raises(ValueError):
        add_open_client_command("AB12CD34", iface="usb0")


def test_modify_and_up_refuse_operator_profiles_and_ethernet():
    name = f"{ATTEMPT_PREFIX}AB12CD34"
    modify = modify_open_client_command(name)
    assert modify[modify.index("connection.interface-name") + 1] == "wlan0"
    assert modify[modify.index("connection.autoconnect") + 1] == "no"
    assert up_command(name)[up_command(name).index("ifname") + 1] == "wlan0"
    with pytest.raises(ValueError):
        modify_open_client_command("Bench")
    with pytest.raises(ValueError):
        up_command("Bench")
    with pytest.raises(ValueError):
        up_command(name, iface="usb0")
    with pytest.raises(ValueError):
        assert_safe(["nmcli", "connection", "delete", "starjar-usb"])
    with pytest.raises(ValueError):
        assert_safe(["nmcli", "connection", "up", "Bench", "ifname", "wlan0"])
    with pytest.raises(ValueError):
        assert_safe(["ip", "link", "set", "usb0", "down"])
    assert_safe(["nmcli", "connection", "show"])
    assert_safe(add_open_client_command("AB12CD34"))


def test_helper_snapshot_hides_the_attempt():
    from starjar.radio import parse_helper_snapshot

    snapshot = parse_helper_snapshot(
        "associated\tattempt\n"
        "activating\tnone\n"
        "visible\tCafe\n"
        "profile\tBench\tBenchWiFi\tyes\n"
    )
    assert snapshot.associated_name == "starjar-attempt-"
    assert "AB12CD34" not in snapshot.visible_ssids
    assert snapshot.profiles[0].name == "Bench"


def test_the_service_does_not_host_an_ap(monkeypatch):
    import starjar.service as service

    assert "add_open_ap_command" not in service.__dict__
    # The hosted-AP helper remains for the old command shape. The boot path does not call it.
    assert "wifi.mode" in add_open_ap_command("AB12CD34")


def test_collect_reads_wifi_profiles_and_skips_ethernet():
    calls: list[list[str]] = []

    def run(argv: list[str]) -> str:
        calls.append(argv)
        if argv[1:3] == ["device", "wifi"] and "rescan" in argv:
            raise RadioError("nmcli failed")
        if argv[1:4] == ["-t", "-f", "NAME,TYPE,AUTOCONNECT"]:
            return "starjar-usb:802-3-ethernet:yes\nBench:802-11-wireless:yes\n"
        if argv[1:4] == ["-t", "-f", "DEVICE,TYPE,STATE,CONNECTION"]:
            return "usb0:ethernet:connected:starjar-usb\nwlan0:wifi:disconnected:\n"
        if argv[1:4] == ["-t", "-f", "SSID"]:
            return "Cafe\n"
        if argv[1:3] == ["-g", "802-11-wireless.ssid"]:
            return "BenchWiFi\n"
        raise AssertionError(argv)

    snapshot = collect_snapshot(run, rescan=True)
    assert snapshot.associated_name is None
    assert snapshot.visible_ssids == frozenset({"Cafe"})
    assert [profile.name for profile in snapshot.profiles] == ["Bench"]
    assert snapshot.profiles[0].ssid == "BenchWiFi"
    assert calls[0][calls[0].index("ifname") + 1] == "wlan0"
