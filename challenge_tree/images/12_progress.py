"""Figure. The bar is not done. There is no secret in the percentage."""

CAPTION = "almost done"


def svg():
    w, h = 400, 160
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>',
        '<text x="24" y="28" font-family="sans-serif" font-size="14" fill="#666">auto-analysis</text>',
        '<rect x="24" y="52" width="352" height="32" fill="#eeeeee" stroke="#222222" stroke-width="1.5"/>',
        '<rect x="26" y="54" width="316" height="28" fill="#ffe56a"/>',
        '<text x="200" y="68" text-anchor="middle" dominant-baseline="middle" '
        'font-family="sans-serif" font-size="14" fill="#222">99%</text>',
        '<text x="200" y="112" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#222">still running</text>',
        '<text x="200" y="140" text-anchor="middle" font-family="sans-serif" font-size="15" '
        'font-weight="700" fill="#c40000">99% since lunch</text>',
        "</svg>",
    ]
    return "".join(parts)
