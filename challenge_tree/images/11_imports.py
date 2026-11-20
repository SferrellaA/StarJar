"""Figure. Two imports. The rest are a promise."""

CAPTION = "the import table"


def svg():
    w, h = 360, 196
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>',
        '<text x="16" y="22" font-family="sans-serif" font-size="14" fill="#666">import address table</text>',
        f'<rect x="16" y="36" width="{w - 32}" height="26" fill="#eeeeee"/>',
        '<text x="28" y="49" dominant-baseline="middle" font-family="sans-serif" font-size="13" fill="#666">name</text>',
    ]
    rows = ("GetProcAddress", "LoadLibraryA", "...")
    for i, name in enumerate(rows):
        y = 70 + i * 28
        color = "#999999" if name == "..." else "#222222"
        parts.append(f'<line x1="16" y1="{y}" x2="{w - 16}" y2="{y}" stroke="#dddddd" stroke-width="1"/>')
        parts.append(
            f'<text x="28" y="{y + 16}" dominant-baseline="middle" font-family="ui-monospace, monospace" '
            f'font-size="14" fill="{color}">{name}</text>'
        )
    parts.append(
        '<text x="180" y="176" text-anchor="middle" font-family="sans-serif" font-size="15" '
        'font-weight="700" fill="#c40000">the rest arrive later</text>'
    )
    parts.append("</svg>")
    return "".join(parts)
