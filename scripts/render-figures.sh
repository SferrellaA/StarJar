#!/bin/sh
# Render the joke figures and open a gallery next to the spec.
# Usage: scripts/render-figures.sh [--no-open] [output-dir]
# Spec: scripts/figures.md
set -eu
root=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
no_open=0
out=""
for arg in "$@"; do
  case $arg in
    --no-open) no_open=1 ;;
    *) out=$arg ;;
  esac
done
if [ -z "$out" ]; then
  out=${TMPDIR:-/tmp}/starjar-figures
fi
mkdir -p "$out"
python3 - "$root" "$out" <<'PY'
import sys
from pathlib import Path

root = Path(sys.argv[1])
out = Path(sys.argv[2])
images = root / "challenge_tree" / "images"
spec_path = root / "scripts" / "figures.md"
spec = spec_path.read_text(encoding="utf-8")
sections = {}
current = None
buf = []
for line in spec.splitlines():
    if line.startswith("## "):
        if current is not None:
            sections[current] = "\n".join(buf).strip()
        current = line[3:].strip()
        buf = []
    elif current is not None:
        buf.append(line)
if current is not None:
    sections[current] = "\n".join(buf).strip()

files = sorted(path for path in images.glob("*.py") if path.is_file())
if not files:
    sys.exit("no figure generators")
missing = [path.name for path in files if path.name not in sections]
if missing:
    sys.exit("scripts/figures.md missing: " + ", ".join(missing))

cards = []
for path in files:
    ns = {"__name__": path.stem}
    exec(path.read_text(encoding="utf-8"), ns)
    markup = ns["svg"]()
    if not isinstance(markup, str) or not markup.lstrip().startswith("<svg"):
        sys.exit(f"{path.name} did not return an svg")
    (out / f"{path.stem}.svg").write_text(markup, encoding="utf-8")
    caption = str(ns.get("CAPTION", ""))
    checklist = sections[path.name]
    items = []
    for raw in checklist.splitlines():
        text = raw.strip()
        if text.startswith("- "):
            items.append("<li>" + text[2:].replace("&", "&amp;").replace("<", "&lt;") + "</li>")
        elif text:
            items.append("<p>" + text.replace("&", "&amp;").replace("<", "&lt;") + "</p>")
    cards.append(
        "<article><h2>"
        + path.name
        + "</h2><p class='cap'>"
        + caption.replace("&", "&amp;").replace("<", "&lt;")
        + "</p>"
        + markup
        + "<div class='spec'>"
        + "".join(items)
        + "</div></article>"
    )

page = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>starjar figures</title>
<style>
body { margin: 1.5rem auto; max-width: 52rem; font-family: sans-serif; color: #222; background: #d2e0fb; }
article { background: #fff; padding: 1rem; margin: 1rem 0; }
h2 { margin: 0 0 0.3rem; font-size: 1rem; }
.cap { color: #c40000; font-weight: 700; }
.spec { color: #333; }
svg { border: 1px solid #bbb; max-width: 100%; height: auto; }
</style></head><body>
<h1>figure check</h1>
<p>Spec is scripts/figures.md. If a picture disagrees with the list, the generator is wrong.</p>
""" + "\n".join(cards) + "</body></html>\n"
(out / "index.html").write_text(page, encoding="utf-8")
print(out / "index.html")
PY

printf 'spec: %s\n' "$root/scripts/figures.md"
if [ "$no_open" -eq 1 ]; then
  exit 0
fi
if grep -qi microsoft /proc/version 2>/dev/null && command -v explorer.exe >/dev/null 2>&1 && command -v wslpath >/dev/null 2>&1; then
  explorer.exe "$(wslpath -w "$out/index.html")" >/dev/null 2>&1 || true
elif command -v wslview >/dev/null 2>&1; then
  wslview "$out/index.html" >/dev/null 2>&1 || true
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$out/index.html" >/dev/null 2>&1 || true
fi
