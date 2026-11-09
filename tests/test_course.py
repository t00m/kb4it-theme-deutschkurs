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
