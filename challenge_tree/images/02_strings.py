"""Figure. The highlighted bytes are a joke, not the jar's code."""

CAPTION = "we already ran strings"


def svg():
    w, h = 360, 196
    cols = 8
    hex_x = 48
    hex_w = 22
    ascii_x = hex_x + cols * hex_w + 8
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="ui-monospace, monospace">',
        f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>',
        '<text x="12" y="16" dominant-baseline="middle" font-size="14" fill="#222">strings(1)</text>',
    ]
    secret = b"SEGFAULT"
    for row in range(6):
        cy = 40 + row * 24
        addr = row * cols
        parts.append(
            f'<text x="12" y="{cy}" dominant-baseline="middle" font-size="13" fill="#888">'
            f"{addr:04x}</text>"
        )
        for col in range(cols):
            index = addr + col
            if row == 2:
                byte = secret[col]
                mark = True
            else:
                byte = 0x80 + ((index * 17 + 3) % 0x70)
                mark = False
            x = hex_x + col * hex_w
            if mark:
                parts.append(
                    f'<rect x="{x - 1}" y="{cy - 10}" width="20" height="18" fill="#ffe56a"/>'
                )
                parts.append(
                    f'<rect x="{ascii_x + col * 12 - 1}" y="{cy - 10}" width="12" height="18" fill="#ffe56a"/>'
                )
            parts.append(
                f'<text x="{x}" y="{cy}" dominant-baseline="middle" font-size="13" fill="#222">'
                f"{byte:02X}</text>"
            )
            shown = chr(byte) if mark else "."
            parts.append(
                f'<text x="{ascii_x + col * 12}" y="{cy}" dominant-baseline="middle" '
                f'font-size="13" fill="#222">{shown}</text>'
            )
    parts.append("</svg>")
    return "".join(parts)
