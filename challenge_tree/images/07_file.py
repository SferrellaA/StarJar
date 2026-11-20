"""Figure. file(1) cannot pick a species. Not a secret."""

CAPTION = "file(1) has decided"


def _line(y, text, color="#222222"):
    return (
        f'<text x="16" y="{y}" font-family="ui-monospace, monospace" font-size="15" fill="{color}">{text}</text>'
    )


def svg():
    w, h = 380, 196
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>',
        '<text x="16" y="22" font-family="sans-serif" font-size="14" fill="#666">file(1)</text>',
        _line(52, "$ file blob"),
        _line(76, "blob: data"),
        _line(100, "blob: PE32 executable"),
        _line(124, "blob: Zip archive data"),
        _line(148, "blob: JPEG image data"),
        '<text x="190" y="178" text-anchor="middle" font-family="sans-serif" font-size="15" '
        'font-weight="700" fill="#c40000">pick one</text>',
        "</svg>",
    ]
    return "".join(parts)
