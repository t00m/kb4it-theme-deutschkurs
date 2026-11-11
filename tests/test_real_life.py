"""Entry pages of Photo, Mistake, Gap and Inbox, and the cue for unchecked facts."""

import re
import subprocess

import pytest
from PIL import Image

from conftest import KB4IT, BuiltSite, prepare_site, warnings
from test_pages import TERMIN, main

SCHILD = """---
Checked: native
Place: Street
Type: Photo
---

# Termin am Schild

![A sign](resources/photos/schild.webp)

## Transcription

Termin nur heute!

Bitte klingeln.

## Meaning

Appointment only today. Please ring.
"""

GRAMMAR = """---
Area: Verbs
Level: A1
Pattern: es-tener-haben
Type: Grammar
---

# Alter mit sein

## Explanation

Age takes *sein*.
"""

MISTAKE = """---
Date: 2026-11-05
Level: A1
Pattern: es-tener-haben
Type: Mistake
---

# Ich habe 40 Jahre

## Wrong

Ich habe 40 Jahre.

## Right

Ich bin 40 Jahre alt.

## Why

Age takes *sein*.
"""

GAP = """---
Date: 2026-11-09
Type: Gap
---

# Krank melden

## I wanted to say

My son is sick today.

## In German

"""

INBOX = """---
Type: Inbox
---

# Inbox November

- 2026-11-09 Kaution | Vermieter hat gesagt
- Termine
"""

OLDER = MISTAKE.replace("2026-11-05", "2026-10-01").replace("# Ich habe 40 Jahre", "# Ich habe Hunger nicht")
LOOSE = MISTAKE.replace("Pattern: es-tener-haben\n", "").replace("# Ich habe 40 Jahre", "# Ich gehe zu Hause")

FILES = {"termin.md": TERMIN, "schild.md": SCHILD, "alter.md": GRAMMAR, "mistake-alter.md": MISTAKE,
         "mistake-older.md": OLDER, "mistake-loose.md": LOOSE, "gap-krank.md": GAP, "inbox-2026-11.md": INBOX}


@pytest.fixture(scope="module")
def life(tmp_path_factory) -> BuiltSite:
    config = prepare_site(tmp_path_factory.mktemp("life"), FILES, starter=False)
    root = config.parent.parent
    photos = root / "source" / "resources" / "photos"
    photos.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (8, 8), "yellow").save(photos / "schild.webp", "WEBP")
    run = subprocess.run([KB4IT, "build", str(config)], capture_output=True, text=True)
    assert run.returncode == 0, run.stdout[-2000:]
    return BuiltSite(root, root / "target", (root / "var" / "log" / "kb4it.log").read_text(encoding="utf-8"))


def test_no_warnings(life):
    assert warnings(life.log) == []


def test_photo_paragraphs_get_anchors(life):
    html = main(life.page("schild.html"))
    assert re.search(r'<p id="p1" class="dk-sentence"><span class="dk-de" lang="de">.*?Termin</a> nur heute!</span>',
                     html)
    assert 'id="p2"' in html


def test_photo_image_is_lazy(life):
    html = main(life.page("schild.html"))
    assert re.search(r'<img [^>]*src="resources/photos/schild.webp"[^>]*loading="lazy"|'
                     r'<img [^>]*loading="lazy"[^>]*src="resources/photos/schild.webp"', html)
    assert (life.target / "resources" / "photos" / "schild.webp").is_file()


def test_photo_card_shows_place(life):
    assert 'href="Place_Street.html"' in main(life.page("schild.html"))


def test_word_page_lists_photo_sentence(life):
    html = main(life.page("termin.html"))
    assert 'href="schild.html#p1"' in html


def test_mistake_sections_marked(life):
    html = main(life.page("mistake-alter.html"))
    assert 'class="kb-sect1 dk-mistake-wrong"' in html
    assert 'class="kb-sect1 dk-mistake-right"' in html


def test_mistake_card_links_grammar_by_pattern(life):
    html = main(life.page("mistake-alter.html"))
    assert 'href="alter.html"' in html
    assert 'href="Pattern_es-tener-haben.html"' in html


def test_gap_card_says_to_process(life):
    assert "To process" in main(life.page("gap-krank.html"))


def test_unchecked_translation_is_marked(life):
    html = main(life.page("termin.html"))
    assert re.search(r'<p class="dk-translation dk-unverified"[^>]*title="[^"]+"', html)
    assert re.search(r'<h1 class="dk-headline [^"]*dk-unverified', html)


def test_native_translation_is_not_marked(life):
    assert "dk-unverified" not in main(life.page("schild.html"))


def test_inbox_not_in_search(life):
    index = next(life.target.rglob("search*.js"), None) or next(life.target.rglob("*search*.json"))
    assert "inbox-2026-11" not in index.read_text(encoding="utf-8")


def test_inbox_page_links_inbox_list(life):
    html = main(life.page("inbox-2026-11.html"))
    assert 'href="inbox.html"' in html


def test_gallery_uses_relative_lazy_images(life):
    html = main(life.page("photos.html"))
    assert '<a class="dk-photo" href="schild.html"' in html
    assert '<img loading="lazy" src="resources/photos/schild.webp" alt="Termin am Schild">' in html


def test_gallery_images_exist_in_target(life):
    html = life.page("photos.html")
    for src in re.findall(r'<img loading="lazy" src="([^"]+)"', html):
        assert (life.target / src).is_file(), src


def test_gallery_shows_all_without_js(life):
    html = main(life.page("photos.html"))
    assert re.search(r'<li class="dk-photo-item" data-place="Street" data-situation="">', html)
    assert "<li class=\"dk-photo-item\" hidden" not in html
    assert re.search(r'<div class="dk-gallery-filters" hidden>', html)


def test_mistakes_grouped_by_pattern_newest_first(life):
    html = main(life.page("mistakes.html"))
    assert html.index("Ich habe 40 Jahre") < html.index("Ich habe Hunger nicht") < html.index("No pattern") \
        < html.index("Ich gehe zu Hause")
    assert 'href="alter.html"' in html.split("No pattern")[0]


def test_inbox_lists_items_and_open_gaps(life):
    html = main(life.page("inbox.html"))
    for text in ("Kaution", "Termine", "Krank melden"):
        assert text in html


def test_inbox_undated_item_is_last(life):
    html = main(life.page("inbox.html"))
    assert html.index("Termine") > max(html.index("Kaution"), html.index("Krank melden"))


def test_inbox_marks_known_word(life):
    html = main(life.page("inbox.html"))
    item = html[html.index("Termine"):]
    assert "already in the course" in item[:400] and 'href="termin.html"' in item[:400]


def test_home_shows_inbox_count(life):
    html = main(life.page("index.html"))
    assert '<a href="inbox.html">Inbox: 3 to process</a>' in html


def test_place_and_pattern_facets(life):
    assert "schild.html" in main(life.page("Place_Street.html"))
    pattern = main(life.page("Pattern_es-tener-haben.html"))
    assert "mistake-alter.html" in pattern and "alter.html" in pattern


def test_list_translation_marked_unverified(life):
    html = main(life.page("vocabulary.html"))
    assert re.search(r'<td class="[^"]*dk-unverified[^"]*"[^>]*>cita</td>', html)


def test_nav_links_photos_and_home_links_mistakes_and_inbox(life):
    page = life.page("termin.html")
    assert '<a href="photos.html">' in page
    for name in ("mistakes.html", "inbox.html"):
        assert f'href="{name}"' not in page
    home = life.page("index.html")
    assert 'href="mistakes.html"' in home
