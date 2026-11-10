"""Metadata checks: one MetaProblem per invalid or missing property."""

import re
from datetime import datetime
from dataclasses import dataclass
from typing import Collection, Mapping, Optional, Sequence

from .model import (AREAS, ARTICLES, AUXILIARIES, CHECKED, GENRES, KINDS, LEVELS, NO_LEVEL, PARTS_OF_SPEECH,
                    REGISTERS, TYPES, Entry)

REASONS = (
    "type_missing", "type_unknown", "level_missing", "level_invalid", "translation_missing",
    "article_missing", "part_of_speech_invalid", "participle_missing", "auxiliary_missing",
    "prefix_missing", "register_invalid", "checked_invalid", "area_invalid", "date_invalid",
    "topic_unknown", "explanation_missing", "flag_invalid", "kind_missing", "kind_invalid", "genre_invalid",
    "situation_unknown", "turn_invalid",
)

FLAGS = ("PluralOnly", "Irregular", "Separable", "Reflexive", "Reply")
DATES = ("Date", "NextTime", "Received", "Deadline")

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}( \d{2}:\d{2}(:\d{2})?)?$")
NEEDS_TRANSLATION = ("Word", "Verb", "Chunk")


@dataclass(frozen=True)
class MetaProblem:
    doc: str
    key: str
    reason: str
    line: int = 0

    def __str__(self) -> str:
        where = f" line={self.line}" if self.line else ""
        return f"META_INVALID doc={self.doc} key={self.key} reason={self.reason}{where}"


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
        if kind not in NO_LEVEL:
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

    if kind == "Conversation":
        if not get("Kind"):
            add("Kind", "kind_missing")
        elif get("Kind")[0] not in KINDS:
            add("Kind", "kind_invalid")

    if kind == "Text" and get("Genre") and get("Genre")[0] not in GENRES:
        add("Genre", "genre_invalid")

    if get("Register") and get("Register")[0] not in REGISTERS:
        add("Register", "register_invalid")
    if get("Checked") and get("Checked")[0] not in CHECKED:
        add("Checked", "checked_invalid")
    for flag in FLAGS:
        if get(flag) and get(flag) != ["yes"]:
            add(flag, "flag_invalid")
    for key in DATES:
        if get(key) and not real_date(get(key)[0]):
            add(key, "date_invalid")
    if topics is not None and any(t not in topics for t in get("Topic")):
        add("Topic", "topic_unknown")
    return problems


def real_date(value: str) -> bool:
    """True for YYYY-MM-DD, optionally with HH:MM or HH:MM:SS, that is a real calendar date."""
    if not DATE.match(value):
        return False
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            datetime.strptime(value, fmt)
            return True
        except ValueError:
            continue
    return False


def check_body(entry: Entry, situations: Optional[Collection[str]] = None) -> list[MetaProblem]:
    """Problems in the body of one entry; with the situation titles, also unknown Situation values."""
    problems = []
    if entry.type == "Grammar" and not entry.sections.get("Explanation", "").strip():
        problems.append(MetaProblem(entry.id, "Explanation", "explanation_missing"))
    for line in entry.bad_lines:
        problems.append(MetaProblem(entry.id, "Turn", "turn_invalid", line))
    if situations is not None and entry.type and any(s not in situations for s in entry.values("Situation")):
        problems.append(MetaProblem(entry.id, "Situation", "situation_unknown"))
    return problems
