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
    (change(WORD, Type="Poster"), None, ("Type", "type_unknown")),
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
    (change(VERB, Separable="Yes", Prefix="an"), None, ("Separable", "flag_invalid")),
    (change(WORD, PluralOnly="true"), None, ("PluralOnly", "flag_invalid")),
    ({"Type": ("Photo",), "Place": ("Moon",)}, None, ("Place", "place_invalid")),
]


@pytest.mark.parametrize("props, topics, expected", ROWS, ids=[r[2][1] for r in ROWS])
def test_reason(props, topics, expected):
    problems = check_properties("a.md", props, topics)
    assert [(p.key, p.reason) for p in problems] == [expected]


def test_impossible_date():
    problems = check_properties("a.md", change(WORD, Date="2026-13-45"), None)
    assert [(p.key, p.reason) for p in problems] == [("Date", "date_invalid")]


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
    # Reasons outside ROWS have their own tests below.
    other = {"explanation_missing", "kind_missing", "kind_invalid", "genre_invalid", "situation_unknown",
             "turn_invalid", "mistake_incomplete"}
    assert set(REASONS) == {r[2][1] for r in ROWS} | other


def test_problem_str():
    problem = MetaProblem("a.md", "Level", "level_invalid")
    assert str(problem) == "META_INVALID doc=a.md key=Level reason=level_invalid"


def test_verify_hook_accepts_lists():
    lines = verify({"deutschkurs": {}}, {"a.md": {"Type": ["Word"]}})
    assert lines
    assert all(line.startswith("META_INVALID doc=a.md") for line in lines)


CONV = {"Type": ("Conversation",), "Level": ("A1",), "Kind": ("model",)}
TEXT = {"Type": ("Text",), "Level": ("A2",)}


def reasons(props):
    return [(p.key, p.reason) for p in check_properties("x.md", props, None)]


def test_new_types_are_clean():
    assert reasons(CONV) == []
    assert reasons(TEXT) == []
    assert reasons({"Type": ("Situation",)}) == []


def test_conversation_needs_a_valid_kind():
    assert reasons(change(CONV, Kind=None)) == [("Kind", "kind_missing")]
    assert reasons(change(CONV, Kind="Model")) == [("Kind", "kind_invalid")]


def test_text_genre_must_be_known():
    assert reasons(change(TEXT, Genre="School letter")) == []
    assert reasons(change(TEXT, Genre="Brief")) == [("Genre", "genre_invalid")]


@pytest.mark.parametrize("key", ["NextTime", "Received", "Deadline"])
def test_every_date_property_is_checked(key):
    assert reasons(change(TEXT, **{key: "2026-02-30"})) == [(key, "date_invalid")]
    assert reasons(change(TEXT, **{key: "2026-02-28"})) == []


def test_reply_is_a_flag():
    assert reasons(change(TEXT, Reply="true")) == [("Reply", "flag_invalid")]


def test_malformed_turns_are_problems_with_the_line():
    from test_parse import CONVERSATION
    entry = entry_from("gruss.md", CONV, CONVERSATION)
    problems = check_body(entry)
    assert [str(p) for p in problems] == [
        "META_INVALID doc=gruss.md key=Turn reason=turn_invalid line=10",
        "META_INVALID doc=gruss.md key=Turn reason=turn_invalid line=16",
    ]


def test_unknown_situation_is_a_problem():
    entry = entry_from("x.md", change(WORD, Situation="Elternabend, Beim Arzt"), "# Termin\n")
    assert [(p.key, p.reason) for p in check_body(entry, {"Elternabend"})] == [("Situation", "situation_unknown")]
    assert check_body(entry, {"Elternabend", "Beim Arzt"}) == []
    assert check_body(entry) == []


def test_new_reasons_listed():
    for reason in ("kind_missing", "kind_invalid", "genre_invalid", "situation_unknown", "turn_invalid"):
        assert reason in REASONS


PHOTO = {"Type": ("Photo",), "Place": ("Street",)}
MISTAKE = {"Type": ("Mistake",), "Level": ("A1",), "Pattern": ("es-tener-haben",)}


def test_photo_needs_no_level():
    assert check_properties("p.md", PHOTO, None) == []


def test_gap_needs_no_level():
    assert check_properties("g.md", {"Type": ("Gap",)}, None) == []
    assert check_properties("i.md", {"Type": ("Inbox",)}, None) == []


def test_mistake_needs_level():
    problems = check_properties("m.md", change(MISTAKE, Level=None), None)
    assert [(p.key, p.reason) for p in problems] == [("Level", "level_missing")]


def test_place_invalid():
    problems = check_properties("p.md", change(PHOTO, Place="Moon"), None)
    assert [(p.key, p.reason) for p in problems] == [("Place", "place_invalid")]


def test_place_invalid_in_verify():
    assert verify({}, {"p.md": change(PHOTO, Place="Moon")}) == [
        "META_INVALID doc=p.md key=Place reason=place_invalid"]


def test_mistake_without_right_is_incomplete():
    entry = entry_from("m.md", MISTAKE, "# Ich habe 40 Jahre\n\n## Wrong\n\nIch habe 40 Jahre.\n\n## Right\n\n\n")
    assert [(p.key, p.reason) for p in check_body(entry)] == [("Right", "mistake_incomplete")]


def test_complete_mistake_is_clean():
    entry = entry_from("m.md", MISTAKE, "# X\n\n## Wrong\n\nIch habe 40 Jahre.\n\n## Right\n\nIch bin 40.\n")
    assert check_body(entry) == []


def test_reasons_of_0_3_listed():
    assert "place_invalid" in REASONS and "mistake_incomplete" in REASONS
