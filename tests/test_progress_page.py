"""The Progress page: parts known at build time in HTML, the rest filled in by progress.js."""

import re

import pytest

from conftest import build_site

ARZT = """---
Type: Situation
---

# Beim Arzt

## I can

- [x] Ich kann einen Termin machen.
- [x] Ich kann sagen, was weh tut.
- [ ] Ich kann ein Rezept holen.

## Log

- 2026-11-02 Ich habe einen Termin gemacht.
- 2026-11-09 Ich habe alles verstanden.
- Ohne Datum geschafft.
"""

SCHULE = """---
Type: Situation
---

# Schule

## Log

- 2026-11-05 Ich habe mit der Lehrerin gesprochen.
"""

ROH = """---
Level: A1
PartOfSpeech: adjective
Translation: raw
Type: Word
---

# roh

## Examples

- Das ist roh. :: That is raw.
"""

LEER = """---
Checked: assistant
Level: A1
PartOfSpeech: adjective
Translation: empty
Type: Word
---

# leer
"""


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    return build_site(tmp_path_factory.mktemp("progress"),
                      {"arzt.md": ARZT, "schule.md": SCHULE, "roh.md": ROH, "leer.md": LEER}, starter=False)


def main(page):
    return page.split("<main", 1)[1].split("</main>", 1)[0]


def test_progress_lists_wins_newest_first(site):
    wins = re.search(r'<ul class="dk-wins[^"]*">.*?</ul>', main(site.page("progress.html")), re.S).group()
    texts = re.findall(r'<span class="dk-win-text" lang="de">([^<]+)</span>', wins)
    assert texts == ["Ich habe alles verstanden.", "Ich habe mit der Lehrerin gesprochen.",
                     "Ich habe einen Termin gemacht.", "Ohne Datum geschafft."]
    assert 'href="arzt.html"' in wins and 'href="schule.html"' in wins


def test_progress_cando_per_situation(site):
    html = main(site.page("progress.html"))
    row = re.search(r'<li class="dk-cando">\s*<a href="arzt.html"[^>]*>Beim Arzt</a>.*?</li>', html, re.S).group()
    assert "2 / 3" in row and '<progress class="uk-progress" value="2" max="3">' in row
    assert 'href="schule.html"' not in re.search(r'<ul class="dk-candos[^"]*">.*?</ul>', html, re.S).group()


def test_progress_not_ready_lists_unchecked_and_without_sentence(site):
    html = main(site.page("progress.html"))
    block = re.search(r'<ul class="dk-not-ready[^"]*">.*?</ul>', html, re.S).group()
    assert re.search(r'href="roh.html"[^>]*>roh</a>\s*<span class="dk-note">Checked: unchecked</span>', block)
    assert re.search(r'href="leer.html"[^>]*>leer</a>\s*<span class="dk-note">No example sentence</span>', block)


def test_progress_works_without_js(site):
    html = main(site.page("progress.html"))
    for block in ('id="dk-known"', 'id="dk-patterns"', 'id="dk-calendar"'):
        assert block in html, block
    assert "framework/deutschkurs/progress.js" in html
    assert "<noscript>" in html


def test_today_block_links_progress(built_site):
    today = re.search(r'<section class="dk-today[^"]*".*?</section>', built_site.page("index.html"), re.S).group()
    assert 'href="progress.html"' in today
