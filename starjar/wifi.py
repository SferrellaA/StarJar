"""nmcli command builders. Open network. Never ethernet. Never autoconnect an attempt."""

from starjar.mode import ATTEMPT_PREFIX, is_attempt
from starjar.secrets import TOKEN_ALPHABET


def delete_command(name: str) -> list[str]:
    if not is_attempt(name):
        raise ValueError("refusing to delete a non-attempt profile")
    return ["nmcli", "connection", "delete", name]


def add_open_ap_command(sid: str, iface: str = "wlan0") -> list[str]:
    if iface != "wlan0":
        raise ValueError("refusing to touch a non-wlan interface")
    if not sid or any(char not in TOKEN_ALPHABET for char in sid):
        raise ValueError("sid")
    return [
        "nmcli",
        "connection",
        "add",
        "type",
        "wifi",
        "ifname",
        iface,
        "con-name",
        f"{ATTEMPT_PREFIX}{sid}",
        "autoconnect",
        "no",
        "ssid",
        sid,
        "wifi.mode",
        "ap",
        "ipv4.method",
        "shared",
        "802-11-wireless-security.key-mgmt",
        "none",
    ]
