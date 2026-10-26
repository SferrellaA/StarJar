"""Stage 3 comes from a file outside the jail. No answer key is rendered."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from html import escape
from pathlib import Path

STANDING_PROMPT = "Ask someone who was there."


@dataclass(frozen=True)
class Trivia:
    title: str
    prompt: str
    questions: tuple[str, ...]


def load_trivia(path: Path) -> Trivia:
    try:
        data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError):
        return Trivia("", STANDING_PROMPT, ())
    if not isinstance(data, dict):
        return Trivia("", STANDING_PROMPT, ())
    title = data.get("title")
    prompt = data.get("prompt")
    raw_questions = data.get("questions")
    questions: list[str] = []
    if isinstance(raw_questions, list):
        questions = [item for item in raw_questions if isinstance(item, str)]
    return Trivia(
        title if isinstance(title, str) else "",
        prompt if isinstance(prompt, str) and prompt else STANDING_PROMPT,
        tuple(questions),
    )


def render_stage3(trivia: Trivia) -> str:
    parts = [
        "<!DOCTYPE html>",
        '<html><head><meta charset="utf-8">',
        "<title>" + escape(trivia.title) + "</title>" if trivia.title else "",
        "</head><body>",
    ]
    if trivia.title:
        parts.append("<h1>" + escape(trivia.title) + "</h1>")
    parts.append("<p>" + escape(trivia.prompt) + "</p>")
    if trivia.questions:
        parts.append("<ol>")
        parts.extend("<li>" + escape(question) + "</li>" for question in trivia.questions)
        parts.append("</ol>")
    parts.append("</body></html>")
    return "\n".join(part for part in parts if part)
