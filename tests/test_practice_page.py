"""The Practice page, the Prepare button and the Today block of the home page."""

import json
import re

from conftest import build_site

ARZT = """---
Type: Situation
NextTime: 2026-11-20
---

# Arzt & Apotheke
"""

SCRIPTS = ["deutschkurs-data.js", "framework/deutschkurs/answer.js", "framework/deutschkurs/scheduler.js",
           "framework/deutschkurs/practice-core.js", "framework/deutschkurs/store.js",
           "framework/deutschkurs/practice.js"]


def main(page):
    return page.split("<main", 1)[1].split("</main>", 1)[0]


def positions(page):
    return [page.index(f'{name}"') for name in SCRIPTS]


def test_practice_page_exists_and_loads_scripts_in_order(built_site):
    page = built_site.page("practice.html")
    found = positions(page)
    assert found == sorted(found)
    assert page.index("framework/deutschkurs/speech.js") > found[-1]
    html = main(page)
    for kind in ("daily", "short", "weekly", "free"):
        assert f'data-session="{kind}"' in html, kind
    assert 'id="dk-practice-card"' in html and 'id="dk-export"' in html and 'id="dk-import"' in html
    assert "<noscript>" in html


def test_free_filters_list_course_values(built_site):
    html = main(built_site.page("practice.html"))
    situation = re.search(r'<select[^>]*data-filter="situation".*?</select>', html, re.S).group()
    assert ">Elternabend</option>" in situation and ">Am Schultor</option>" in situation
    kinds = re.search(r'<select[^>]*data-filter="type".*?</select>', html, re.S).group()
    assert 'value="Word"' in kinds and 'value="Mistake"' in kinds and 'value="Photo"' not in kinds


def test_prepare_button_encodes_title(tmp_path):
    site = build_site(tmp_path, {"arzt.md": ARZT}, starter=False)
    html = main(site.page("arzt.html"))
    assert re.search(r'<a class="dk-prepare uk-button uk-button-primary" href="practice.html#situation=Arzt%20%26%20Apotheke"',
                     html)


def test_starter_situation_has_prepare_and_data(built_site):
    page = built_site.page("situation-elternabend.html")
    assert 'href="practice.html#situation=Elternabend"' in page


def test_home_today_block_without_js_links_practice(built_site):
    page = built_site.page("index.html")
    today = re.search(r'<section class="dk-today[^"]*".*?</section>', page, re.S).group()
    assert 'href="practice.html"' in today
    found = positions(page)
    assert found == sorted(found)


def test_practice_strings_come_from_labels(tmp_path):
    site = build_site(tmp_path, settings={"labels": {"check": "Prüfen", "daily": "Täglich"}})
    page = site.page("practice.html")
    strings = json.loads(re.search(r'<script type="application/json" id="dk-practice-labels">(.*?)</script>',
                                   page, re.S).group(1))
    assert strings["check"] == "Prüfen"
    assert ">Täglich<" in main(page)


def test_no_practice_link_in_top_bar(built_site):
    top = re.search(r'<header class="dk-top.*?</header>', built_site.page("index.html"), re.S).group()
    assert "practice.html" not in top
