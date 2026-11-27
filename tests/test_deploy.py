from pathlib import Path


def test_boot_unit_restarts_and_is_not_cron():
    unit = Path("deploy/starjar.service").read_text(encoding="utf-8")
    leds = Path("deploy/starjar-leds.service").read_text(encoding="utf-8")
    install = Path("deploy/install.sh").read_text(encoding="utf-8")
    assert "Restart=on-failure" in unit
    assert "WantedBy=multi-user.target" in unit
    assert "User=star" in unit
    assert "User=root" in leds
    assert "Restart=on-failure" in leds
    assert "systemctl enable" in install
    assert "crontab" in install
    assert "reboot" not in install
    assert "pip" not in install
    assert "uv " not in install
    makefile = Path("Makefile").read_text(encoding="utf-8")
    assert "morse-visual" not in makefile.split("help:")[1].split("test:")[0]
    for name in ("help", "test", "shell", "demo", "install", "clean"):
        assert f"{name}:" in makefile
    assert "\nbuild:" not in makefile
    demo = Path("scripts/starjar-demo").read_text(encoding="utf-8")
    assert "starjar-install" in demo
    assert "make build" not in demo
    assert '["make", "-C", str(ROOT), "clean"]' in demo
    assert "def _stop_jar" not in demo
    assert "jar_tests" in makefile
    assert "jar:" not in makefile


def test_clean_uninstalls_the_challenge_and_clears_traces():
    script = Path("scripts/starjar-clean").read_text(encoding="utf-8")
    makefile = Path("Makefile").read_text(encoding="utf-8")
    help_text = makefile.split("help:")[1].split("test:")[0]
    assert "scripts/starjar-clean" in makefile
    assert "Does not remove the installed service" not in makefile
    assert "scoreboard" in help_text
    assert "Trivia" in help_text
    assert "systemctl disable --now starjar.service starjar-leds.service" in script
    assert "rm -rf /opt/starjar" in script
    assert ".bash_history" in script
    assert "systemd-journald" in script
    assert "starjar-attempt-" in script
    assert "/var/lib/starjar" not in script
    assert "starjar-usb-gadget.service" not in script
    assert not any(line.strip().startswith("reboot") for line in script.splitlines())
