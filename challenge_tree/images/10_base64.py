"""Figure. The blob is hello. Not a key."""

import math

CAPTION = "military-grade"


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


def _box(x, y, w, h, label, stroke):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#ffffff" stroke="{stroke}" stroke-width="2"/>'
        f'<text x="{x + w / 2:.0f}" y="{y + h / 2:.0f}" text-anchor="middle" dominant-baseline="middle" '
        f'font-family="ui-monospace, monospace" font-size="16" fill="#222">{label}</text>'
    )


def svg():
    w, h = 320, 210
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>',
        '<text x="160" y="22" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#666">encrypted payload</text>',
        _box(70, 40, 180, 34, "aGVsbG8=", "#222222"),
        _arrow(160, 74, 160, 112),
        _box(70, 112, 180, 34, "hello", "#c40000"),
        '<text x="160" y="168" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#c40000">base64</text>',
        '<text x="160" y="192" text-anchor="middle" font-family="sans-serif" font-size="15" '
        'font-weight="700" fill="#c40000">the key was the alphabet</text>',
        "</svg>",
    ]
    return "".join(parts)
