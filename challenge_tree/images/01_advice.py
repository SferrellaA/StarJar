"""Figure. Drawing code only. This file is not the jar's code."""

import math

CAPTION = "standard procedure"


def _esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _arrow(x1, y1, x2, y2, color):
    ang = math.atan2(y2 - y1, x2 - x1)
    head = 8
    left = ang + 2.6
    right = ang - 2.6
    tip = (x2, y2)
    a = (x2 - head * math.cos(left), y2 - head * math.sin(left))
    b = (x2 - head * math.cos(right), y2 - head * math.sin(right))
    points = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in (tip, a, b))
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{color}" stroke-width="1.6"/>'
        f'<polygon points="{points}" fill="{color}"/>'
    )


def _box(x, y, w, h, label, stroke):
    cx = x + w / 2
    cy = y + h / 2
    return (
        f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" '
        f'fill="#ffffff" stroke="{stroke}" stroke-width="2"/>'
        f'<text x="{cx:.0f}" y="{cy:.0f}" text-anchor="middle" dominant-baseline="middle" '
        f'font-family="sans-serif" font-size="13" fill="#222">{_esc(label)}</text>'
    )


def svg():
    w, h = 520, 228
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">',
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>',
        '<line x1="260" y1="22" x2="260" y2="176" stroke="#dddddd" stroke-width="1"/>',
    ]
    parts.append(
        '<text x="130" y="18" text-anchor="middle" font-family="sans-serif" '
        'font-size="13" fill="#666">old advice</text>'
    )
    parts.append(
        '<text x="390" y="18" text-anchor="middle" font-family="sans-serif" '
        'font-size="13" fill="#666">new advice</text>'
    )
    left = [
        (36, 32, "won't disassemble", "#222222"),
        (36, 92, "did you install kali?", "#c40000"),
        (36, 152, "install kali", "#222222"),
    ]
    right = [
        (276, 32, "still won't", "#222222"),
        (276, 92, "have you tried ghidra-mcp?", "#c40000"),
        (276, 152, "all 110 tools", "#222222"),
    ]
    box_w, box_h = 208, 32
    for x, y, label, stroke in left + right:
        parts.append(_box(x, y, box_w, box_h, label, stroke))
    for x in (140, 380):
        parts.append(_arrow(x, 64, x, 92, "#222222"))
        parts.append(_arrow(x, 124, x, 152, "#222222"))
    # Loops back to the question. Neither column reaches the bytes.
    parts.append(
        '<line x1="36" y1="168" x2="16" y2="168" stroke="#c40000" stroke-width="1.6"/>'
        '<line x1="16" y1="168" x2="16" y2="108" stroke="#c40000" stroke-width="1.6"/>'
    )
    parts.append(_arrow(16, 108, 36, 108, "#c40000"))
    parts.append(
        '<line x1="484" y1="168" x2="504" y2="168" stroke="#c40000" stroke-width="1.6"/>'
        '<line x1="504" y1="168" x2="504" y2="108" stroke="#c40000" stroke-width="1.6"/>'
    )
    parts.append(_arrow(504, 108, 484, 108, "#c40000"))
    parts.append(
        '<text x="260" y="208" text-anchor="middle" font-family="sans-serif" '
        'font-size="15" font-weight="700" fill="#c40000">the bytes remain unread</text>'
    )
    parts.append("</svg>")
    return "".join(parts)
