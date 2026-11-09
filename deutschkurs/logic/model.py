"""The document model: entry types, their properties, sections and allowed values."""

from dataclasses import dataclass, field
from typing import Mapping

from .parse import Pair, h1, pairs, sections

TYPES = ("Word", "Verb", "Chunk", "Grammar")
LEVELS = ("A1", "A2", "B1", "B2", "C1", "C2")
CHECKED = ("unchecked", "assistant", "reference", "native", "attested")
REGISTERS = ("du", "Sie", "neutral", "colloquial")
ARTICLES = ("der", "die", "das")
PARTS_OF_SPEECH = ("noun", "adjective", "adverb", "preposition", "conjunction", "pronoun", "particle", "other")
AREAS = ("Verbs", "Nouns", "Cases", "Word order", "Sentences", "Other")
GOVERNMENTS = ("Akkusativ", "Dativ", "Präposition")
AUXILIARIES = ("haben", "sein")
YES = ("yes",)

COMMON = ("Type", "Level", "Topic", "Situation", "Translation", "Checked", "Source", "Date", "Tag")

PROPERTIES: dict[str, tuple[str, ...]] = {
    "Word": COMMON + ("Article", "Plural", "PluralOnly", "PartOfSpeech", "Forms", "Stress", "Regional", "Family"),
    "Verb": COMMON + ("Present", "Preterite", "Participle", "Auxiliary", "Irregular", "Separable", "Prefix",
                      "Reflexive", "Government", "Preposition", "KonjunktivII", "Stress"),
    "Chunk": COMMON + ("Register",),
    "Grammar": COMMON + ("Area", "Case", "Tense", "Pattern", "Marker"),
}

SECTIONS: dict[str, tuple[str, ...]] = {
    "Word": ("Examples", "Pronunciation", "False friends", "Notes"),
    "Verb": ("Examples", "Typical mistakes", "Notes"),
    "Chunk": ("Variants", "Usage"),
    "Grammar": ("Explanation", "Simple German", "Typical mistakes"),
}

# Section that holds the example sentences of each type.
EXAMPLES = {"Word": "Examples", "Verb": "Examples", "Chunk": "Variants"}


@dataclass(frozen=True)
class Entry:
    id: str
    type: str
    title: str
    level: str = ""
    translation: str = ""
    checked: str = "unchecked"
    props: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    sections: Mapping[str, str] = field(default_factory=dict)
    examples: tuple[Pair, ...] = ()

    def values(self, key: str) -> tuple[str, ...]:
        return tuple(self.props.get(key, ()))

    def value(self, key: str, default: str = "") -> str:
        values = self.values(key)
        return values[0] if values else default

    @property
    def is_noun(self) -> bool:
        return self.type == "Word" and self.value("PartOfSpeech") == "noun"


def entry_from(doc_id: str, props: Mapping[str, tuple[str, ...]], markdown: str) -> Entry:
    """Build an Entry from a document's properties and its Markdown source."""
    props = {key: tuple(values) for key, values in props.items()}

    def first(key: str, default: str = "") -> str:
        values = props.get(key, ())
        return values[0] if values else default

    kind = first("Type")
    parts = sections(markdown)
    examples = tuple(pairs(parts.get(EXAMPLES.get(kind, ""), "")))
    return Entry(
        id=doc_id,
        type=kind,
        title=h1(markdown) or doc_id,
        level=first("Level"),
        translation=", ".join(props.get("Translation", ())),
        checked=first("Checked", "unchecked"),
        props=props,
        sections=parts,
        examples=examples,
    )
