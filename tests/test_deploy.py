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
    for name in ("help", "test", "shell", "demo", "build", "clean"):
        assert f"{name}:" in makefile
    assert "jar_tests" in makefile
    assert "jar:" not in makefile
