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
    assert TYPES == ("Word", "Verb", "Chunk", "Grammar")


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
