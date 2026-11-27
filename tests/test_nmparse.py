from starjar.nmparse import parse_devices, parse_ssids, split_terse, wlan_state


def test_split_terse_keeps_escaped_colons():
    assert split_terse(r"Cafe\:Guest:802-11-wireless:yes") == [
        "Cafe:Guest",
        "802-11-wireless",
        "yes",
    ]


def test_wlan_state_ignores_usb():
    devices = parse_devices(
        "usb0:ethernet:connected:starjar-usb\n"
        "wlan0:wifi:connecting (configuring):Bench\n"
    )
    assert wlan_state(devices) == (None, "Bench")
    connected = parse_devices("wlan0:wifi:connected:Bench\nusb0:ethernet:connected:starjar-usb\n")
    assert wlan_state(connected) == ("Bench", None)
    assert parse_ssids("\nCafe\n") == frozenset({"Cafe"})
