"""Figure. One opcode changed. Not a recipe."""

CAPTION = "the whole patch"


def _cell(x, y, label, fill, stroke):
    return (
        f'<rect x="{x}" y="{y}" width="44" height="28" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        f'<text x="{x + 22}" y="{y + 14}" text-anchor="middle" dominant-baseline="middle" '
        f'font-family="ui-monospace, monospace" font-size="14" fill="#222">{label}</text>'
    )


def svg():
    w, h = 360, 176
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>',
        '<text x="180" y="22" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#666">the patch</text>',
        '<text x="24" y="62" dominant-baseline="middle" font-family="sans-serif" font-size="14" fill="#222">before</text>',
        _cell(100, 48, "74", "#ffffff", "#222222"),
        _cell(148, 48, "0A", "#ffffff", "#222222"),
        '<text x="210" y="62" dominant-baseline="middle" font-family="ui-monospace, monospace" font-size="14" fill="#222">jz</text>',
        '<text x="24" y="106" dominant-baseline="middle" font-family="sans-serif" font-size="14" fill="#222">after</text>',
        _cell(100, 92, "75", "#ffe56a", "#c40000"),
        _cell(148, 92, "0A", "#ffffff", "#222222"),
        '<text x="210" y="106" dominant-baseline="middle" font-family="ui-monospace, monospace" font-size="14" fill="#c40000">jnz</text>',
        '<text x="180" y="154" text-anchor="middle" font-family="sans-serif" font-size="15" '
        'font-weight="700" fill="#c40000">one byte</text>',
        "</svg>",
    ]
    return "".join(parts)
