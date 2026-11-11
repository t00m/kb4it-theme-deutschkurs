"""Situations and Conversations can be filtered (0.6.0, D5)."""

import re


def main(page):
    return page.split("<main", 1)[1].split("</main>", 1)[0]


def select(html, key):
    found = re.search(rf'<select class="dk-list-filter uk-select uk-form-small" data-key="{key}">(.*?)</select>', html, re.S)
    return re.findall(r'<option value="([^"]*)"', found.group(1)) if found else None


def test_situations_filter_by_topic(built_site):
    html = main(built_site.page("situations.html"))
    assert '<div class="dk-list-filters" hidden>' in html
    assert select(html, "topic") == ["", "Schule"]
    assert select(html, "level") is None
    assert re.search(r'<li class="dk-situation dk-filterable" data-topic="Schule"', html)


def test_conversations_filter_by_topic_level_and_kind(built_site):
    html = main(built_site.page("conversations.html"))
    assert "Schule" in select(html, "topic")
    assert select(html, "level")[0] == "" and "A1" in select(html, "level")
    assert "model" in select(html, "kind")
    assert re.search(r'<li class="dk-filterable" data-topic="[^"]*Schule[^"]*" data-level="A1" data-kind="model">', html)
    assert '<section class="dk-group">' in html


def test_other_lists_have_no_filters(built_site):
    for name in ("grammar.html", "texts.html", "mistakes.html"):
        assert "dk-list-filters" not in built_site.page(name), name
