from deutschkurs.logic.parse import Pair, h1, pairs, sections

DOC = """---
Type: Word
---

# Termin

## Examples

- Ich habe einen Termin. :: Tengo una cita.

## Notes

Masculino.
"""


def test_sections_order_and_bodies():
    result = sections(DOC)
    assert list(result) == ["Examples", "Notes"]
    assert result["Notes"].strip() == "Masculino."


def test_sections_ignore_headings_in_code():
    doc = "# T\n\n## A\n\n```\n## not a section\n```\n"
    assert list(sections(doc)) == ["A"]


def test_pairs():
    text = "- Ich habe einen Termin. :: Tengo una cita.\n- Ohne Übersetzung"
    assert pairs(text) == [Pair("Ich habe einen Termin.", "Tengo una cita."), Pair("Ohne Übersetzung", "")]


def test_pairs_keeps_double_colon_inside_translation_side():
    assert pairs("- a :: b :: c") == [Pair("a", "b :: c")]


def test_h1():
    assert h1(DOC) == "Termin"


def test_h1_missing():
    assert h1("---\nType: Word\n---\n\ntext") == ""


CONVERSATION = """---
Kind: model
Type: Conversation
---

# Gruß am Schultor

- **Mutter:** Hallo! Na, wie geht's? :: Hello! How are you?
- **ich**: Hallo! *Gut*, danke. :: Hello! Fine, thanks.
- Das ist kein Turn.
- **Mutter:** Bis morgen!

## Variations

- 2 **ich:** Es geht. :: So-so.
- ohne Nummer

## Notes

- **Kein:** Turn hier.
"""


def test_turns_numbered_by_position():
    from deutschkurs.logic.parse import turns
    found, _, _ = turns(CONVERSATION)
    assert [(u.anchor, u.speaker, u.german, u.translation) for u in found] == [
        ("t1", "Mutter", "Hallo! Na, wie geht's?", "Hello! How are you?"),
        ("t2", "ich", "Hallo! Gut, danke.", "Hello! Fine, thanks."),
        ("t3", "", "Das ist kein Turn.", ""),
        ("t4", "Mutter", "Bis morgen!", ""),
    ]


def test_malformed_turns_reported_with_their_line():
    from deutschkurs.logic.parse import turns
    _, _, bad = turns(CONVERSATION)
    assert bad == [10, 16]


def test_variations_name_the_turn_they_replace():
    from deutschkurs.logic.parse import turns
    _, variations, _ = turns(CONVERSATION)
    assert [(u.anchor, u.replaces, u.speaker, u.german, u.translation) for u in variations] == [
        ("v1", 2, "ich", "Es geht.", "So-so.")]


def test_turn_list_ends_at_the_first_paragraph():
    from deutschkurs.logic.parse import turns
    text = "# T\n\n- **A:** Eins.\n\nEin Absatz.\n\n- **B:** Zwei.\n"
    assert [u.german for u in turns(text)[0]] == ["Eins."]


TEXT = """---
Type: Text
---

# Elternbrief

Liebe Eltern,

> Dear parents,

am Freitag machen wir einen *Ausflug*.
Bitte geben Sie Ihrem Kind eine Brotdose mit.

> On Friday we are going on a trip.
> Please give your child a lunch box.

![Foto](resources/foto.jpg)

- eine Liste

Viele Grüße

## Notes

Kein Satz des Briefes.
"""


def test_paragraphs_with_their_translation():
    from deutschkurs.logic.parse import paragraphs
    assert [(u.anchor, u.german, u.translation) for u in paragraphs(TEXT)] == [
        ("s1", "Liebe Eltern,", "Dear parents,"),
        ("s2", "am Freitag machen wir einen Ausflug. Bitte geben Sie Ihrem Kind eine Brotdose mit.",
         "On Friday we are going on a trip. Please give your child a lunch box."),
        ("s3", "Viele Grüße", ""),
    ]


def test_tasks_counts_ticked_and_total():
    from deutschkurs.logic.parse import tasks
    assert tasks("- [x] Eins :: one\n- [ ] Zwei\n* [X] Drei\n- kein Task\n") == (2, 3)


def test_blockquote_right_after_a_paragraph_is_its_translation():
    from deutschkurs.logic.parse import paragraphs
    text = "# T\n\nGuten Tag.\n> Good day.\n\nTschüs.\n"
    assert [(u.german, u.translation) for u in paragraphs(text)] == [("Guten Tag.", "Good day."), ("Tschüs.", "")]


def test_code_right_after_a_paragraph_is_not_part_of_it():
    from deutschkurs.logic.parse import paragraphs
    text = "# T\n\nGuten Tag.\n```\ncode\n```\nTschüs.\n"
    assert [u.german for u in paragraphs(text)] == ["Guten Tag.", "Tschüs."]


def test_unmarked_line_inside_a_quote_stays_in_the_translation():
    from deutschkurs.logic.parse import paragraphs
    text = "# T\n\nGuten Tag.\n\n> Good\nday.\n"
    assert [(u.german, u.translation) for u in paragraphs(text)] == [("Guten Tag.", "Good day.")]


def test_turn_speaker_in_underscores():
    from deutschkurs.logic.parse import turns
    found, _, bad = turns("# T\n\n- __A:__ Hallo.\n- **B** und **C:** Nein.\n")
    assert [(u.speaker, u.german) for u in found] == [("A", "Hallo."), ("", "B und C: Nein.")]
    assert bad == [4]


def test_paragraph_text_has_no_images_links_or_tags():
    from deutschkurs.logic.parse import paragraphs
    text = "# T\n\n![Foto](a.png) Siehe [die Seite](http://x.de) und <b>hier</b>.\n\n![Nur Bild](b.png)\n"
    assert [u.german for u in paragraphs(text)] == ["Siehe die Seite und hier."]


def test_rules_and_boxes_are_not_paragraphs():
    from deutschkurs.logic.parse import paragraphs
    text = "# T\n\nEins.\n\n---\n\n!!! note\n    Im Kasten.\n\n<span>Zwei</span> und mehr.\n\n<div>Block</div>\n"
    assert [u.german for u in paragraphs(text)] == ["Eins.", "Zwei und mehr."]


from deutschkurs.logic.parse import InboxItem, image, inbox_items

PHOTO_DOC = """---
Type: Photo
---

# Baustelle betreten verboten

![Sign at a building site](resources/photos/2026-11-09-baustelle.webp)

## Transcription

Baustelle betreten verboten!
Eltern haften für ihre Kinder.

Zweiter Satz.

## Meaning

![later](resources/photos/other.webp)
"""


def test_image_found_before_sections():
    assert image(PHOTO_DOC) == "resources/photos/2026-11-09-baustelle.webp"
    assert image("# T\n\n## Meaning\n\n![x](a.webp)\n") == ""


INBOX_DOC = """---
Type: Inbox
---

# Inbox November

- 2026-11-09 Kaution | Vermieter hat gesagt | Wohnung
- Pfand
- 2026-13-45 Pfand am Automaten
- 2026-11-10 ![](resources/photos/2026-11-09-pfand.webp) Pfandautomat
"""


def test_inbox_items_with_and_without_date():
    items = inbox_items(INBOX_DOC)
    assert [(i.date, i.text) for i in items] == [
        ("2026-11-09", "Kaution | Vermieter hat gesagt | Wohnung"),
        ("", "Pfand"),
        ("2026-13-45", "Pfand am Automaten"),
        ("2026-11-10", "Pfandautomat"),
    ]
    assert items[0].line == 7


def test_inbox_item_image_split_from_text():
    item = inbox_items(INBOX_DOC)[3]
    assert item == InboxItem("2026-11-10", "Pfandautomat", "resources/photos/2026-11-09-pfand.webp", 10)


def test_image_with_spaces_in_angle_brackets():
    assert image('# T\n\n![x](<resources/photos/mein foto.webp>)\n') == "resources/photos/mein foto.webp"
    assert image('# T\n\n![x](<resources/photos/mein foto.webp> "Titel")\n') == "resources/photos/mein foto.webp"
    assert image('# T\n\n![x](resources/photos/a.webp "Titel")\n') == "resources/photos/a.webp"
