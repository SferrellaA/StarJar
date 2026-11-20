"""Figure. A rename that did not help. Not a secret."""

CAPTION = "renamed for clarity"


def _box(x, y, label, stroke):
    return (
        f'<rect x="{x}" y="{y}" width="168" height="36" fill="#ffffff" stroke="{stroke}" stroke-width="2"/>'
        f'<text x="{x + 84}" y="{y + 18}" text-anchor="middle" dominant-baseline="middle" '
        f'font-family="ui-monospace, monospace" font-size="13" fill="#222">{label}</text>'
    )


def svg():
    w, h = 420, 176
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>',
        '<text x="104" y="28" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#666">before</text>',
        '<text x="316" y="28" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#666">after</text>',
        _box(20, 48, "FUN_00401234", "#222222"),
        _box(232, 48, "FUN_00401234_1", "#c40000"),
        '<text x="210" y="140" text-anchor="middle" font-family="sans-serif" font-size="15" '
        'font-weight="700" fill="#c40000">much clearer</text>',
        "</svg>",
    ]
    return "".join(parts)
