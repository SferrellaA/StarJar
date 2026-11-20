"""Figure. A projected solid. There is no model to rotate."""

import math

CAPTION = "the binary, unfolded"


def _edges():
    verts = [(x, y, z) for x in (-1.0, 1.0) for y in (-1.0, 1.0) for z in (-1.0, 1.0)]
    found = []
    for i, a in enumerate(verts):
        for b in verts[i + 1 :]:
            if sum(p != q for p, q in zip(a, b)) == 1:
                found.append((a, b))
    return found


def _project(x, y, z, spin):
    c, s = math.cos(spin), math.sin(spin)
    x, z = c * x - s * z, s * x + c * z
    ay, ax = 0.55, 0.62
    c, s = math.cos(ay), math.sin(ay)
    x, z = c * x + s * z, -s * x + c * z
    c, s = math.cos(ax), math.sin(ax)
    y, z = c * y - s * z, s * y + c * z
    f = 4.0 / (z + 5.8)
    return x * 78 * f, y * 78 * f


def svg():
    w, h = 280, 240
    cx, cy = 140, 128
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">',
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>',
    ]
    edges = _edges()
    for spin, color in ((0.0, "#222222"), (math.pi / 4, "#c40000")):
        for a, b in edges:
            x1, y1 = _project(*a, spin)
            x2, y2 = _project(*b, spin)
            parts.append(
                f'<line x1="{cx + x1:.1f}" y1="{cy - y1:.1f}" x2="{cx + x2:.1f}" '
                f'y2="{cy - y2:.1f}" stroke="{color}" stroke-width="1.4"/>'
            )
    parts.append("</svg>")
    return "".join(parts)
