"""Metadata checks: one MetaProblem per invalid or missing property."""

import re
from dataclasses import dataclass
from typing import Mapping, Optional, Sequence

from .model import AREAS, ARTICLES, AUXILIARIES, CHECKED, LEVELS, PARTS_OF_SPEECH, REGISTERS, TYPES, Entry

REASONS = (
    "type_missing", "type_unknown", "level_missing", "level_invalid", "translation_missing",
    "article_missing", "part_of_speech_invalid", "participle_missing", "auxiliary_missing",
    "prefix_missing", "register_invalid", "checked_invalid", "area_invalid", "date_invalid",
    "topic_unknown", "explanation_missing",
)

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}( \d{2}:\d{2}(:\d{2})?)?$")
NEEDS_TRANSLATION = ("Word", "Verb", "Chunk")


@dataclass(frozen=True)
class MetaProblem:
    doc: str
    key: str
    reason: str

    def __str__(self) -> str:
        return f"META_INVALID doc={self.doc} key={self.key} reason={self.reason}"


def check_properties(doc: str, props: Mapping[str, Sequence[str]],
                     topics: Optional[Sequence[str]]) -> list[MetaProblem]:
    """Problems in the properties of one document."""
    problems: list[MetaProblem] = []

    def get(key: str) -> list[str]:
        return [str(v).strip() for v in props.get(key, ()) if str(v).strip()]

    def add(key: str, reason: str) -> None:
        problems.append(MetaProblem(doc, key, reason))

    kind = get("Type")
    if not kind:
        add("Type", "type_missing")
        return problems
    kind = kind[0]
    if kind not in TYPES:
        add("Type", "type_unknown")
        return problems

    level = get("Level")
    if not level:
        add("Level", "level_missing")
    elif level[0] not in LEVELS:
        add("Level", "level_invalid")

    if kind in NEEDS_TRANSLATION and not get("Translation"):
        add("Translation", "translation_missing")

    if kind == "Word":
        pos = get("PartOfSpeech")
        if not pos or pos[0] not in PARTS_OF_SPEECH:
            add("PartOfSpeech", "part_of_speech_invalid")
        elif pos[0] == "noun" and "yes" not in get("PluralOnly"):
            if not any(a in ARTICLES for a in get("Article")):
                add("Article", "article_missing")

    if kind == "Verb":
        if not get("Participle"):
            add("Participle", "participle_missing")
        if not get("Auxiliary") or not set(get("Auxiliary")) <= set(AUXILIARIES):
            add("Auxiliary", "auxiliary_missing")
        if "yes" in get("Separable") and not get("Prefix"):
            add("Prefix", "prefix_missing")

    if kind == "Grammar":
        area = get("Area")
        if not area or area[0] not in AREAS:
            add("Area", "area_invalid")

    if get("Register") and get("Register")[0] not in REGISTERS:
        add("Register", "register_invalid")
    if get("Checked") and get("Checked")[0] not in CHECKED:
        add("Checked", "checked_invalid")
    if get("Date") and not DATE.match(get("Date")[0]):
        add("Date", "date_invalid")
    if topics is not None and any(t not in topics for t in get("Topic")):
        add("Topic", "topic_unknown")
    return problems


def check_body(entry: Entry) -> list[MetaProblem]:
    """Problems in the body sections of one entry."""
    problems = []
    if entry.type == "Grammar" and not entry.sections.get("Explanation", "").strip():
        problems.append(MetaProblem(entry.id, "Explanation", "explanation_missing"))
    return problems
