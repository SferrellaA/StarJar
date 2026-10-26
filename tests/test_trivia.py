import tomllib
from pathlib import Path

from starjar.trivia import STANDING_PROMPT, load_trivia, render_stage3


def test_example_is_placeholders_without_answers():
    data = tomllib.loads(Path("trivia.example.toml").read_text(encoding="utf-8"))
    assert "answer" not in data
    assert "answers" not in data
    assert data["prompt"] == STANDING_PROMPT
    assert isinstance(data["questions"], list)
    assert len(data["questions"]) >= 1


def test_missing_or_broken_file_returns_the_prompt_without_questions(tmp_path: Path):
    missing = render_stage3(load_trivia(tmp_path / "missing.toml"))
    assert STANDING_PROMPT in missing
    assert "<li>" not in missing
    assert "Traceback" not in missing

    broken = tmp_path / "broken.toml"
    broken.write_text("this is not [\n", encoding="utf-8")
    rendered = render_stage3(load_trivia(broken))
    assert STANDING_PROMPT in rendered
    assert "<li>" not in rendered

    unread = render_stage3(load_trivia(tmp_path))
    assert "<li>" not in unread


def test_renders_questions_in_order_and_ignores_an_answer_key(tmp_path: Path):
    path = tmp_path / "trivia.toml"
    path.write_text(
        "\n".join(
            [
                'title = "After"',
                'prompt = "Ask someone who was there."',
                "questions = [",
                '  "First placeholder.",',
                '  "Second placeholder.",',
                "]",
                'answers = ["secret-answer-value"]',
            ]
        ),
        encoding="utf-8",
    )
    html = render_stage3(load_trivia(path))
    assert html.index("First placeholder.") < html.index("Second placeholder.")
    assert "secret-answer-value" not in html
    assert "<ol>" in html


def test_escapes_question_text(tmp_path: Path):
    path = tmp_path / "trivia.toml"
    path.write_text(
        'title = "T"\nprompt = "Ask someone who was there."\n'
        'questions = ["<script>alert(1)</script>"]\n',
        encoding="utf-8",
    )
    html = render_stage3(load_trivia(path))
    assert "<script>alert" not in html
    assert "&lt;script&gt;" in html
