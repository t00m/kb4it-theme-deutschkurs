from deutschkurs.logic.config import DeutschkursConfig
from deutschkurs.logic.course import build_course, sort_key


def doc(doc_id, title, **props):
    return doc_id, {k: tuple(v.split(", ")) for k, v in props.items()}, f"# {title}\n"


WORD = dict(Type="Word", PartOfSpeech="noun", Article="der", Translation="x")
DOCS = [
    doc("zug.md", "Zug", Level="A1", **WORD),
    doc("aerger.md", "Ärger", Level="A2", **WORD),
    doc("abend.md", "Abend", Level="A1", **WORD),
    doc("notiz.md", "Notiz"),
]


def test_sort_key_folds_umlauts():
    assert sorted(["Zug", "Ärger", "Abend", "älter"], key=sort_key) == ["Abend", "älter", "Ärger", "Zug"]


def test_by_type_sorted_with_umlauts():
    course = build_course(DOCS, DeutschkursConfig())
    assert [e.title for e in course.by_type("Word")] == ["Abend", "Ärger", "Zug"]


def test_untyped_doc_kept_with_problem():
    course = build_course(DOCS, DeutschkursConfig())
    assert course.entries["notiz.md"].type == ""
    assert [(p.doc, p.reason) for p in course.problems] == [("notiz.md", "type_missing")]


def test_facet_level():
    course = build_course(DOCS, DeutschkursConfig())
    assert [e.title for e in course.facet("Level")["A1"]] == ["Abend", "Zug"]
    assert list(course.facet("Level")) == ["A1", "A2"]


def test_glossary_uses_url():
    course = build_course(DOCS, DeutschkursConfig(), url=lambda i: "x/" + i)
    assert course.url("zug.md") == "x/zug.md"
    assert course.glossary.lookup("Zug") == ("zug.md", "dk-m")


SITUATION_DOCS = [
    doc("termin.md", "Termin", Level="A1", Situation="Beim Arzt", **WORD),
    doc("zug.md", "Zug", Level="A1", Situation="Am Bahnhof", **WORD),
    ("arzt.md", {"Type": ("Situation",)}, "# Beim Arzt\n"),
    ("anruf.md", {"Type": ("Conversation",), "Level": ("A1",), "Kind": ("model",), "Situation": ("Beim Arzt",)},
     "# Anruf\n\n- **ich:** Ich brauche einen Termin.\n- kein Turn\n"),
]


def test_situations_by_title():
    course = build_course(SITUATION_DOCS, DeutschkursConfig())
    assert course.situations == {"Beim Arzt": "arzt.md"}
    assert [e.id for e in course.in_situation("Beim Arzt")] == ["anruf.md", "termin.md"]


def test_unknown_situation_and_bad_turn_are_problems():
    course = build_course(SITUATION_DOCS, DeutschkursConfig())
    assert [str(p) for p in course.problems] == [
        "META_INVALID doc=anruf.md key=Turn reason=turn_invalid line=4",
        "META_INVALID doc=zug.md key=Situation reason=situation_unknown",
    ]


def test_course_has_index_and_coverage():
    course = build_course(SITUATION_DOCS, DeutschkursConfig(known_words=["Brauche"]))
    assert [(o.doc, o.anchor) for o in course.index["termin.md"]] == [("anruf.md", "t1")]
    found = course.coverage["anruf.md"]
    assert (found.total, found.missing) == (6, ("Turn",))
