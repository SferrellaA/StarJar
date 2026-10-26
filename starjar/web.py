"""Sloppy routes, jailed reads. The debug route does not know the code."""

from __future__ import annotations

import hmac
import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

from aiohttp import web

from starjar.jail import JailError, resolve_inside
from starjar.scoreboard import load_public
from starjar.secrets import Attempt
from starjar.trivia import load_trivia, render_stage3

SECRET_PATH = "/debrief"
DEBUG_BODY = "The jar is spelling the code."
TAUNT_PATH = "Nothing in the jar by that name."
TAUNT_CODE = "That is not what the jar is spelling."
TEXT_SUFFIXES = {".bak", ".py", ".txt", ".toml", ".md", ".html", ".css"}


@dataclass
class AppState:
    www: Path
    challenge_tree: Path
    trivia: Path
    scoreboard: Path
    attempt: Attempt


STATE_KEY = web.AppKey("state", AppState)


def make_app(state: AppState) -> web.Application:
    app = web.Application(middlewares=[guard])
    app[STATE_KEY] = state
    app.router.add_get("/", index)
    app.router.add_get("/brython.js", www_file("brython.js"))
    app.router.add_get("/brython_stdlib.js", www_file("brython_stdlib.js"))
    app.router.add_get("/robots.txt", robots)
    app.router.add_get("/debug", debug)
    app.router.add_get(SECRET_PATH, debrief_form)
    app.router.add_post(SECRET_PATH, debrief_submit)
    app.router.add_get("/get", listing_root)
    app.router.add_get("/get/", listing_root)
    app.router.add_get("/get/{path:.*}", read_tail)
    app.router.add_get("/scoreboard", scoreboard_route)
    return app


@web.middleware
async def guard(request: web.Request, handler):
    raw = request.raw_path or ""
    if ".." in raw or ".." in unquote(raw) or ".." in request.path:
        return _taunt(TAUNT_PATH, status=404)
    try:
        return await handler(request)
    except (JailError, FileNotFoundError):
        return _taunt(TAUNT_PATH, status=404)
    except Exception:
        return _taunt(TAUNT_PATH, status=404)


async def index(request: web.Request) -> web.StreamResponse:
    return await _www(request, "index.html")


def www_file(name: str):
    async def handler(request: web.Request) -> web.StreamResponse:
        return await _www(request, name)

    return handler


async def robots(request: web.Request) -> web.Response:
    path = _state(request).challenge_tree / "robots.txt"
    if not path.is_file():
        return _taunt(TAUNT_PATH, status=404)
    return web.Response(text=path.read_text(encoding="utf-8"), content_type="text/plain")


async def debug(_request: web.Request) -> web.Response:
    return web.Response(text=DEBUG_BODY + "\n", content_type="text/plain")


async def debrief_form(_request: web.Request) -> web.Response:
    body = (
        "<!DOCTYPE html><html><body>"
        '<form method="post" action="/debrief">'
        '<label>Code <input name="code" autocomplete="off"></label>'
        '<button type="submit">Enter</button>'
        "</form></body></html>"
    )
    return web.Response(text=body, content_type="text/html")


async def debrief_submit(request: web.Request) -> web.Response:
    state = _state(request)
    form = await request.post()
    given = form.get("code", "")
    if not isinstance(given, str):
        given = ""
    if not hmac.compare_digest(given, state.attempt.code):
        return _taunt(TAUNT_CODE, status=200)
    page = render_stage3(load_trivia(state.trivia))
    return web.Response(text=page, content_type="text/html")


async def listing_root(request: web.Request) -> web.Response:
    return _listing(_state(request).challenge_tree)


async def read_tail(request: web.Request) -> web.StreamResponse:
    return _serve_tree(request, request.match_info.get("path", ""))


async def scoreboard_route(request: web.Request) -> web.Response:
    path = _state(request).scoreboard
    try:
        entries = load_public(path)
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        entries = []
    return web.json_response(entries)


def _serve_tree(request: web.Request, requested: str) -> web.StreamResponse:
    root = _state(request).challenge_tree
    path = resolve_inside(root, requested)
    if path.is_dir():
        return _listing(path)
    return _file(path)


def _listing(path: Path) -> web.Response:
    names = []
    for child in sorted(path.iterdir(), key=lambda item: item.name):
        if child.is_symlink() or not child.is_dir():
            names.append(child.name)
        else:
            names.append(child.name + "/")
    text = ("\n".join(names) + "\n") if names else ""
    return web.Response(text=text, content_type="text/plain")


def _file(path: Path) -> web.Response:
    if path.suffix.lower() in TEXT_SUFFIXES:
        return web.Response(text=path.read_text(encoding="utf-8"), content_type="text/plain")
    return web.FileResponse(path)


async def _www(request: web.Request, name: str) -> web.StreamResponse:
    path = _state(request).www / name
    if not path.is_file() or path.is_symlink():
        return _taunt(TAUNT_PATH, status=404)
    return web.FileResponse(path)


def _state(request: web.Request) -> AppState:
    return request.app[STATE_KEY]


def _taunt(text: str, status: int) -> web.Response:
    return web.Response(status=status, text=text + "\n", content_type="text/plain")
