"""Figure. Same bytes, two readings. Not the jar's code."""

CAPTION = "which end is the beef"


def svg():
    w, h = 360, 188
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>',
        '<text x="180" y="22" text-anchor="middle" font-family="sans-serif" font-size="15" fill="#222">the same four bytes</text>',
    ]
    labels = ("DE", "AD", "BE", "EF")
    for i, label in enumerate(labels):
        x = 92 + i * 44
        parts.append(f'<rect x="{x}" y="40" width="40" height="32" fill="#ffe56a" stroke="#222" stroke-width="1"/>')
        parts.append(
            f'<text x="{x + 20}" y="56" text-anchor="middle" dominant-baseline="middle" '
            f'font-family="ui-monospace, monospace" font-size="14" fill="#222">{label}</text>'
        )
    parts.append(
        '<text x="24" y="108" font-family="sans-serif" font-size="14" fill="#222">big-endian</text>'
        '<text x="200" y="108" font-family="ui-monospace, monospace" font-size="14" fill="#222">DEADBEEF</text>'
    )
    parts.append(
        '<text x="24" y="136" font-family="sans-serif" font-size="14" fill="#222">little-endian</text>'
        '<text x="200" y="136" font-family="ui-monospace, monospace" font-size="14" fill="#c40000">EFBEADDE</text>'
    )
    parts.append(
        '<text x="180" y="168" text-anchor="middle" font-family="sans-serif" font-size="15" '
        'font-weight="700" fill="#c40000">the beef moved</text>'
    )
    parts.append("</svg>")
    return "".join(parts)
