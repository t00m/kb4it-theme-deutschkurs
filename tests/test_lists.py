import json
import re

import pytest

from conftest import build_site, warnings
from test_pages import ANRUFEN, BUTTERBROT, DATIV, HELFEN, TALK, TERMIN

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
    return build_site(tmp_path_factory.mktemp("lists"), EXTRA, starter=False)


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
    site = build_site(tmp_path, {"vocabulary.md": TERMIN, "kind.md": KIND}, starter=False)
    assert any("DOC_NAME_RESERVED" in line and "vocabulary.md" in line for line in warnings(site.log))
    assert 'class="dk-row"' in site.page("vocabulary.html")


INDEX = """---
Topic: Schule
---

# Willkommen

Mein eigener Startseitentext.
"""


def test_own_index_replaces_home(tmp_path):
    site = build_site(tmp_path, {"index.md": INDEX, "kind.md": KIND}, starter=False)
    assert "Mein eigener Startseitentext." in site.page("index.html")


def test_facet_page_names_reserved(tmp_path):
    names = ("Topic.md", "Level.md", "Register.md", "ConversationKind.md", "Genre.md")
    site = build_site(tmp_path, {**{name: INDEX for name in names}, "kind.md": KIND}, starter=False)
    log = "\\n".join(warnings(site.log))
    assert "kind.md" not in log
    for name in names:
        assert f"DOC_NAME_RESERVED doc={name}" in log or f'DOC_NAME_RESERVED doc="{name}"' in log, name


def test_facet_value_names_warned(tmp_path):
    site = build_site(tmp_path, {"Level_A1.md": INDEX, "kind.md": KIND}, starter=False)
    assert any("PAGE_NAME_TAKEN doc=Level_A1.md" in line for line in warnings(site.log))


def test_page_name_that_differs_only_by_case_is_warned(tmp_path):
    genre = KIND.replace("# Kind", "# Genre").replace("die Kinder", "die Genres")
    site = build_site(tmp_path, {"genre.md": genre, "kind.md": KIND}, starter=False)
    log = warnings(site.log)
    assert any("PAGE_NAME_TAKEN doc=genre.md" in line for line in log)
    assert not any("kind.md" in line for line in log)


ARZT = """---
Kind: real
Level: A2
Type: Conversation
---

# Beim Arzt

- **Arzt:** Guten Tag! :: Good day!
- **ich:** Guten Tag!
"""

ZETTEL = """---
Level: A1
Type: Text
---

# Zettel im Flur

Bitte Schuhe ausziehen.
"""

SPIELPLATZ = """---
Type: Situation
---

# Auf dem Spielplatz
"""

LATE = """---
Deadline: 2026-12-01
Genre: Notice
Level: A1
Type: Text
---

# Aushang

Der Termin ist neu.
"""


@pytest.fixture(scope="module")
def talk(tmp_path_factory):
    extra = {**TALK, "beim-arzt.md": ARZT, "zettel.md": ZETTEL, "spielplatz.md": SPIELPLATZ, "aushang.md": LATE}
    return build_site(tmp_path_factory.mktemp("talk-lists"), extra, starter=False)


def cards(html):
    return re.findall(r'<li class="dk-situation">.*?</li>', html, re.S)


def test_situations_page_has_a_card_per_situation(talk):
    found = cards(main(talk.page("situations.html")))
    assert len(found) == 2
    tor = next(c for c in found if 'href="am-schultor.html"' in c)
    assert "<dt>I can</dt><dd>1 / 2</dd>" in tor
    assert "<dt>Next time</dt><dd>2026-11-10</dd>" in tor
    assert "<dt>Conversations</dt><dd>1</dd>" in tor
    assert "<dt>Texts</dt><dd>1</dd>" in tor
    assert "<dt>Chunks</dt><dd>0</dd>" in tor
    assert "<dt>Vocabulary</dt><dd>1</dd>" in tor


def test_situation_card_without_tasks_or_date_leaves_them_out(talk):
    platz = next(c for c in cards(main(talk.page("situations.html"))) if 'href="spielplatz.html"' in c)
    assert "I can" not in platz and "Next time" not in platz
    assert "<dt>Conversations</dt><dd>0</dd>" in platz


def test_conversations_are_grouped_by_situation(talk):
    html = main(talk.page("conversations.html"))
    assert html.index('<h2><a href="am-schultor.html" lang="de">Am Schultor</a></h2>') < html.index('href="gruss.html"')
    assert html.index('href="gruss.html"') < html.index("<h2>No situation</h2>") < html.index('href="beim-arzt.html"')
    gruss = re.search(r'<li>(?:(?!</li>).)*href="gruss.html".*?</li>', html, re.S).group()
    assert 'class="dk-badge dk-kind dk-kind-model">model<' in gruss
    assert 'class="dk-badge dk-level">A1<' in gruss
    assert "70 %" in gruss


def test_texts_are_grouped_by_genre(talk):
    html = main(talk.page("texts.html"))
    assert html.index("<h2>School letter</h2>") < html.index('href="brief.html"') < html.index("<h2>Notice</h2>")
    assert html.index("<h2>Other</h2>") < html.index('href="zettel.html"')
    brief = re.search(r'<li>(?:(?!</li>).)*href="brief.html".*?</li>', html, re.S).group()
    assert 'class="dk-badge dk-level">A2<' in brief
    assert "57 %" in brief
    assert 'data-date="2026-11-20" data-hide="past"' in brief and "Deadline: " in brief
    zettel = re.search(r'<li>(?:(?!</li>).)*href="zettel.html".*?</li>', html, re.S).group()
    assert "data-date" not in zettel


def test_home_counts_the_new_lists(talk):
    html = main(talk.page("index.html"))
    assert re.search(r'href="situations.html"[^>]*>\s*<span class="dk-count">2</span>', html)
    assert re.search(r'href="conversations.html"[^>]*>\s*<span class="dk-count">2</span>', html)
    assert re.search(r'href="texts.html"[^>]*>\s*<span class="dk-count">3</span>', html)
    assert html.index('href="situations.html"') < html.index('href="vocabulary.html"')


def test_home_lists_coming_up_situations(talk):
    html = main(talk.page("index.html"))
    block = re.search(r'<section class="dk-dated dk-coming-up">.*?</section>', html, re.S).group()
    assert "<h2>Coming up</h2>" in block
    items = re.findall(r"<li.*?</li>", block, re.S)
    assert len(items) == 1
    assert 'data-date="2026-11-10" data-days="7" data-hide="past later"' in items[0]
    assert 'href="am-schultor.html"' in items[0] and "2026-11-10" in items[0]


def test_home_lists_deadlines_soonest_first(talk):
    html = main(talk.page("index.html"))
    block = re.search(r'<section class="dk-dated dk-deadlines">.*?</section>', html, re.S).group()
    assert "<h2>Open deadlines</h2>" in block
    items = re.findall(r"<li.*?</li>", block, re.S)
    assert ['data-date="2026-11-20" data-hide="past"' in items[0], 'href="brief.html"' in items[0]] == [True, True]
    assert 'data-date="2026-12-01"' in items[1] and 'href="aushang.html"' in items[1]
    assert len(items) == 2


def test_home_without_dates_has_no_dated_blocks(site):
    assert "dk-dated" not in main(site.page("index.html"))


def test_new_lists_exist_when_empty(site):
    for name in ("situations.html", "conversations.html", "texts.html", "photos.html", "mistakes.html", "inbox.html"):
        assert "<main" in site.page(name)


SOON = """---
NextTime: 2026-11-10
Type: Situation
---

# Beim Arzt
"""


def test_prepare_days_sets_the_coming_up_window(tmp_path):
    site = build_site(tmp_path, {"situation-arzt.md": SOON}, settings={"prepare_days": 3}, starter=False)
    assert 'data-date="2026-11-10" data-days="3" data-hide="past later"' in main(site.page("index.html"))
    assert 'data-date="2026-11-10" data-days="3" data-hide="past later"' in site.page("situation-arzt.html")


@pytest.mark.parametrize("value", [-1, True, "soon", 2.5])
def test_prepare_days_that_is_no_number_of_days_falls_back(value):
    from deutschkurs.logic.theme import whole_days
    assert whole_days(value) == 7
    assert whole_days(0) == 0
