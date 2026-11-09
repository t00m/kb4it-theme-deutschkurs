"""The course: every entry of the site, its glossary and its problems."""

from dataclasses import dataclass, field
from typing import Callable, Iterable, Mapping, Sequence

from .checks import MetaProblem, check_body, check_properties
from .config import DeutschkursConfig
from .glossary import Glossary, build_glossary
from .model import Entry, entry_from

FOLD = str.maketrans({"ä": "a", "ö": "o", "ü": "u", "ß": "ss", "Ä": "a", "Ö": "o", "Ü": "u"})
Doc = tuple[str, Mapping[str, Sequence[str]], str]


def sort_key(text: str) -> tuple[str, str]:
    """Sort German text case-insensitively, umlauts next to their base letter."""
    return text.translate(FOLD).casefold(), text


def default_url(doc_id: str) -> str:
    return (doc_id[:-3] if doc_id.endswith(".md") else doc_id) + ".html"


@dataclass
class Course:
    entries: dict[str, Entry] = field(default_factory=dict)
    glossary: Glossary = field(default_factory=Glossary)
    problems: list[MetaProblem] = field(default_factory=list)
    urls: dict[str, str] = field(default_factory=dict)

    def url(self, doc_id: str) -> str:
        return self.urls.get(doc_id) or default_url(doc_id)

    def by_type(self, kind: str) -> list[Entry]:
        return sorted((e for e in self.entries.values() if e.type == kind), key=lambda e: sort_key(e.title))

    def typed(self) -> list[Entry]:
        return sorted((e for e in self.entries.values() if e.type), key=lambda e: sort_key(e.title))

    def facet(self, key: str) -> dict[str, list[Entry]]:
        """Typed entries grouped by each value of a property, values sorted."""
        groups: dict[str, list[Entry]] = {}
        for entry in self.typed():
            for value in entry.values(key):
                groups.setdefault(value, []).append(entry)
        return {value: groups[value] for value in sorted(groups, key=sort_key)}


def build_course(docs: Iterable[Doc], config: DeutschkursConfig,
                 url: Callable[[str], str] = default_url) -> Course:
    """Read every document into an Entry, check it and index its forms."""
    course = Course()
    for doc_id, props, markdown in sorted(docs, key=lambda d: d[0]):
        entry = entry_from(doc_id, props, markdown)
        course.entries[doc_id] = entry
        course.urls[doc_id] = url(doc_id)
        course.problems += check_properties(doc_id, props, config.topics)
        course.problems += check_body(entry)
    course.glossary = build_glossary(course.entries.values())
    return course
