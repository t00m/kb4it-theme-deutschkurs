"""The course: every entry of the site, its glossary and its problems."""

from dataclasses import dataclass, field
from typing import Callable, Iterable, Mapping, Sequence

from .checks import MetaProblem, check_body, check_properties
from .config import DeutschkursConfig
from .german import sort_key
from .glossary import Glossary, build_glossary
from .index import Coverage, Occurrence, build_index, coverage
from .model import Entry, entry_from

Doc = tuple[str, Mapping[str, Sequence[str]], str]


def default_url(doc_id: str) -> str:
    return (doc_id[:-3] if doc_id.endswith(".md") else doc_id) + ".html"


@dataclass
class Course:
    entries: dict[str, Entry] = field(default_factory=dict)
    glossary: Glossary = field(default_factory=Glossary)
    problems: list[MetaProblem] = field(default_factory=list)
    urls: dict[str, str] = field(default_factory=dict)
    # Entry id to the sentences it appears in.
    index: dict[str, list[Occurrence]] = field(default_factory=dict)
    # Id of a Text or Conversation to its coverage.
    coverage: dict[str, Coverage] = field(default_factory=dict)
    # Title of a Situation to its id.
    situations: dict[str, str] = field(default_factory=dict)

    def url(self, doc_id: str) -> str:
        return self.urls.get(doc_id) or default_url(doc_id)

    def by_type(self, kind: str) -> list[Entry]:
        return sorted((e for e in self.entries.values() if e.type == kind), key=lambda e: sort_key(e.title))

    def typed(self) -> list[Entry]:
        return sorted((e for e in self.entries.values() if e.type), key=lambda e: sort_key(e.title))

    def in_situation(self, title: str) -> list[Entry]:
        """Typed entries whose Situation is this title."""
        return [e for e in self.typed() if title in e.values("Situation")]

    def facet(self, key: str) -> dict[str, list[Entry]]:
        """Typed entries grouped by each value of a property, values sorted."""
        groups: dict[str, list[Entry]] = {}
        for entry in self.typed():
            for value in entry.values(key):
                groups.setdefault(value, []).append(entry)
        return {value: groups[value] for value in sorted(groups, key=sort_key)}


def build_course(docs: Iterable[Doc], config: DeutschkursConfig,
                 url: Callable[[str], str] = default_url) -> Course:
    """Read every document into an Entry, check it and index its forms and sentences."""
    course = Course()
    docs = sorted(docs, key=lambda d: d[0])
    for doc_id, props, markdown in docs:
        entry = entry_from(doc_id, props, markdown)
        course.entries[doc_id] = entry
        course.urls[doc_id] = url(doc_id)
        if entry.type == "Situation" and entry.title:
            course.situations.setdefault(entry.title, doc_id)
    for doc_id, props, _ in docs:
        course.problems += check_properties(doc_id, props, config.topics)
        course.problems += check_body(course.entries[doc_id], course.situations)
    course.glossary = build_glossary(course.entries.values())
    course.index = build_index(course.entries.values(), course.glossary)
    known = frozenset(str(word).lower() for word in config.known_words or ())
    for entry in course.entries.values():
        if entry.type in ("Text", "Conversation"):
            course.coverage[entry.id] = coverage((*entry.units, *entry.variations), course.glossary, known)
    return course
