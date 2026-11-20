"""Figure. The names did not survive strip. Not a secret."""

import math

CAPTION = "after strip"


def _arrow(x1, y1, x2, y2):
    ang = math.atan2(y2 - y1, x2 - x1)
    head = 8
    a = (x2 - head * math.cos(ang + 2.6), y2 - head * math.sin(ang + 2.6))
    b = (x2 - head * math.cos(ang - 2.6), y2 - head * math.sin(ang - 2.6))
    points = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in ((x2, y2), a, b))
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#222222" stroke-width="1.6"/>'
        f'<polygon points="{points}" fill="#222222"/>'
    )


def _box(x, y, label):
    return (
        f'<rect x="{x}" y="{y}" width="72" height="30" fill="#ffffff" stroke="#222222" stroke-width="2"/>'
        f'<text x="{x + 36}" y="{y + 15}" text-anchor="middle" dominant-baseline="middle" '
        f'font-family="ui-monospace, monospace" font-size="14" fill="#222">{label}</text>'
    )


def svg():
    w, h = 360, 200
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>',
        '<text x="180" y="20" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#666">symbols</text>',
        _box(144, 36, "a"),
    ]
    children = ((20, "a.1"), (144, "a.2"), (268, "a.3"))
    for x, label in children:
        parts.append(_arrow(180, 66, x + 36, 108))
        parts.append(_box(x, 108, label))
    parts.append(
        '<text x="180" y="176" text-anchor="middle" font-family="sans-serif" font-size="15" '
        'font-weight="700" fill="#c40000">the names were the documentation</text>'
    )
    parts.append("</svg>")
    return "".join(parts)
