import asyncio
import os
from pathlib import Path

from aiohttp.test_utils import TestClient, TestServer

from starjar.secrets import Attempt
from starjar.web import DEBUG_BODY, SECRET_PATH, TAUNT_CODE, TAUNT_PATH, AppState, make_app


def _state(tmp_path: Path, attempt: Attempt, trivia: Path | None = None) -> AppState:
    root = tmp_path / "challenge_tree"
    (root / "images").mkdir(parents=True)
    (root / "robots.txt").write_text("Disallow: /debrief\n", encoding="utf-8")
    (root / "routes.py.bak").write_text("POST /debrief\n", encoding="utf-8")
    www = tmp_path / "www"
    www.mkdir()
    (www / "index.html").write_text("brython.js\n/get/\n", encoding="utf-8")
    (www / "brython.js").write_text("brython", encoding="utf-8")
    (www / "brython_stdlib.js").write_text("stdlib", encoding="utf-8")
    return AppState(
        www=www,
        challenge_tree=root,
        trivia=trivia or (tmp_path / "missing.toml"),
        scoreboard=tmp_path / "scoreboard.json",
        attempt=attempt,
    )


async def test_debug_hides_the_code_and_secret_route_requires_it(tmp_path: Path):
    attempt = Attempt("AB12CD34", "Q7K2")
    app = make_app(_state(tmp_path, attempt))
    async with TestClient(TestServer(app)) as client:
        debug = await client.get("/debug")
        debug_body = await debug.text()
        assert debug.status == 200
        assert debug_body.strip() == DEBUG_BODY
        assert attempt.code not in debug_body
        assert attempt.sid not in debug_body

        wrong = await client.post(SECRET_PATH, data={"code": "NOPE"})
        wrong_body = await wrong.text()
        assert wrong.status == 200
        assert TAUNT_CODE.strip() in wrong_body
        assert attempt.code not in wrong_body
        assert "Traceback" not in wrong_body

        right = await client.post(SECRET_PATH, data={"code": attempt.code})
        right_body = await right.text()
        assert right.status == 200
        assert "Ask someone who was there." in right_body
        assert "<li>" not in right_body
        assert attempt.code not in right_body
        assert "Traceback" not in right_body


async def test_jail_over_http_and_scoreboard_is_not_the_reader(tmp_path: Path):
    attempt = Attempt("AB12CD34", "Q7K2")
    outside = tmp_path / "trivia.toml"
    outside.write_text(
        'title = "T"\nprompt = "Ask someone who was there."\nquestions = ["One."]\n',
        encoding="utf-8",
    )
    state = _state(tmp_path, attempt, trivia=outside)
    (state.challenge_tree / "leak").symlink_to(outside)
    state.scoreboard.write_text('[{"initials":"AL","time":9,"code":"Q7K2"}]\n', encoding="utf-8")
    (state.challenge_tree / "scoreboard.json").write_text('[{"initials":"NO","time":1}]\n', encoding="utf-8")
    app = make_app(state)

    async with TestClient(TestServer(app)) as client:
        listing = await client.get("/get/")
        listed = await listing.text()
        assert "routes.py.bak" in listed
        assert "images/" in listed
        assert attempt.code not in listed

        leak = await client.get("/get/leak")
        leak_body = await leak.text()
        assert leak.status == 404
        assert "One." not in leak_body
        assert TAUNT_PATH.strip() in leak_body
        assert "Traceback" not in leak_body

        missing = await client.get("/get/images/nope.png")
        assert missing.status == 404
        assert "Traceback" not in await missing.text()

        images = await client.get("/get/images")
        assert images.status == 200
        assert "Traceback" not in await images.text()

        board = await client.get("/scoreboard")
        payload = await board.json()
        assert payload == [{"initials": "AL", "time": 9}]
        assert "code" not in await board.text()

        page = await client.get("/")
        assert page.status == 200


async def test_raw_dotdot_does_not_escape(tmp_path: Path):
    attempt = Attempt("AB12CD34", "Q7K2")
    outside = tmp_path / "passwd"
    outside.write_text("root:x:0:0:root:/root:/bin/sh\n", encoding="utf-8")
    app = make_app(_state(tmp_path, attempt))
    runner = __import__("aiohttp").web.AppRunner(app)
    await runner.setup()
    site = __import__("aiohttp").web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    sockets = [sock for sock in site._server.sockets]  # type: ignore[attr-defined]
    port = sockets[0].getsockname()[1]
    try:
        reader, writer = await asyncio.open_connection("127.0.0.1", port)
        writer.write(b"GET /get/../../etc/passwd HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        await writer.drain()
        body = await reader.read()
        writer.close()
        await writer.wait_closed()
    finally:
        await runner.cleanup()
    assert b"Traceback" not in body
    assert b"root:x:" not in body
    assert outside.read_text(encoding="utf-8").encode() not in body


def test_committed_tree_names_the_list_and_the_secret_path():
    html = Path("www/index.html").read_text(encoding="utf-8")
    assert 'src="/brython.js"' in html
    assert 'src="/brython_stdlib.js"' in html
    assert "/get/" in html
    assert "cdn" not in html.lower()
    assert "http://" not in html.lower()
    assert "https://" not in html.lower()
    version = Path("www/brython.version").read_text(encoding="utf-8")
    assert version.startswith("3.15.0\n")
    assert Path("www/brython.js").stat().st_size > 100_000
    assert Path("www/brython_stdlib.js").stat().st_size > 100_000
    bak = Path("challenge_tree/routes.py.bak").read_text(encoding="utf-8")
    robots = Path("challenge_tree/robots.txt").read_text(encoding="utf-8")
    assert SECRET_PATH in bak
    assert SECRET_PATH in robots
    images = Path("challenge_tree/images")
    figures = [
        path
        for path in images.iterdir()
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp"}
    ]
    assert figures == []


def test_config_example_has_pin_18_and_no_secrets():
    from starjar.config import load_config

    text = Path("config.example.toml").read_text(encoding="utf-8").lower()
    assert "password" not in text
    assert "ssid" not in text
    config = load_config(Path("config.example.toml"), base=Path("."))
    assert config.led_pin == 18
    assert config.led_count == 50
    assert config.attempt == Path("/run/starjar")
    assert config.trivia == Path("/var/lib/starjar/trivia.toml")
    assert config.scoreboard == Path("/var/lib/starjar/scoreboard.json")
    from starjar.leds import pwm_kwargs

    kwargs = pwm_kwargs(config.led_count, config.led_pin, config.led_order)
    assert kwargs["pin"] == 18
    assert kwargs["channel"] == 0
    assert "spi" not in kwargs
