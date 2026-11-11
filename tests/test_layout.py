"""Page layout on UIkit: local library, top bar, menu, search dialog and list components."""

import json
import re

from conftest import THEME

PAGES = ("index.html", "termin.html", "search.html", "404.html", "add.html", "vocabulary.html", "photos.html")
LINKS = ["index.html", "situations.html", "conversations.html", "texts.html", "photos.html", "mistakes.html",
         "inbox.html", "vocabulary.html", "Article.html", "verbs.html", "chunks.html", "grammar.html", "skill.html"]


def header(page):
    return re.search(r'<header class="dk-top[^"]*".*?</header>', page, re.S).group()


def test_theme_json_lists_uikit():
    theme = json.loads((THEME / "theme.json").read_text(encoding="utf-8"))
    assert "uikit" in theme["assets"]


def test_uikit_is_deployed_and_linked_locally(built_site):
    for path in ("css/uikit.min.css", "js/uikit.min.js", "js/uikit-icons.min.js"):
        assert (built_site.target / "resources/vendor/uikit" / path).is_file(), path
    for name in PAGES:
        page = built_site.page(name)
        css = page.index('href="resources/vendor/uikit/css/uikit.min.css"')
        assert css < page.index("framework/deutschkurs/deutschkurs.css"), name
        assert 'src="resources/vendor/uikit/js/uikit.min.js"' in page, name
        assert 'src="resources/vendor/uikit/js/uikit-icons.min.js"' in page, name


def test_top_bar_is_a_sticky_uikit_navbar(built_site):
    top = header(built_site.page("termin.html"))
    assert "data-uk-sticky" in top
    assert re.search(r'<nav class="dk-bar uk-navbar-container[^"]*" data-uk-navbar', top)
    assert re.search(r'<a class="dk-brand[^"]*" href="index.html"[^>]*><img [^>]*width="24" height="24"', top)


def test_bar_and_phone_menu_list_every_page_in_order(built_site):
    for name in PAGES:
        page = built_site.page(name)
        bar = re.search(r'<ul class="dk-nav uk-navbar-nav uk-visible@m">.*?<div class="uk-navbar-right">', page, re.S).group()
        assert re.findall(r'href="([^"]+\.html)"', bar) == LINKS, name
        menu = re.search(r'<div id="dk-menu" data-uk-offcanvas[^>]*>.*?</ul>', page, re.S).group()
        assert re.findall(r'href="([^"]+\.html)"', menu) == LINKS, name
        assert 'href="#dk-menu"' in header(page), name


def test_bar_groups_have_label_overrides(tmp_path):
    from conftest import build_site
    site = build_site(tmp_path, settings={"labels": {"menu_life": "Mi vida", "menu_course": "Curso"}})
    top = header(site.page("index.html"))
    assert "Mi vida" in top and "Curso" in top


def test_search_opens_in_a_dialog(built_site):
    page = built_site.page("termin.html")
    assert 'href="#dk-search" data-uk-toggle' in header(page)
    dialog = re.search(r'<div id="dk-search" data-uk-modal>.*?</div>\s*</div>', page, re.S).group()
    assert 'id="kb4it-search-input"' in dialog


def test_content_sits_in_a_container_and_card(built_site):
    for name in ("index.html", "termin.html", "vocabulary.html", "404.html"):
        page = built_site.page(name)
        assert re.search(r'<main class="dk-main[^"]* uk-container uk-container-small"', page), name
        assert "uk-card uk-card-default" in page.split("<main", 1)[1], name


def test_lists_use_uikit_components(built_site):
    vocabulary = built_site.page("vocabulary.html")
    assert re.search(r'<table id="dk-table" class="dk-table uk-table[^"]*"', vocabulary)
    assert 'class="dk-filter uk-input uk-form-small' in vocabulary
    assert 'class="dk-filter-select uk-select uk-form-small' in vocabulary
    home = built_site.page("index.html")
    assert re.search(r'<a class="dk-tile uk-card uk-card-default[^"]*" href="vocabulary.html"', home)
    photos = built_site.page("photos.html")
    assert re.search(r'<ul class="dk-photos uk-grid-small[^"]*" data-uk-grid', photos)


def test_buttons_use_uikit(built_site):
    termin = built_site.page("termin.html")
    assert re.search(r'<button type="button" class="dk-listen uk-button uk-button-default uk-button-small"', termin)


def test_footer_closes_the_page_wrapper(built_site):
    page = built_site.page("termin.html")
    assert page.count('<div class="dk-page') == 1
    tail = page.split('<footer', 1)[1]
    assert tail.index("</footer>") < tail.index("</div>") < tail.index("</body>")


def test_add_page_cards_use_uikit(built_site):
    add = built_site.page("add.html")
    assert add.count('class="uk-card uk-card-default uk-card-hover uk-card-small kb-add-card"') == 11
    assert 'data-kb-open="photo"' in add


def test_search_keys_script_is_loaded(built_site):
    page = built_site.page("termin.html")
    assert page.index("deutschkurs/ui.js") > page.index("</footer>")
    assert (built_site.target / "resources/themes/deutschkurs/framework/deutschkurs/ui.js").is_file()
