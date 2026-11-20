"""Figure. A dependency drawing. Not a secret."""

import math

CAPTION = "real dependency graph"


def _esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _arrow(x1, y1, x2, y2):
    ang = math.atan2(y2 - y1, x2 - x1)
    head = 8
    a = (x2 - head * math.cos(ang + 2.6), y2 - head * math.sin(ang + 2.6))
    b = (x2 - head * math.cos(ang - 2.6), y2 - head * math.sin(ang - 2.6))
    points = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in ((x2, y2), a, b))
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="#222222" stroke-width="1.6"/>'
        f'<polygon points="{points}" fill="#222222"/>'
    )


def _box(x, y, w, h, label, stroke, fill):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="2"/>'
        f'<text x="{x + w / 2:.0f}" y="{y + h / 2:.0f}" text-anchor="middle" '
        f'dominant-baseline="middle" font-family="sans-serif" font-size="14" fill="#222">'
        f"{_esc(label)}</text>"
    )


def svg():
    w, h = 360, 230
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">',
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>',
        '<text x="180" y="22" text-anchor="middle" font-family="sans-serif" '
        'font-size="15" fill="#222">to print one byte</text>',
        _box(130, 40, 100, 32, "main", "#222222", "#ffffff"),
    ]
    children = [
        (16, 128, 96, "capstone", "#222222", "#ffffff"),
        (132, 128, 96, "binwalk", "#222222", "#ffffff"),
        (248, 128, 96, "left-pad", "#c40000", "#fff5f5"),
    ]
    for x, y, bw, label, stroke, fill in children:
        parts.append(_box(x, y, bw, 32, label, stroke, fill))
        parts.append(_arrow(180, 72, x + bw / 2, y))
    parts.append(
        '<text x="296" y="184" text-anchor="middle" font-family="sans-serif" '
        'font-size="13" fill="#c40000">11 lines</text>'
    )
    parts.append(
        '<text x="296" y="204" text-anchor="middle" font-family="sans-serif" '
        'font-size="13" fill="#c40000">1 byte</text>'
    )
    parts.append("</svg>")
    return "".join(parts)
