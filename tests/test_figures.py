import re
from pathlib import Path

IMAGES = Path("challenge_tree/images")
SPEC = Path("scripts/figures.md")


def _load(path: Path):
    ns: dict = {"__name__": path.stem}
    exec(path.read_text(encoding="utf-8"), ns)
    markup = ns["svg"]()
    assert isinstance(markup, str)
    assert markup.lstrip().startswith("<svg ")
    assert markup.rstrip().endswith("</svg>")
    assert isinstance(ns["CAPTION"], str) and ns["CAPTION"]
    assert "transform=" not in markup
    return markup


def _bounds(markup: str):
    view = re.search(r'viewBox="0 0 ([0-9.]+) ([0-9.]+)"', markup)
    assert view is not None
    w, h = float(view.group(1)), float(view.group(2))
    for match in re.finditer(r"<rect\b([^>]*)/?>", markup):
        attrs = dict(re.findall(r'([A-Za-z-]+)="([^"]*)"', match.group(1)))
        x = float(attrs.get("x", "0"))
        y = float(attrs.get("y", "0"))
        rw = float(attrs["width"])
        rh = float(attrs["height"])
        assert -1 <= x and x + rw <= w + 1
        assert -1 <= y and y + rh <= h + 1
    for match in re.finditer(r"<line\b([^>]*)/?>", markup):
        attrs = dict(re.findall(r'([A-Za-z0-9]+)="([^"]*)"', match.group(1)))
        for key in ("x1", "y1", "x2", "y2"):
            val = float(attrs[key])
            limit = w if key.startswith("x") else h
            assert -1 <= val <= limit + 1
    for match in re.finditer(r'points="([^"]+)"', markup):
        for pair in match.group(1).split():
            x, y = pair.split(",")
            assert -1 <= float(x) <= w + 1
            assert -1 <= float(y) <= h + 1
    for match in re.finditer(r"<text\b([^>]*)>", markup):
        attrs = dict(re.findall(r'([A-Za-z-]+)="([^"]*)"', match.group(1)))
        if "x" in attrs:
            assert -1 <= float(attrs["x"]) <= w + 1
        if "y" in attrs:
            assert -1 <= float(attrs["y"]) <= h + 1


def test_generators_match_the_spec_and_stay_on_the_card():
    scripts = sorted(IMAGES.glob("*.py"))
    assert [path.name for path in scripts] == [
        "01_advice.py",
        "02_strings.py",
        "03_leftpad.py",
        "04_decompile.py",
        "05_solid.py",
        "06_endian.py",
        "07_file.py",
        "08_sections.py",
        "09_stripped.py",
        "10_base64.py",
        "11_imports.py",
        "12_progress.py",
        "13_rename.py",
        "14_runtime.py",
        "15_patch.py",
    ]
    spec = SPEC.read_text(encoding="utf-8")
    for path in scripts:
        assert f"## {path.name}" in spec
        _bounds(_load(path))
    advice = _load(IMAGES / "01_advice.py")
    assert "did you install kali?" in advice
    assert "have you tried ghidra-mcp?" in advice
    assert "all 110 tools" in advice
    assert "the bytes remain unread" in advice
    strings = _load(IMAGES / "02_strings.py")
    letters = re.findall(r">([A-Z.])</text>", strings)
    assert "".join(letters)[16:24] == "SEGFAULT"
    assert set(letters) <= set("SEGFAULT.")
    assert "strings(1)" in strings
    assert strings.count('fill="#ffe56a"') == 16
    leftpad = _load(IMAGES / "03_leftpad.py")
    assert "left-pad" in leftpad
    assert "11 lines" in leftpad
    decompile = _load(IMAGES / "04_decompile.py")
    assert "AI summary: function is fine" in decompile
    assert "undefined FUN_08001234(void)" in decompile
    solid = _load(IMAGES / "05_solid.py")
    assert solid.count("<line ") == 24
    assert "<text" not in solid
    assert "EFBEADDE" in _load(IMAGES / "06_endian.py")
    assert "DEADBEEF" in _load(IMAGES / "06_endian.py")
    file_card = _load(IMAGES / "07_file.py")
    assert "PE32 executable" in file_card and "JPEG image data" in file_card
    sections = _load(IMAGES / "08_sections.py")
    assert ".rsrc" in sections and "the program is the resource" in sections
    stripped = _load(IMAGES / "09_stripped.py")
    assert ">a.1<" in stripped and ">a.3<" in stripped
    assert "aGVsbG8=" in _load(IMAGES / "10_base64.py")
    assert "GetProcAddress" in _load(IMAGES / "11_imports.py")
    assert "99%" in _load(IMAGES / "12_progress.py")
    renamed = _load(IMAGES / "13_rename.py")
    assert "FUN_00401234_1" in renamed and "FUN_00401234<" in renamed
    runtime = _load(IMAGES / "14_runtime.py")
    assert "main.main" in runtime and runtime.count("runtime.") == 5
    patch = _load(IMAGES / "15_patch.py")
    assert ">74<" in patch and ">75<" in patch and ">jnz<" in patch


def test_page_runs_the_generators_and_still_names_the_list():
    html = Path("www/index.html").read_text(encoding="utf-8")
    assert "/get/" in html
    assert "/get/images" in html
    assert "exec(" in html
    assert "have you tried ghidra-mcp?" in html
    script = Path("scripts/render-figures.sh").read_text(encoding="utf-8")
    assert "figures.md" in script
