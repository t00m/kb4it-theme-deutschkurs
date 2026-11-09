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
