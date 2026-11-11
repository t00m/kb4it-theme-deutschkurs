"""Sentence index: where each entry appears in texts and conversations, and how much of them is known."""

import re
from dataclasses import dataclass
from typing import Collection, Iterable, Sequence

from .german import BASIC, WORD, sort_key
from .glossary import Glossary, find_spans
from .model import Entry
from .parse import Unit

SOURCES = ("Text", "Photo", "Conversation")
# Real sources first, model conversations last.
RANK = {"Text": 0, "Photo": 1, "real": 2, "reconstructed": 3}
PLACEHOLDER = re.compile(r"\[[^\]]*\]")
SENTENCE_END = re.compile(r"(^|[.!?:])[\s\"'„“”»«()*-]*$")
TITLES = ("Herr", "Frau")


@dataclass(frozen=True)
class Occurrence:
    """One sentence unit of a document."""
    doc: str
    anchor: str
    german: str
    translation: str
    title: str
    kind: str


@dataclass(frozen=True)
class Coverage:
    """Distinct words of a document and the ones without an entry."""
    total: int
    covered: int
    missing: tuple[str, ...]

    @property
    def percent(self) -> int:
        return round(100 * self.covered / self.total) if self.total else 100


def _sources(entries: Iterable[Entry]) -> list[Entry]:
    def rank(entry: Entry) -> int:
        return RANK.get(entry.type, RANK.get(entry.value("Kind"), 4))
    found = [e for e in entries if e.type in SOURCES]
    return sorted(found, key=lambda e: (rank(e), sort_key(e.title), e.id))


def _occurrence(entry: Entry, unit: Unit) -> Occurrence:
    return Occurrence(entry.id, unit.anchor, unit.german, unit.translation, entry.title, entry.value("Kind"))


def build_index(entries: Iterable[Entry], glossary: Glossary) -> dict[str, list[Occurrence]]:
    """Entry id to the sentence units that hold one of its forms, real sources first."""
    index: dict[str, list[Occurrence]] = {}
    for entry in _sources(entries):
        for unit in (*entry.units, *entry.variations):
            for doc_id in dict.fromkeys(span[2] for span in find_spans(unit.german, glossary)):
                index.setdefault(doc_id, []).append(_occurrence(entry, unit))
    return index


def coverage(units: Sequence[Unit], glossary: Glossary, known: Collection[str]) -> Coverage:
    """Count the distinct words of the units; a word is covered by an entry, a basic word or a known word.

    Left out: single letters, the name after Herr or Frau, and placeholders such as [Adresse].
    """
    covered: set[str] = set()
    shown: dict[str, tuple[bool, str]] = {}
    for unit in units:
        text = PLACEHOLDER.sub(lambda m: " " * len(m.group()), unit.german)
        spans = find_spans(text, glossary)
        previous = ""
        for m in WORD.finditer(text):
            word, after_title = m.group(), previous in TITLES
            previous = word
            if len(word) < 2 or after_title:
                continue
            key = word.lower()
            inside = not SENTENCE_END.search(text[:m.start()])
            # Prefer the spelling seen inside a sentence: there the capital letter means a noun.
            if key not in shown or (inside and not shown[key][0]):
                shown[key] = (inside, word)
            if key in BASIC or key in known or any(a < m.end() and m.start() < b for a, b, _, _ in spans):
                covered.add(key)
    missing = sorted((form for key, (_, form) in shown.items() if key not in covered), key=sort_key)
    return Coverage(len(shown), len(covered), tuple(missing))


def marker_hits(markers: Sequence[str], entries: Iterable[Entry]) -> list[Occurrence]:
    """Sentence units that hold one of the marker words as a whole word."""
    wanted = {m.strip().lower() for m in markers if m.strip()}
    if not wanted:
        return []
    hits = []
    for entry in _sources(entries):
        for unit in (*entry.units, *entry.variations):
            if wanted & {w.lower() for w in WORD.findall(unit.german)}:
                hits.append(_occurrence(entry, unit))
    return hits
