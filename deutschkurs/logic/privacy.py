"""Privacy checks: personal data in the source text, and location data in photos."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence
from urllib.parse import unquote

# Capitalised words after five digits that name an amount, not a town.
UNITS = ("Euro", "EUR", "Cent", "Stück", "Meter", "Kilometer", "Jahre", "Tage", "Stunden", "Minuten")
STREETS = r"(?:straße|strasse|str\.|weg|platz|gasse|allee|ring|damm|ufer)"

PATTERNS = (
    ("iban", re.compile(r"\b[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){2,7}(?: ?[A-Z0-9]{1,4})?\b")),
    ("email", re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}\b")),
    # +49 or a 0 and an area code of 2 to 5 digits, then at least 5 more digits.
    ("phone", re.compile(r"(?<![\w.:-])(?:\+49[ /-]?\d{2,5}|0\d{2,5})[ /-]?\d{2,4}[ -]?\d{2,6}(?![\w.:-])")),
    ("address", re.compile(rf"\b\d{{5}} (?!(?:{'|'.join(UNITS)})\b)[A-ZÄÖÜ][a-zäöüß]+")),
    ("address", re.compile(rf"\b[A-ZÄÖÜ][a-zäöüß-]*{STREETS} \d{{1,4}}[a-z]?\b")),
)

GPS_IFD = 0x8825
PHOTO_SUFFIXES = (".jpg", ".jpeg", ".webp")


@dataclass(frozen=True)
class Hit:
    reason: str
    line: int
    text: str


def scan(text: str, allow: Sequence[str] = ()) -> list[Hit]:
    """Suspected personal data, one Hit per match, lines counted from 1; hits containing an allowed string are dropped."""
    hits = []
    for n, line in enumerate(text.splitlines(), start=1):
        # A span already claimed by an earlier pattern (a phone number inside an IBAN) is not a second hit.
        taken: list[tuple[int, int]] = []
        for reason, pattern in PATTERNS:
            for match in pattern.finditer(line):
                found = match.group(0)
                if reason == "iban" and not any(c.isdigit() for c in found[4:]):
                    continue
                if any(match.start() < end and start < match.end() for start, end in taken):
                    continue
                taken.append(match.span())
                if not any(a and a in found for a in allow):
                    hits.append(Hit(reason, n, found))
    return hits


def image_path(source_dir: Path, src: str) -> Optional[Path]:
    """The file an image src points to inside the source folder, or None for a remote image."""
    if src.startswith(("http://", "https://", "//")):
        return None
    return source_dir / unquote(src)


def has_gps(path: Path) -> Optional[bool]:
    """True when the image holds GPS data, None when Pillow is missing."""
    try:
        from PIL import Image
    except ImportError:
        return None
    with Image.open(path) as img:
        return bool(img.getexif().get_ifd(GPS_IFD))


def photo_files(source_dir: Path) -> list[Path]:
    """Images under source/resources/photos/ that can hold EXIF data."""
    folder = source_dir / "resources" / "photos"
    if not folder.is_dir():
        return []
    return sorted(p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in PHOTO_SUFFIXES)
