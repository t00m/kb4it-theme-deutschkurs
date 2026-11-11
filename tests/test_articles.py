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
    return re.findall(r'<td><a class="dk-[mfnpl]+" href="[^"]+" lang="de">([^<]+)</a></td>', table)


def test_article_pages_exist_even_without_nouns(tmp_path):
    site = build_site(tmp_path, {"bis-morgen.md": CHUNK}, starter=False)
    for name in ("Article.html", "Article_der.html", "Article_die.html", "Article_das.html"):
        assert (site.target / name).is_file(), name
    assert "The course has no noun with this article yet." in main(site.page("Article_das.html"))


def test_der_page_lists_only_der_nouns_sorted(built_site):
    page = built_site.page("Article_der.html")
    assert words(page) == ["Ausflug", "Elternabend", "Termin"]
    assert re.search(r'<p class="dk-article-head"><span class="dk-m">der</span> 3</p>', page)


def test_die_page_has_feminine_then_plural_only(built_site):
    html = main(built_site.page("Article_die.html"))
    feminine, plural = html.split('<div class="dk-article-group uk-h3">', 2)[1:]
    assert "Brotdose" in feminine and "Lehrerin" in feminine and "Schule" in feminine and "Eltern" not in feminine
    assert "Eltern" in plural and 'class="dk-pl"' in plural
    assert "3" in feminine.split("</div>", 1)[0] and "1" in plural.split("</div>", 1)[0]


def test_article_hub_counts(built_site):
    html = main(built_site.page("Article.html"))
    for article, count in (("der", 3), ("die", 4), ("das", 2)):
        assert re.search(rf'href="Article_{article}.html"[^>]*>.*?{article}.*?</a>\s*<span class="dk-count[^"]*">{count}</span>',
                         html, re.S), article


def test_word_card_badge_links_article_page(built_site):
    assert re.search(r'<a class="dk-badge dk-article dk-m" href="Article_der.html">der</a>', built_site.page("termin.html"))
    assert re.search(r'<a class="dk-badge dk-article dk-pl" href="Article_die.html">die</a>', built_site.page("eltern.html"))


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
