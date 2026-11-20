"""Figure. A fake listing. The summary is the joke, not a finding."""

CAPTION = "decompiler output (trust it)"


def _esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg():
    w, h = 380, 228
    lines = [
        "undefined FUN_08001234(void)",
        "{",
        "  if (real) {",
        "    respect();",
        "  }",
        "  /* stopped here */",
        "}",
    ]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">',
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>',
        f'<rect x="0" y="0" width="{w}" height="28" fill="#eeeeee"/>',
        '<text x="12" y="14" dominant-baseline="middle" font-family="sans-serif" '
        'font-size="13" fill="#333">decompile</text>',
        f'<rect x="12" y="40" width="{w - 24}" height="26" fill="#ffe56a"/>',
        '<text x="190" y="53" text-anchor="middle" dominant-baseline="middle" '
        'font-family="sans-serif" font-size="13" fill="#222">AI summary: function is fine</text>',
    ]
    y = 88
    for line in lines:
        parts.append(
            f'<text x="16" y="{y}" font-family="ui-monospace, monospace" font-size="14" '
            f'fill="#222">{_esc(line)}</text>'
        )
        y += 16
    parts.append(
        '<text x="190" y="212" text-anchor="middle" font-family="sans-serif" '
        'font-size="13" font-weight="700" fill="#c40000">backdoor not included</text>'
    )
    parts.append("</svg>")
    return "".join(parts)
