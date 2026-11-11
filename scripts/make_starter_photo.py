"""Draw the starter photo: a yellow building site sign, made by code, no camera and no EXIF data.

Usage: python3 scripts/make_starter_photo.py [output.webp]
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

DEFAULT = Path(__file__).resolve().parent.parent / "deutschkurs" / "apps" / "default" / "source" / "resources" \
    / "photos" / "2026-11-09-baustelle.webp"
SIZE = (640, 400)
LINES = ("Baustelle", "betreten verboten!", "Eltern haften für ihre Kinder.")


# Fonts with German letters; Pillow's own font has no umlauts and is the last resort.
FONTS = ("DejaVuSans.ttf", "LiberationSans-Regular.ttf", "/usr/share/fonts/liberation-sans-fonts/LiberationSans-Regular.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "Arial.ttf")


def font(size: int):
    for name in FONTS:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def draw(path: Path) -> None:
    img = Image.new("RGB", SIZE, "#8fa3b0")
    pen = ImageDraw.Draw(img)
    pen.rectangle((60, 40, 580, 360), fill="#f5c400", outline="#222222", width=8)
    for n, (text, size) in enumerate(zip(LINES, (56, 40, 28))):
        y = 80 + n * 90
        width = pen.textlength(text, font=font(size))
        pen.text(((SIZE[0] - width) / 2, y), text, fill="#111111", font=font(size))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "WEBP", quality=80)


if __name__ == "__main__":
    draw(Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT)
