"""Checks against a jar that is plugged in over USB. Not the unit tests."""

from __future__ import annotations

import json
import subprocess
import time

import pytest

SSH = ["scripts/starjar-ssh"]


def remote(command: str, timeout: int = 40) -> str:
    result = subprocess.run(
        [*SSH, command],
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or f"remote command failed ({result.returncode})"
        raise AssertionError(detail)
    return result.stdout


def test_service_is_enabled_and_not_a_cron_job():
    unit = remote("systemctl cat starjar.service")
    assert "Restart=on-failure" in unit
    assert "WantedBy=multi-user.target" in unit
    assert remote("systemctl is-enabled starjar.service").strip() == "enabled"
    assert remote("systemctl is-enabled starjar-leds.service").strip() == "enabled"
    assert remote("systemctl is-active starjar.service").strip() == "active"
    assert remote("systemctl is-active starjar-leds.service").strip() == "active"
    cron = remote(
        "sh -c 'crontab -u star -l 2>/dev/null || true; "
        "ls /etc/cron.d 2>/dev/null || true'"
    )
    assert "starjar" not in cron


def test_restart_keeps_the_attempt_and_the_journal_is_clean():
    before = remote("cat /run/starjar/sid /run/starjar/code")
    sid, code = before.split()
    stamp = remote("date '+%Y-%m-%d %H:%M:%S'").strip()
    remote("sudo -n systemctl restart starjar.service", timeout=40)
    deadline = time.time() + 30
    after = ""
    while time.time() < deadline:
        if remote("systemctl is-active starjar.service").strip() != "active":
            time.sleep(0.4)
            continue
        try:
            after = remote("cat /run/starjar/sid /run/starjar/code")
        except AssertionError:
            time.sleep(0.4)
            continue
        break
    assert after == before
    status = {}
    deadline = time.time() + 15
    while time.time() < deadline:
        result = subprocess.run(
            [*SSH, "/usr/local/bin/jump status"],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            status = json.loads(result.stdout)
            break
        time.sleep(0.4)
    assert status.get("stage") == "idle"
    journal = remote(
        "journalctl -u starjar.service -u starjar-leds.service "
        f"--since '{stamp}' --no-pager -o cat"
    )
    if sid in journal or code in journal:
        raise AssertionError("journal contains an attempt secret")
    mode = remote("stat -c %a /run/starjar").strip()
    assert mode == "750" or mode == "700"


def test_usb_stays_up_and_attempt_profiles_are_clients():
    devices = remote("nmcli -t -f DEVICE,STATE,CONNECTION device status")
    assert any(line.startswith("usb0:") and "starjar-usb" in line for line in devices.splitlines())
    report = remote(
        "python3 - <<'PY'\n"
        "import subprocess\n"
        "out = subprocess.check_output(['nmcli','-t','-f','NAME,TYPE','connection','show'], text=True)\n"
        "found = False\n"
        "for line in out.splitlines():\n"
        "    name, kind = line.split(':', 1)\n"
        "    if not name.startswith('starjar-attempt-') or kind != '802-11-wireless':\n"
        "        continue\n"
        "    found = True\n"
        "    mode = subprocess.check_output(['nmcli','-g','802-11-wireless.mode','connection','show',name], text=True).strip()\n"
        "    auto = subprocess.check_output(['nmcli','-g','connection.autoconnect','connection','show',name], text=True).strip()\n"
        "    iface = subprocess.check_output(['nmcli','-g','connection.interface-name','connection','show',name], text=True).strip()\n"
        "    print(mode)\n"
        "    print(auto)\n"
        "    print(iface)\n"
        "if not found:\n"
        "    print('none')\n"
        "PY"
    )
    if report.strip() == "none":
        return
    mode, auto, iface = report.split()
    assert mode == "infrastructure"
    assert auto == "no"
    assert iface == "wlan0"


def test_debug_page_and_jump_status_hide_the_attempt():
    secrets = remote("cat /run/starjar/sid /run/starjar/code").split()
    debug = ""
    deadline = time.time() + 20
    while time.time() < deadline:
        result = subprocess.run(
            [*SSH, "curl -fsS http://127.0.0.1:8080/debug"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            debug = result.stdout
            break
        time.sleep(0.4)
    if not debug:
        raise AssertionError("debug page did not come up")
    status = remote("/usr/local/bin/jump status")
    payload = json.loads(status)
    assert payload["ok"] is True
    assert payload["stage"] in {"idle", "phase1", "phase1-dry", "phase2", "victory", "leds"}
    assert "sid" not in payload
    for secret in secrets:
        if secret in debug or secret in status:
            raise AssertionError("a local page or jump status contains an attempt secret")
    assert "stage: idle" in debug
    assert "now spelling the code" not in debug
    assert remote("test -d /var/lib/starjar && echo ok").strip() == "ok"


def _dark() -> None:
    """Keep the strip off. The hunt is make demo, not make test."""

    remote("touch /run/starjar/hold")
    subprocess.run(
        [*SSH, "/usr/local/bin/jump idle"],
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )


@pytest.fixture(scope="session", autouse=True)
def jar_plugged_in():
    result = subprocess.run(
        [*SSH, "true"],
        check=False,
        capture_output=True,
        text=True,
        timeout=40,
    )
    if result.returncode == 253:
        pytest.fail(
            result.stderr.strip()
            or "the jar is visible, but it is probably restarting. that takes a few minutes.",
            pytrace=False,
        )
    if result.returncode != 0:
        pytest.fail(
            "the jar is not reachable over USB\n" + result.stderr.strip(),
            pytrace=False,
        )
    _dark()
    yield
    _dark()
