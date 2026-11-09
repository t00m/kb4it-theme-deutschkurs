import json
import re

import pytest

from conftest import build_site, warnings
from test_pages import ANRUFEN, BUTTERBROT, DATIV, HELFEN, TERMIN

KIND = """---
Article: das
Level: A1
PartOfSpeech: noun
Plural: die Kinder
Topic: Schule
Translation: niño
Type: Word
---

# Kind
"""

AERGER = """---
Article: der
Level: A2
PartOfSpeech: noun
Plural: none
Translation: enfado
Type: Word
---

# Ärger
"""

WIE_GEHTS = """---
Level: A1
Register: colloquial
Translation: ¿qué tal?
Type: Chunk
---

# Wie geht's?
"""

PERFEKT = """---
Area: Verbs
Level: A2
Tense: Perfekt
Type: Grammar
---

# Perfekt

## Explanation

Pasado hablado.
"""

EXTRA = {"termin.md": TERMIN, "butterbrot.md": BUTTERBROT, "anrufen.md": ANRUFEN, "helfen.md": HELFEN,
         "dativ.md": DATIV, "kind.md": KIND, "aerger.md": AERGER, "wie-gehts.md": WIE_GEHTS,
         "perfekt.md": PERFEKT}


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    return build_site(tmp_path_factory.mktemp("lists"), EXTRA)


def main(page):
    return page.split("<main", 1)[1].split("</main>", 1)[0]


def rows(html):
    return re.findall(r"<tr class=\"dk-row\".*?</tr>", html, re.S)


def test_no_warnings(site):
    assert warnings(site.log) == []


def test_vocabulary_table(site):
    html = main(site.page("vocabulary.html"))
    found = rows(html)
    assert len(found) == 4
    titles = [re.search(r'href="[^"]+"[^>]*>([^<]+)</a>', r).group(1) for r in found]
    assert titles == ["Ärger", "Butterbrot", "Kind", "Termin"]
    kind = found[2]
    assert "das" in kind and "die Kinder" in kind and "niño" in kind and "A1" in kind
    assert 'href="kind.html"' in kind


def test_vocabulary_escapes_translation(site):
    html = site.page("vocabulary.html")
    assert "&lt;casero&gt;" in html and "<casero>" not in html


def test_verbs_table(site):
    found = rows(main(site.page("verbs.html")))
    anrufen = next(r for r in found if 'href="anrufen.html"' in r)
    assert "hat angerufen" in anrufen
    assert "an-" in anrufen


def test_chunks_table(site):
    found = rows(main(site.page("chunks.html")))
    assert len(found) == 1
    assert "colloquial" in found[0] and "¿qué tal?" in found[0]


def test_grammar_by_area(site):
    html = main(site.page("grammar.html"))
    assert html.index(">Cases<") < html.index('href="dativ.html"')
    assert html.index(">Verbs<") < html.index('href="perfekt.html"')


def test_facets(site):
    html = main(site.page("Level.html"))
    assert 'href="Level_A1.html"' in html and 'href="Level_A2.html"' in html
    a1 = main(site.page("Level_A1.html"))
    assert 'href="kind.html"' in a1 and 'href="perfekt.html"' not in a1
    assert 'href="kind.html"' in main(site.page("Topic_Schule.html"))
    assert 'href="wie-gehts.html"' in main(site.page("Register_colloquial.html"))


def test_card_links_to_facets(site):
    html = main(site.page("kind.html"))
    assert 'href="Level_A1.html"' in html
    assert 'href="Topic_Schule.html"' in html


def test_nav(site):
    for name in ("index.html", "termin.html", "search.html", "404.html"):
        nav = re.search(r'<nav class="dk-nav">.*?</nav>', site.page(name), re.S).group()
        for href in ("index.html", "vocabulary.html", "verbs.html", "chunks.html", "grammar.html"):
            assert f'href="{href}"' in nav, (name, href)


def test_home(site):
    html = main(site.page("index.html"))
    assert re.search(r'href="vocabulary.html"[^>]*>\s*<span class="dk-count">4</span>', html)
    assert re.search(r'href="verbs.html"[^>]*>\s*<span class="dk-count">2</span>', html)


def test_search_record(site):
    text = (site.target / "search-index.js").read_text(encoding="utf-8")
    records = json.loads(text[text.index("=") + 1:].strip().rstrip(";"))
    termin = next(r for r in records if r["u"] == "termin.html")
    assert termin["f"] == {"Type": ["Word"], "Level": ["A1"], "Article": ["der"]}
    assert termin["s"] == "cita"


def test_reserved_name_refused(tmp_path):
    site = build_site(tmp_path, {"vocabulary.md": TERMIN})
    assert "vocabulary" in "\n".join(warnings(site.log))
    assert 'class="dk-row"' in site.page("vocabulary.html")
