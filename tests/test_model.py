from pathlib import Path

from deutschkurs.logic.model import SECTIONS, TYPES, entry_from

STARTER = Path(__file__).resolve().parent.parent / "deutschkurs" / "apps" / "default" / "source"

CHUNK = """---
Type: Chunk
Level: A2
Register: neutral
Translation: avisar a alguien
Checked: attested
---

# Bescheid sagen

## Variants

- Sag mir Bescheid! :: ¡Avísame!
- Sagen Sie mir bitte Bescheid. :: Avíseme, por favor.

## Usage

Cuando prometes informar a alguien más tarde.
"""


def test_types():
    assert TYPES == ("Word", "Verb", "Chunk", "Grammar", "Text", "Conversation", "Situation", "Photo", "Mistake",
                     "Gap", "Inbox")


def test_word_entry():
    props = {"Type": ("Word",), "Level": ("A1",), "Article": ("der",), "PartOfSpeech": ("noun",),
             "Translation": ("cita",)}
    entry = entry_from("termin", props, (STARTER / "termin.md").read_text(encoding="utf-8"))
    assert entry.type == "Word"
    assert entry.title == "Termin"
    assert entry.level == "A1"
    assert entry.translation == "cita"
    assert entry.checked == "unchecked"
    assert entry.is_noun is True
    assert entry.value("Article") == "der"
    assert entry.value("Missing", "x") == "x"


def test_chunk_examples_from_variants():
    props = {"Type": ("Chunk",), "Level": ("A2",), "Checked": ("attested",)}
    entry = entry_from("bescheid-sagen", props, CHUNK)
    assert entry.checked == "attested"
    assert [p.translation for p in entry.examples] == ["¡Avísame!", "Avíseme, por favor."]
    assert entry.is_noun is False


def test_sections_known_per_type():
    assert SECTIONS["Grammar"] == ("Explanation", "Simple German", "Typical mistakes")
    assert SECTIONS["Word"] == ("Examples", "Pronunciation", "False friends", "Notes")


def test_translation_with_comma_joined():
    props = {"Type": ("Word",), "Translation": ("pan", "mantequilla")}
    assert entry_from("x", props, "# X").translation == "pan, mantequilla"


def test_new_types_and_their_sections():
    assert TYPES[4:7] == ("Text", "Conversation", "Situation")
    assert SECTIONS["Conversation"] == ("Variations", "Notes")
    assert SECTIONS["Situation"] == ("I can", "Log")


def test_conversation_entry_has_units():
    from test_parse import CONVERSATION
    entry = entry_from("gruss.md", {"Type": ("Conversation",), "Kind": ("model",)}, CONVERSATION)
    assert [u.anchor for u in entry.units] == ["t1", "t2", "t3", "t4"]
    assert [u.anchor for u in entry.variations] == ["v1"]
    assert entry.bad_lines == (10, 16)


def test_text_entry_has_units():
    from test_parse import TEXT
    entry = entry_from("brief.md", {"Type": ("Text",)}, TEXT)
    assert [u.anchor for u in entry.units] == ["s1", "s2", "s3"]


def test_situation_entry_counts_can_do():
    text = "---\nType: Situation\n---\n\n# Elternabend\n\n## I can\n\n- [x] Eins :: one\n- [ ] Zwei :: two\n"
    assert entry_from("s.md", {"Type": ("Situation",)}, text).cando == (1, 2)


def test_word_entry_has_no_units():
    assert entry_from("x.md", {"Type": ("Word",)}, "# Termin\n\nEin Absatz.\n").units == ()


def test_photo_units_are_transcription_paragraphs():
    from test_parse import PHOTO_DOC
    entry = entry_from("p.md", {"Type": ("Photo",)}, PHOTO_DOC)
    assert [(u.anchor, u.german) for u in entry.units] == [
        ("p1", "Baustelle betreten verboten! Eltern haften für ihre Kinder."), ("p2", "Zweiter Satz.")]
    assert entry.image == "resources/photos/2026-11-09-baustelle.webp"


def test_gap_with_blank_in_german_is_open():
    gap = "# Krank melden\n\n## I wanted to say\n\nMy son is sick.\n\n## In German\n\n   \n\n"
    assert entry_from("g.md", {"Type": ("Gap",)}, gap).open_gap
    done = gap.replace("   \n", "Mein Sohn ist krank.\n")
    assert not entry_from("g.md", {"Type": ("Gap",)}, done).open_gap
    assert not entry_from("w.md", {"Type": ("Word",)}, gap).open_gap


def test_inbox_entry_has_items():
    from test_parse import INBOX_DOC
    entry = entry_from("inbox-2026-11.md", {"Type": ("Inbox",)}, INBOX_DOC)
    assert len(entry.inbox) == 4


def test_new_types_and_sections():
    assert {"Photo", "Mistake", "Gap", "Inbox"} <= set(TYPES)
    assert SECTIONS["Mistake"] == ("Wrong", "Right", "Why")
    assert SECTIONS["Gap"] == ("I wanted to say", "In German")
