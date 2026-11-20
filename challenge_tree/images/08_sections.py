"""Figure. The section chart is the joke."""

CAPTION = "the program"


def svg():
    w, h = 420, 188
    rows = (
        (".text", 40, "#222222"),
        (".data", 24, "#222222"),
        (".rsrc", 300, "#c40000"),
    )
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>',
        '<text x="16" y="22" font-family="sans-serif" font-size="14" fill="#666">section sizes</text>',
    ]
    for i, (name, bar, color) in enumerate(rows):
        y = 44 + i * 36
        parts.append(
            f'<text x="16" y="{y + 12}" dominant-baseline="middle" font-family="ui-monospace, monospace" '
            f'font-size="14" fill="{color}">{name}</text>'
        )
        parts.append(
            f'<rect x="84" y="{y}" width="{bar}" height="24" fill="{color}"/>'
        )
    parts.append(
        '<text x="210" y="168" text-anchor="middle" font-family="sans-serif" font-size="15" '
        'font-weight="700" fill="#c40000">the program is the resource</text>'
    )
    parts.append("</svg>")
    return "".join(parts)
