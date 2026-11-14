import pytest

from conftest import build_site, warnings
from deutschkurs.logic.checks import check_properties, step


def word(title, pos, level="A1", extra=""):
    return f"""---
Checked: assistant
Level: {level}
PartOfSpeech: {pos}
Translation: x
Type: Word
{extra}---

# {title}

## Examples

- {title} ist gut. :: x
"""


def grammar(title, level, step_line=""):
    return f"""---
Area: Other
Checked: assistant
Level: {level}
{step_line}Type: Grammar
---

# {title}

## Explanation

Short.
"""


TALK = """---
Checked: assistant
Kind: model
Level: A1
Type: Conversation
---

# Am Morgen

- **Kind:** Ich bin müde. :: I am tired.
"""

FILES = {
    "termin.md": word("Termin", "noun", extra="Article: der\nPlural: die Termine\n"),
    "klein.md": word("klein", "adjective"),
    "hier.md": word("hier", "adverb"),
    "spaet.md": word("spät", "adjective", level="A2"),
    # Alphabetical order would put Akkusativ first; the Step puts it second.
    "akkusativ.md": grammar("Akkusativ", "A1", "Step: 2\n"),
    "zahlen.md": grammar("Zahlen", "A1", "Step: 1\n"),
    "artikel.md": grammar("Artikel", "A1"),
    "dativ.md": grammar("Dativ", "A2"),
    "am-morgen.md": TALK,
}


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    return build_site(tmp_path_factory.mktemp("levels"), FILES, starter=False)


def main(html):
    return html[html.index("<main"):] if "<main" in html else html


def test_no_warnings(site):
    assert warnings(site.log) == []


def test_overview_has_a_card_per_level(site):
    html = main(site.page("Level.html"))
    assert 'href="Level_A1.html"' in html and 'href="Level_A2.html"' in html
    assert 'href="practice.html#level=A1"' in html
    assert "How to study a level" in html
    # The learner's level (default A2) is marked.
    a2 = html[html.index('href="Level_A2.html"') - 400:]
    assert "dk-mine" in a2 and "Your level" in html


def test_study_page_follows_the_study_order(site):
    html = main(site.page("Level_A1.html"))
    assert html.index('id="grammar"') < html.index('id="conversations"') < html.index('id="vocabulary"')
    # Steps first, by number; then the entries without a Step.
    assert html.index('href="zahlen.html"') < html.index('href="akkusativ.html"') < html.index('href="artikel.html"')
    assert 'href="dativ.html"' not in html and 'href="spaet.html"' not in html
    assert 'href="practice.html#level=A1"' in html


def test_words_by_part_of_speech_nouns_with_article(site):
    html = main(site.page("Level_A1.html"))
    words = html[html.index('id="vocabulary"'):]
    assert words.index(">noun<") < words.index(">adjective<") < words.index(">adverb<")
    assert ">der Termin<" in words


def test_home_points_to_the_levels(site):
    html = main(site.page("index.html"))
    assert "Start here" in html
    assert 'uk-button-primary uk-button-small" href="Level_A2.html"' in html
    assert 'uk-button-default uk-button-small" href="Level_A1.html"' in html


def test_menu_links_the_levels(site):
    assert 'href="Level.html"' in site.page("klein.html")


def test_step_values():
    assert step("1") == 1 and step(" 12 ") == 12
    assert step("0") is None and step("zwei") is None and step("1.5") is None and step("²") is None


def test_step_invalid_reported():
    props = {"Type": ["Grammar"], "Level": ["A1"], "Area": ["Other"], "Step": ["zwei"]}
    assert [p.reason for p in check_properties("g.md", props, None)] == ["step_invalid"]
    props["Step"] = ["3"]
    assert check_properties("g.md", props, None) == []
