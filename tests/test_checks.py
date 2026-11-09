from pathlib import Path

import pytest

from deutschkurs.logic.checks import REASONS, MetaProblem, check_body, check_properties
from deutschkurs.logic.model import entry_from
from deutschkurs.logic.verify import verify

WORD = {"Type": ("Word",), "Level": ("A1",), "Translation": ("cita",), "Article": ("der",),
        "PartOfSpeech": ("noun",)}
VERB = {"Type": ("Verb",), "Level": ("A1",), "Translation": ("llamar",), "Participle": ("angerufen",),
        "Auxiliary": ("haben",)}
GRAMMAR = {"Type": ("Grammar",), "Level": ("A2",), "Area": ("Verbs",)}


def change(base, **kw):
    props = dict(base)
    for key, value in kw.items():
        if value is None:
            props.pop(key, None)
        else:
            props[key] = tuple(value.split(", "))
    return props


ROWS = [
    ({"Level": ("A1",)}, None, ("Type", "type_missing")),
    (change(WORD, Type="Text"), None, ("Type", "type_unknown")),
    (change(WORD, Level=None), None, ("Level", "level_missing")),
    (change(WORD, Level="A3"), None, ("Level", "level_invalid")),
    (change(WORD, Translation=None), None, ("Translation", "translation_missing")),
    (change(WORD, Article=None), None, ("Article", "article_missing")),
    (change(WORD, PartOfSpeech="thing"), None, ("PartOfSpeech", "part_of_speech_invalid")),
    (change(VERB, Participle=None), None, ("Participle", "participle_missing")),
    (change(VERB, Auxiliary=None), None, ("Auxiliary", "auxiliary_missing")),
    (change(VERB, Separable="yes"), None, ("Prefix", "prefix_missing")),
    (change(WORD, Register="formal"), None, ("Register", "register_invalid")),
    (change(WORD, Checked="maybe"), None, ("Checked", "checked_invalid")),
    (change(GRAMMAR, Area="Stuff"), None, ("Area", "area_invalid")),
    (change(WORD, Date="09.11.2026"), None, ("Date", "date_invalid")),
    (change(WORD, Topic="Kino"), ["Schule"], ("Topic", "topic_unknown")),
]


@pytest.mark.parametrize("props, topics, expected", ROWS, ids=[r[2][1] for r in ROWS])
def test_reason(props, topics, expected):
    problems = check_properties("a.md", props, topics)
    assert [(p.key, p.reason) for p in problems] == [expected]


def test_explanation_missing():
    entry = entry_from("g", GRAMMAR, "# Perfekt\n\n## Simple German\n\nText.\n")
    assert [(p.key, p.reason) for p in check_body(entry)] == [("Explanation", "explanation_missing")]


def test_grammar_with_explanation_ok():
    entry = entry_from("g", GRAMMAR, "# Perfekt\n\n## Explanation\n\nTexto.\n")
    assert check_body(entry) == []


def test_valid_entries_have_no_problem():
    assert check_properties("a.md", WORD, None) == []
    assert check_properties("a.md", VERB, None) == []
    assert check_properties("a.md", change(VERB, Auxiliary="haben, sein"), None) == []
    assert check_properties("a.md", change(WORD, Date="2026-11-09 10:30"), None) == []
    assert check_properties("a.md", change(WORD, Topic="Schule"), ["Schule"]) == []


def test_starter_word_valid():
    starter = Path(__file__).resolve().parent.parent / "deutschkurs/apps/default/source/termin.md"
    assert starter.is_file()
    assert check_properties("termin.md", WORD, None) == []


def test_plural_only_noun_needs_no_article():
    assert check_properties("a.md", change(WORD, Article=None, PluralOnly="yes"), None) == []


def test_reasons_complete():
    assert set(REASONS) == {r[2][1] for r in ROWS} | {"explanation_missing"}


def test_problem_str():
    problem = MetaProblem("a.md", "Level", "level_invalid")
    assert str(problem) == "META_INVALID doc=a.md key=Level reason=level_invalid"


def test_verify_hook_accepts_lists():
    lines = verify({"deutschkurs": {}}, {"a.md": {"Type": ["Word"]}})
    assert lines
    assert all(line.startswith("META_INVALID doc=a.md") for line in lines)
