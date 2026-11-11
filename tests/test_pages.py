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
    assert html.count('class="dk-listen uk-button uk-button-default uk-button-small"') == 3
    assert html.count('class="dk-listen dk-slow uk-button uk-button-default uk-button-small"') == 3
    assert html.count('data-rate="slow"') == 3


def test_examples_split_into_german_and_translation(site):
    html = main(site.page("termin.html"))
    assert '<span class="dk-de" lang="de">Ich habe morgen einen Termin.</span>' in html
    assert '<span class="dk-tr dk-no-link" lang="en">Mañana tengo una cita.</span>' in html
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


GRUSS = """---
Checked: assistant
Date: 2026-11-05
Kind: model
Level: A1
Situation: Am Schultor
Type: Conversation
---

# Gruß am Schultor

- **Mutter:** Hallo! Hast du morgen einen Termin? :: Hello! Do you have an appointment tomorrow?
- **ich:** Ja, weil ich krank bin. :: Yes, because I am ill.
- Das ist kein Turn.
- **Mutter:** Gute Besserung!

## Variations

- 2 **ich:** Nein, ich habe Zeit. :: No, I have time.

## Notes

- Na? :: Well?
"""

BRIEF = """---
Checked: attested
Deadline: 2026-11-20
Genre: School letter
Level: A2
Received: 2026-11-09
Reply: yes
Situation: Am Schultor
Type: Text
---

# Elternbrief

Liebe Eltern,

> Dear parents,

![Foto](resources/foto.png)

- eine Liste

der Termin ist am Freitag.

> The appointment is on Friday.

## Notes

Kein Satz.
"""

SCHULTOR = """---
NextTime: 2026-11-10
Type: Situation
---

# Am Schultor

## I can

- [x] Ich kann grüßen. :: I can greet.
- [ ] Ich kann nach einem Termin fragen. :: I can ask for an appointment.
"""

WEIL = """---
Area: Sentences
Level: A2
Marker: weil
Type: Grammar
---

# Nebensatz mit weil

## Explanation

The verb goes to the end.
"""

KIND = """---
Article: das
Level: A1
PartOfSpeech: noun
Situation: Nirgendwo
Translation: child
Type: Word
---

# Kind
"""

TALK = {"termin.md": TERMIN.replace("Checked:", "Situation: Am Schultor\nChecked:"), "gruss.md": GRUSS,
        "brief.md": BRIEF, "am-schultor.md": SCHULTOR, "weil.md": WEIL, "kind.md": KIND}


@pytest.fixture(scope="module")
def talk(tmp_path_factory):
    return build_site(tmp_path_factory.mktemp("talk"), TALK, starter=False)


def test_only_the_expected_problems(talk):
    found = warnings(talk.log)
    assert len(found) == 2
    assert any("doc=gruss.md" in line and "turn_invalid" in line for line in found)
    assert any("doc=kind.md" in line and "situation_unknown" in line for line in found)


def test_conversation_is_a_dialogue(talk):
    html = main(talk.page("gruss.html"))
    assert html.count('<ol class="dk-dialogue">') == 1
    assert '<li id="t1" class="dk-turn dk-other"><span class="dk-speaker dk-no-link">Mutter</span>' in html
    assert '<li id="t2" class="dk-turn dk-me"><span class="dk-speaker dk-no-link">ich</span>' in html
    assert '<li id="t3" class="dk-turn dk-invalid">' in html
    assert '<li id="t4" class="dk-turn dk-other">' in html
    assert 'data-say="Hallo! Hast du morgen einen Termin?"' in html
    assert " :: " not in html


def test_turn_words_are_linked_but_speakers_are_not(talk):
    html = main(talk.page("gruss.html"))
    first = html.split('<li id="t1"', 1)[1].split("</li>", 1)[0]
    assert 'href="termin.html"' in first
    assert '<span class="dk-speaker dk-no-link">Mutter</span>' in first


def test_variation_points_to_its_turn(talk):
    html = main(talk.page("gruss.html"))
    assert '<li id="v1" class="dk-turn dk-variation dk-me"><a class="dk-replaces" href="#t2">2</a>' in html


def test_turn_translations_show_without_script(talk):
    html = main(talk.page("gruss.html"))
    assert '<span class="dk-tr dk-no-link" lang="en">Hello! Do you have an appointment tomorrow?</span>' in html
    assert '<button type="button" class="dk-toggle-tr uk-button uk-button-default uk-button-small" hidden ' in html
    assert "dk-hide-tr" not in html


def test_conversation_card_and_coverage(talk):
    html = main(talk.page("gruss.html"))
    assert '<a class="dk-badge dk-kind dk-kind-model" href="ConversationKind_model.html">model</a>' in html
    assert 'href="am-schultor.html"' in html
    assert "Words you don&#39;t have yet" in html or "Words you don't have yet" in html
    missing = html.split('class="dk-missing"', 1)[1].split("</ul>", 1)[0]
    assert ">Besserung<" in missing and ">Termin<" not in missing


def test_text_sentences_have_anchors_and_folded_translations(talk):
    html = main(talk.page("brief.html"))
    assert '<p id="s1" class="dk-sentence"><span class="dk-de" lang="de">Liebe Eltern,</span>' in html
    second = html.split('<p id="s2" class="dk-sentence">', 1)[1].split("</p>", 1)[0]
    assert 'href="termin.html"' in second and 'data-say="der Termin ist am Freitag."' in second
    assert html.count('<details class="dk-fold dk-tr-fold" lang="en">') == 2
    assert 'id="s3"' not in html
    assert re.search(r"<p><img [^>]*></p>", html)


def test_text_card_and_deadline_banner(talk):
    html = main(talk.page("brief.html"))
    banner = re.search(r'<p class="dk-banner dk-deadline uk-alert uk-alert-danger"[^>]*>', html).group()
    assert 'data-date="2026-11-20"' in banner and 'data-hide="past"' in banner and " hidden" not in banner
    assert '<a class="dk-badge dk-genre" href="Genre_School_letter.html">School letter</a>' in html
    assert '<span class="dk-badge dk-reply">Needs a reply</span>' in html
    assert "dk-checked-attested" in html


def test_situation_page(talk):
    html = main(talk.page("am-schultor.html"))
    banner = re.search(r'<p class="dk-banner dk-coming uk-alert uk-alert-primary"[^>]*>', html).group()
    assert 'data-date="2026-11-10"' in banner and 'data-days="7"' in banner
    assert 'data-hide="past later"' in banner and " hidden" not in banner
    assert "1 / 2" in html
    for href in ("gruss.html", "brief.html", "termin.html"):
        assert f'href="{href}"' in html, href
    assert '<input type="checkbox"' in html
    assert '<span class="dk-de" lang="de">Ich kann grüßen.</span>' in html
    assert " :: " not in html
    assert "dk-checked" not in html


def test_word_shows_where_it_appears(talk):
    html = main(talk.page("termin.html"))
    where = html.split('class="dk-where"', 1)[1]
    assert where.index('href="brief.html#s2"') < where.index('href="gruss.html#t1"')
    assert "The appointment is on Friday." in where
    assert 'href="am-schultor.html"' in html
    assert 'id="s2"' in talk.page("brief.html") and 'id="t1"' in talk.page("gruss.html")


def test_unknown_situation_is_not_a_link(talk):
    html = main(talk.page("kind.html"))
    assert "<span>Nirgendwo</span>" in html
    assert "Nirgendwo.html" not in html and 'href=""' not in html


def test_grammar_lists_sentences_with_its_marker(talk):
    html = main(talk.page("weil.html"))
    texts = html.split('class="dk-candidates"', 1)[1]
    assert 'href="gruss.html#t2"' in texts and "Ja, weil ich krank bin." in texts


def test_kind_and_genre_have_facet_pages(talk):
    assert 'href="ConversationKind_model.html"' in main(talk.page("ConversationKind.html"))
    assert 'href="gruss.html"' in main(talk.page("ConversationKind_model.html"))
    assert 'href="brief.html"' in main(talk.page("Genre_School_letter.html"))
    assert "das Kind" in main(talk.page("kind.html"))


def test_date_without_a_time_is_shown_as_a_day(talk):
    card = main(talk.page("gruss.html"))
    assert "<dt>Date</dt><dd>2026-11-05</dd>" in card
