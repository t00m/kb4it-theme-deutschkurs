from pathlib import Path
"""Article pages: one page per article with every noun that takes it."""

import re

import pytest

from conftest import build_site, warnings

CHUNK = """---
Level: A1
Translation: see you tomorrow
Type: Chunk
---

# bis morgen
"""

TAKEN = """---
Level: A1
Translation: x
Type: Chunk
---

# Article der
"""


def main(page):
    return page.split("<main", 1)[1].split("</main>", 1)[0]


def words(page):
    """Linked words of the article table, in order."""
    table = page.split('<table id="dk-table"', 1)[1].split("</table>", 1)[0]
    return re.findall(r'<td><a class="dk-[mfnpl]+ dk-cued" href="[^"]+" lang="de">([^<]+)</a></td>', table)


def test_article_pages_exist_even_without_nouns(tmp_path):
    site = build_site(tmp_path, {"bis-morgen.md": CHUNK}, starter=False)
    for name in ("Article.html", "Article_der.html", "Article_die.html", "Article_das.html"):
        assert (site.target / name).is_file(), name
    assert "The course has no noun with this article yet." in main(site.page("Article_das.html"))


def test_der_page_lists_only_der_nouns_sorted(built_site):
    page = built_site.page("Article_der.html")
    assert words(page) == ["Ausflug", "Elternabend", "Termin"]
    assert re.search(r'<p class="dk-article-head"><span class="dk-m dk-cued">der</span> 3</p>', page)


def test_die_page_has_feminine_then_plural_only(built_site):
    html = main(built_site.page("Article_die.html"))
    feminine, plural = html.split('<div class="dk-article-group uk-h3">', 2)[1:]
    assert "Brotdose" in feminine and "Lehrerin" in feminine and "Schule" in feminine and "Eltern" not in feminine
    assert "Eltern" in plural and 'class="dk-pl dk-cued"' in plural
    assert "3" in feminine.split("</div>", 1)[0] and "1" in plural.split("</div>", 1)[0]


def test_article_hub_counts(built_site):
    html = main(built_site.page("Article.html"))
    for article, count in (("der", 3), ("die", 4), ("das", 2)):
        assert re.search(rf'href="Article_{article}.html"[^>]*>.*?{article}.*?</a>\s*<span class="dk-count[^"]*">{count}</span>',
                         html, re.S), article


def test_word_card_badge_links_article_page(built_site):
    assert re.search(r'<a class="dk-badge dk-article dk-m dk-cued" href="Article_der.html">der</a>', built_site.page("termin.html"))
    assert re.search(r'<a class="dk-badge dk-article dk-pl dk-cued" href="Article_die.html">die</a>', built_site.page("eltern.html"))


def test_vocabulary_links_three_articles(built_site):
    html = main(built_site.page("vocabulary.html"))
    links = re.search(r'<p class="dk-articles">.*?</p>', html, re.S).group()
    assert re.findall(r'href="([^"]+)"', links) == ["Article_der.html", "Article_die.html", "Article_das.html"]
    assert html.index('class="dk-articles"') < html.index('id="dk-table"')
    assert re.search(r'<td><a class="dk-m" href="Article_der.html" lang="de">der</a></td>', html)


def test_article_md_reserved_and_prefix_taken(tmp_path):
    site = build_site(tmp_path, {"Article_der_x.md": TAKEN}, starter=False)
    assert any("PAGE_NAME_TAKEN doc=Article_der_x.md" in line for line in warnings(site.log))
    from deutschkurs.logic.theme import Theme
    assert "Article.md" in Theme.reserved_pages


def test_articles_not_linked_in_sentences(built_site):
    body = main(built_site.page("termin.html")).split('class="dk-body', 1)[1]
    assert "Article_" not in body


def test_article_pages_not_in_search(built_site):
    index = (built_site.target / "search-index.js").read_text(encoding="utf-8")
    assert "Article_der" not in index


TWO_TOPICS = """---
Article: das
Checked: assistant
Level: A1
PartOfSpeech: noun
Plural: die Kinder
Topic: Familie, Schule
Translation: child
Type: Word
---

# Kind
"""


def test_topic_filter_lists_single_topics(tmp_path):
    site = build_site(tmp_path, {"kind.md": TWO_TOPICS}, starter=False)
    html = main(site.page("Article_das.html"))
    topic = re.search(r'<select[^>]*data-column="4".*?</select>', html, re.S).group()
    assert re.findall(r'<option value="([^"]*)">', topic) == ["", "Familie", "Schule"]


def test_cue_in_cards_and_tables(built_site):
    termin = main(built_site.page("termin.html"))
    assert re.search(r"<h1 class=\"dk-headline dk-m dk-cued[ \"]", termin)
    assert re.search(r'<dd class="dk-pl dk-cued">die Termine</dd>', termin)
    vocabulary = main(built_site.page("vocabulary.html"))
    assert '<a class="dk-m dk-cued" href="termin.html" lang="de">Termin</a>' in vocabulary
    assert '<td class="dk-pl dk-cued">die Termine</td>' in vocabulary
    der = main(built_site.page("Article_der.html"))
    assert '<a class="dk-m dk-cued" href="termin.html" lang="de">Termin</a>' in der
    assert '<td class="dk-pl dk-cued">die Termine</td>' in der


def test_cue_css_covers_every_gender():
    css = (Path(__file__).resolve().parent.parent / "deutschkurs" / "framework" / "deutschkurs" / "deutschkurs.css").read_text()
    for g in ("m", "f", "n", "pl"):
        assert f'.dk-cued.dk-{g}::after' in css, g


def test_vocabulary_links_level_and_part_of_speech(built_site):
    vocabulary = main(built_site.page("vocabulary.html"))
    row = re.search(r'<tr class="dk-row">\s*<td[^>]*>.*?href="termin.html".*?</tr>', vocabulary, re.S).group()
    assert '<td><a href="Level_A1.html">A1</a></td>' in row
    assert '<td><a href="PartOfSpeech_noun.html">noun</a></td>' in row


def test_part_of_speech_pages(built_site):
    assert 'href="PartOfSpeech_noun.html"' in main(built_site.page("PartOfSpeech.html"))
    nouns = main(built_site.page("PartOfSpeech_noun.html"))
    assert 'href="termin.html"' in nouns and 'href="krank.html"' not in nouns
    assert "Part of speech: noun" in built_site.page("PartOfSpeech_noun.html")


def test_verb_and_chunk_tables_link_the_level(built_site):
    for name in ("verbs.html", "chunks.html"):
        assert re.search(r'<td><a href="Level_A[12].html">A[12]</a></td>', main(built_site.page(name))), name


def test_word_page_links_its_part_of_speech(built_site):
    assert re.search(r'<dt>Part of speech</dt><dd><a href="PartOfSpeech_noun.html">noun</a></dd>',
                     main(built_site.page("termin.html")))
    assert re.search(r'<dt>Part of speech</dt><dd><a href="PartOfSpeech_preposition.html">preposition</a></dd>',
                     main(built_site.page("mit.html")))
