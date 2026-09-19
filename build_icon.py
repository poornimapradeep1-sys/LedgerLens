"""
build_icon.py

One-off build asset generator: renders the same violet-to-cyan gradient
rounded-square + checkmark used by theme.make_app_icon() (Qt, runtime)
as a standalone multi-size .ico file for PyInstaller's --icon flag,
since PyInstaller needs a file on disk, not a QIcon in memory. Not
imported by the app itself — run manually only when the icon design
changes.
"""

from PIL import Image, ImageDraw

VIOLET_DARK = (124, 58, 237)
CYAN = (34, 211, 238)


def render(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pad = max(1, round(size * 0.03))
    radius = round(size * 0.22)
    for y in range(size):
        t = y / max(1, size - 1)
        color = tuple(round(VIOLET_DARK[i] + (CYAN[i] - VIOLET_DARK[i]) * t) for i in range(3))
        draw.line([(0, y), (size, y)], fill=color)

    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([pad, pad, size - pad, size - pad], radius=radius, fill=255)

    bg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bg.paste(img, (0, 0), mask)

    draw = ImageDraw.Draw(bg)
    width = max(2, round(size * 0.078))
    pts = [
        (size * 0.28, size * 0.52),
        (size * 0.44, size * 0.68),
        (size * 0.74, size * 0.34),
    ]
    draw.line(pts, fill=(255, 255, 255, 255), width=width, joint="curve")
    r = width / 2
    for x, y in pts:
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 255))

    return bg


sizes = [16, 24, 32, 48, 64, 128, 256]
images = [render(s) for s in sizes]
images[-1].save(
    "icon.ico",
    format="ICO",
    sizes=[(s, s) for s in sizes],
)
print("Wrote icon.ico")
