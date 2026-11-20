"""Figure. A Go binary's strings. main is the short one."""

CAPTION = "we found main"


def svg():
    w, h = 340, 220
    lines = (
        "runtime.mallocgc",
        "runtime.morestack",
        "runtime.convT64",
        "main.main",
        "runtime.gcBgMarkWorker",
        "runtime.memmove",
    )
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>',
        '<text x="16" y="20" font-family="sans-serif" font-size="14" fill="#666">strings(1)</text>',
    ]
    for i, line in enumerate(lines):
        y = 40 + i * 24
        if line == "main.main":
            parts.append(f'<rect x="12" y="{y - 12}" width="108" height="20" fill="#ffe56a"/>')
            color = "#222222"
        else:
            color = "#888888"
        parts.append(
            f'<text x="16" y="{y}" dominant-baseline="middle" font-family="ui-monospace, monospace" '
            f'font-size="14" fill="{color}">{line}</text>'
        )
    parts.append(
        '<text x="170" y="200" text-anchor="middle" font-family="sans-serif" font-size="14" '
        'font-weight="700" fill="#c40000">the program is in there</text>'
    )
    parts.append("</svg>")
    return "".join(parts)
