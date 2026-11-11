"""Privacy and photo checks. Every sample here is made up."""

import subprocess
from pathlib import Path

import pytest
from PIL import Image

from conftest import KB4IT, build_site, prepare_site, warnings
from deutschkurs.logic.privacy import Hit, has_gps, image_path, scan

HITS = [
    ("Bitte an DE89 3704 0044 0532 0130 00 zahlen.", "iban"),
    ("IBAN: DE89370400440532013000", "iban"),
    ("Konto AT61 1904 3002 3457 3201", "iban"),
    ("Schreiben Sie an eltern.post@schule-beispiel.de bitte.", "email"),
    ("Ruf mich an: +49 30 1234567", "phone"),
    ("Telefon 030 1234567", "phone"),
    ("Handy 0176 12345678", "phone"),
    ("Wir wohnen in 10115 Berlin.", "address"),
    ("Hauptstraße 12", "address"),
    ("am Kirchweg 3a", "address"),
    ("Marktplatz 1, vorne", "address"),
]

CLEAN = [
    "Am 2026-11-09 war Elternabend.",
    "Bis zum 20.11.2026 abgeben.",
    "Wir treffen uns um 08:30 am Schultor.",
    "Siehe Seite 12.",
    "Die Wohnung kostet 10000 Euro.",
    "Wir brauchen 12345 Stück.",
    "Ich habe 40 Jahre gearbeitet.",
    "Bitte geben Sie den Zettel bei Frau A. ab: [Adresse], [IBAN].",
]


@pytest.mark.parametrize("text, reason", HITS)
def test_hit(text, reason):
    assert [h.reason for h in scan(text)] == [reason]


@pytest.mark.parametrize("text", CLEAN)
def test_no_hit(text):
    assert scan(text) == []


def test_lines_count_from_one():
    hits = scan("---\nType: Text\n---\n\nHallo\nHauptstraße 12\n")
    assert hits == [Hit("address", 6, "Hauptstraße 12")]


def test_allow_drops_a_hit():
    assert scan("Hauptstraße 12 ist die Schule.", allow=["Hauptstraße 12"]) == []
    assert len(scan("Hauptstraße 12 ist die Schule.", allow=["Bahnhofstraße 1"])) == 1


def test_image_path(tmp_path):
    assert image_path(tmp_path, "resources/photos/mein%20foto.webp") == tmp_path / "resources/photos/mein foto.webp"
    assert image_path(tmp_path, "https://example.org/a.webp") is None
    assert image_path(tmp_path, "http://example.org/a.webp") is None


def write_image(path: Path, gps: bool, fmt: str = "WEBP") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (8, 8), "yellow")
    exif = img.getexif()
    if gps:
        ifd = exif.get_ifd(0x8825)
        ifd[1] = "N"
        ifd[2] = (52.0, 31.0, 0.0)
    img.save(path, fmt, exif=exif.tobytes())
    return path


def test_has_gps(tmp_path):
    assert has_gps(write_image(tmp_path / "a.webp", gps=True)) is True
    assert has_gps(write_image(tmp_path / "b.webp", gps=False)) is False
    assert has_gps(write_image(tmp_path / "C.JPG", gps=True, fmt="JPEG")) is True


PHOTO = """---
Type: Photo
Place: Street
---

# Schild

![Schild](resources/photos/{name})

## Transcription

Baustelle betreten verboten!
"""


def run_build(config: Path) -> str:
    run = subprocess.run([KB4IT, "build", str(config)], capture_output=True, text=True)
    assert run.returncode == 0, run.stdout[-2000:] + run.stderr[-2000:]
    return (config.parent.parent / "var" / "log" / "kb4it.log").read_text(encoding="utf-8")


def test_build_reports_missing_photo(tmp_path):
    site = build_site(tmp_path, {"schild.md": PHOTO.format(name="fehlt.webp")}, starter=False)
    assert any("PHOTO_MISSING" in w and "schild" in w and "reason=missing" in w for w in warnings(site.log))


def test_build_reports_remote_photo(tmp_path):
    text = PHOTO.replace("resources/photos/{name}", "https://example.org/x.webp")
    site = build_site(tmp_path, {"schild.md": text}, starter=False)
    assert any("PHOTO_MISSING" in w and "reason=remote" in w for w in warnings(site.log))


def test_build_finds_encoded_upper_case_photo(tmp_path):
    config = prepare_site(tmp_path, {"schild.md": PHOTO.format(name="mein%20foto.JPG")}, starter=False)
    write_image(config.parent.parent / "source" / "resources" / "photos" / "mein foto.JPG", gps=True, fmt="JPEG")
    log = run_build(config)
    assert not any("PHOTO_MISSING" in w for w in warnings(log))
    assert any("PHOTO_GPS" in w and "mein foto.JPG" in w for w in warnings(log))


def test_build_reports_privacy_hit(tmp_path):
    text = "---\nType: Text\nLevel: A1\n---\n\n# Brief\n\nWir wohnen in 10115 Berlin.\n"
    site = build_site(tmp_path, {"brief.md": text}, starter=False)
    assert any("PRIVACY_SUSPECT doc=brief.md reason=address line=8" in w for w in warnings(site.log))


def test_privacy_allow_setting(tmp_path):
    text = "---\nType: Text\nLevel: A1\n---\n\n# Brief\n\nWir wohnen in 10115 Berlin.\n"
    site = build_site(tmp_path, {"brief.md": text}, settings={"privacy_allow": ["10115 Berlin"]}, starter=False)
    assert not any("PRIVACY_SUSPECT" in w for w in warnings(site.log))


def test_strict_privacy_stops_the_build(tmp_path):
    text = "---\nType: Text\nLevel: A1\n---\n\n# Brief\n\nHauptstraße 12\n"
    config = prepare_site(tmp_path, {"brief.md": text}, {"strict": True}, starter=False)
    run = subprocess.run([KB4IT, "build", str(config)], capture_output=True, text=True)
    assert run.returncode != 0
