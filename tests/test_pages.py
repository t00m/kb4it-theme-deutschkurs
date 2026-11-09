import re

import pytest

from conftest import build_site, warnings

TERMIN = """---
Article: der
Checked: assistant
Level: A1
PartOfSpeech: noun
Plural: die Termine
Translation: cita
Type: Word
---

# Termin

## Examples

- Ich habe morgen einen Termin. :: Mañana tengo una cita.
- Der Termin ist um acht Uhr. :: La cita es a las ocho.
"""

BUTTERBROT = """---
Article: das
Level: A2
PartOfSpeech: noun
Translation: pan & mantequilla <casero>
Type: Word
---

# Butterbrot
"""

ANRUFEN = """---
Auxiliary: haben
Level: A1
Participle: angerufen
Prefix: an
Present: ich rufe an, du rufst an, er ruft an
Separable: yes
Translation: llamar por teléfono
Type: Verb
---

# anrufen

## Examples

- Ich rufe dich morgen an. :: Te llamo mañana.
"""

HELFEN = """---
Auxiliary: haben
Government: Dativ
Level: A1
Participle: geholfen
Translation: ayudar
Type: Verb
---

# helfen

## Typical mistakes

- Kannst du mich helfen? :: Kannst du mir helfen?
"""

DATIV = """---
Area: Cases
Case: Dativ
Level: A2
Type: Grammar
---

# Dativ

## Explanation

El dativo marca a quien recibe algo.

## Simple German

Der Dativ zeigt, wem etwas gehört oder wer etwas bekommt.
"""

EXTRA = {"termin.md": TERMIN, "butterbrot.md": BUTTERBROT, "anrufen.md": ANRUFEN, "helfen.md": HELFEN,
         "dativ.md": DATIV}


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    return build_site(tmp_path_factory.mktemp("pages"), EXTRA, starter=False)


@pytest.fixture(scope="module")
def b1_site(tmp_path_factory):
    return build_site(tmp_path_factory.mktemp("pages_b1"), EXTRA, {"learner_level": "B1"}, starter=False)


def main(page: str) -> str:
    return page.split("<main", 1)[1].split("</main>", 1)[0]


def test_no_warnings(site):
    assert warnings(site.log) == []


def test_word_card(site):
    html = main(site.page("termin.html"))
    assert re.search(r'class="[^"]*dk-m[^"]*"[^>]*>der Termin<', html)
    assert "die Termine" in html
    assert "cita" in html
    assert "A1" in html
    assert "dk-checked-assistant" in html
    assert html.count('class="dk-listen"') == 3


def test_examples_split_into_german_and_translation(site):
    html = main(site.page("termin.html"))
    assert '<span class="dk-de" lang="de">Ich habe morgen einen Termin.</span>' in html
    assert '<span class="dk-tr dk-no-link" lang="es">Mañana tengo una cita.</span>' in html
    assert " :: " not in html


def test_translation_escaped(site):
    html = site.page("butterbrot.html")
    assert "&lt;casero&gt;" in html
    assert "<casero>" not in html


def test_verb_card(site):
    html = main(site.page("anrufen.html"))
    assert "hat angerufen" in html
    assert "Separable" in html
    assert "AN-rufen" in html
    assert "ich rufe an" in html


def test_grammar_lists_verbs_by_case(site):
    html = main(site.page("dativ.html"))
    assert 'href="helfen.html"' in html


def test_grammar_explanation_first_below_german_from(site):
    html = main(site.page("dativ.html"))
    assert html.index('id="explanation"') < html.index('id="simple-german"')
    assert re.search(r'<details class="dk-fold">.*id="simple-german"', html, re.S)


def test_grammar_simple_german_first_from_german_from(b1_site):
    html = main(b1_site.page("dativ.html"))
    assert html.index('id="simple-german"') < html.index('id="explanation"')
    assert re.search(r'<details class="dk-fold">.*id="explanation"', html, re.S)


def test_body_speech_attributes(site):
    body = re.search(r"<body[^>]*>", site.page("index.html")).group()
    assert 'data-speech="true"' in body
    assert 'data-speech-lang="de-DE"' in body


def test_scripts_local(site):
    for name in ("index.html", "termin.html", "search.html", "404.html"):
        page = site.page(name)
        assert 'src="resources/themes/deutschkurs/framework/deutschkurs/core.js"' in page, name
        assert 'src="resources/themes/deutschkurs/framework/deutschkurs/speech.js"' in page, name


def test_typical_mistakes_are_german_and_only_the_right_form_is_spoken(site):
    html = main(site.page("helfen.html"))
    assert '<span class="dk-wrong" lang="de">Kannst du mich helfen?</span>' in html
    assert '<span class="dk-right" lang="de">Kannst du mir helfen?</span>' in html
    assert 'data-say="Kannst du mir helfen?"' in html
    assert 'data-say="Kannst du mich helfen?"' not in html
