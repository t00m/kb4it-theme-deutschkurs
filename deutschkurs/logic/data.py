"""The practice data file: deutschkurs-data.js, read by the Practice, Progress and home pages."""

import hashlib
import json
from pathlib import Path

from .config import DeutschkursConfig
from .course import Course
from .glossary import Glossary, find_spans
from .model import Entry
from .parse import Pair, Unit, clean
from .render import day

FILE = "deutschkurs-data.js"
PREFIX = "window.DEUTSCHKURS_DATA = "
# Above this size the build warns with DATA_LARGE (spec 7.1).
LIMIT = 2 * 1024 * 1024
# Types that give practice cards.
PRACTISED = ("Word", "Verb", "Chunk", "Conversation", "Mistake", "Gap")
# Types whose sentence units feed the sentence index.
SENTENCE_TYPES = ("Text", "Conversation", "Photo")


def site_id(title: str) -> str:
    """Short, stable id of a course for its storage keys (plan R2)."""
    return hashlib.sha256(str(title).encode("utf-8")).hexdigest()[:12]


def too_large(size: int) -> bool:
    return size > LIMIT


def forms_by_entry(g: Glossary) -> dict[str, list[str]]:
    """Every surface form the glossary knows, by entry id, in first-seen order."""
    found: dict[str, list[str]] = {}

    def add(doc_id: str, form: str) -> None:
        forms = found.setdefault(doc_id, [])
        if form not in forms:
            forms.append(form)

    for form, (doc_id, _) in g.nouns.items():
        add(doc_id, form)
    for form, doc_id in g.forms.items():
        add(doc_id, form)
    for phrase, doc_id in g.phrases:
        add(doc_id, phrase)
    for form, pairs in g.separable.items():
        for _, doc_id in pairs:
            add(doc_id, form)
    return found


def _paragraph(text: str) -> str:
    """The first paragraph of a section, as plain text on one line."""
    first = text.strip().split("\n\n", 1)[0]
    return clean(first)


def _sentences(course: Course) -> list[tuple[str, str, str, str]]:
    """(doc id, anchor, German, translation) of every sentence unit and every example."""
    found = []
    for entry in course.entries.values():
        if entry.type in SENTENCE_TYPES:
            for unit in (*entry.units, *entry.variations):
                found.append((entry.id, unit.anchor, unit.german, unit.translation))
        elif entry.type in ("Word", "Verb", "Chunk"):
            for pair in entry.examples:
                found.append((entry.id, "", pair.german, pair.translation))
    return found


def _rows(course: Course, sentences) -> tuple[list[dict], dict[str, list[dict]]]:
    """Cloze rows, one per glossary span, and the sentences where a separable verb is split."""
    rows, split = [], {}
    for doc_id, anchor, german, translation in sentences:
        brackets: dict[str, list[list[int]]] = {}
        for start, end, entry_id, css in find_spans(german, course.glossary):
            if css == "dk-bracket":
                brackets.setdefault(entry_id, []).append([start, end])
                continue
            rows.append({"entry": entry_id, "doc": doc_id, "anchor": anchor, "german": german,
                         "translation": translation, "start": start, "end": end})
        for entry_id, parts in brackets.items():
            split.setdefault(entry_id, []).append({"german": german, "translation": translation, "parts": parts})
    return rows, split


def _pairs(pairs: tuple[Pair, ...]) -> list[dict]:
    return [{"german": p.german, "translation": p.translation} for p in pairs]


def _turn(unit: Unit, me: str) -> dict:
    return {"speaker": unit.speaker, "german": unit.german, "translation": unit.translation,
            "me": unit.speaker.strip().lower() == me.strip().lower()}


def _record(entry: Entry, course: Course, forms: list[str], split: list[dict], has_sentence: bool) -> dict:
    ready = entry.checked != "unchecked" and (entry.type != "Word" or bool(entry.examples) or has_sentence)
    record = {"id": entry.id, "type": entry.type, "title": entry.title, "url": course.url(entry.id),
              "level": entry.level, "translation": entry.translation, "checked": entry.checked, "ready": ready,
              "situations": list(entry.values("Situation")), "topics": list(entry.values("Topic")),
              "date": day(entry.value("Date"))}
    if entry.type in ("Word", "Verb", "Chunk"):
        record["forms"] = forms
        record["examples"] = _pairs(entry.examples)
    if entry.type == "Word":
        plural_only = entry.value("PluralOnly") == "yes"
        record.update(article="" if plural_only else entry.value("Article"), plural=entry.value("Plural"),
                      plural_only=plural_only, regional=list(entry.values("Regional")),
                      noun=entry.is_noun)
    elif entry.type == "Verb":
        record.update(participle=entry.value("Participle"), auxiliary=list(entry.values("Auxiliary")),
                      separable=split)
    elif entry.type == "Chunk":
        record["variants"] = [p.german for p in entry.examples]
    elif entry.type == "Conversation":
        me = entry.value("Me") or "ich"
        record["turns"] = [_turn(unit, me) for unit in entry.units]
    elif entry.type == "Mistake":
        record.update(wrong=_paragraph(entry.sections.get("Wrong", "")),
                      right=_paragraph(entry.sections.get("Right", "")), pattern=entry.value("Pattern"))
    elif entry.type == "Gap":
        record.update(wanted=_paragraph(entry.sections.get("I wanted to say", "")),
                      german=_paragraph(entry.sections.get("In German", "")))
    return record


def build_data(course: Course, config: DeutschkursConfig, title: str, version: str) -> dict:
    """The payload of deutschkurs-data.js (spec 7.1)."""
    rows, split = _rows(course, _sentences(course))
    indexed = {row["entry"] for row in rows} | set(split)
    forms = forms_by_entry(course.glossary)
    entries = [_record(e, course, forms.get(e.id, []), split.get(e.id, []), e.id in indexed)
               for e in course.entries.values() if e.type in PRACTISED]
    situations = [{"title": e.title, "url": course.url(e.id), "next_time": day(e.value("NextTime")),
                   "cando": list(e.cando)} for e in course.by_type("Situation")]
    days = config.prepare_days
    settings = {"learner_level": config.learner_level, "daily_reviews": config.daily_reviews,
                "daily_new": config.daily_new, "weekly_new": config.weekly_new,
                "prepare_days": days if type(days) is int and days >= 0 else 7, "native": config.native}
    return {"version": version, "site": site_id(title), "settings": settings, "entries": entries,
            "sentences": rows, "situations": situations}


def write_data(target: Path, payload: dict) -> int:
    """Write deutschkurs-data.js into the target folder; return its size in bytes."""
    text = PREFIX + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n"
    raw = text.encode("utf-8")
    (Path(target) / FILE).write_bytes(raw)
    return len(raw)
