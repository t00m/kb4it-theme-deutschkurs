"""The document model: entry types, their properties, sections and allowed values."""

from dataclasses import dataclass, field
from typing import Mapping

from .parse import InboxItem, Pair, Unit, h1, image, inbox_items, pairs, paragraphs, sections, tasks, turns

TYPES = ("Word", "Verb", "Chunk", "Grammar", "Text", "Conversation", "Situation", "Photo", "Mistake", "Gap", "Inbox")
LEVELS = ("A1", "A2", "B1", "B2", "C1", "C2")
CHECKED = ("unchecked", "assistant", "reference", "native", "attested")
REGISTERS = ("du", "Sie", "neutral", "colloquial")
ARTICLES = ("der", "die", "das")
PARTS_OF_SPEECH = ("noun", "adjective", "adverb", "preposition", "conjunction", "pronoun", "particle", "other")
AREAS = ("Verbs", "Nouns", "Cases", "Word order", "Sentences", "Other")
GOVERNMENTS = ("Akkusativ", "Dativ", "Präposition")
AUXILIARIES = ("haben", "sein")
KINDS = ("real", "reconstructed", "model")
GENRES = ("Letter", "School letter", "Official letter", "Notice", "Contract", "Chat", "Email", "Article", "Other")
PLACES = ("Street", "Supermarket", "Station", "School", "Doctor", "Office", "Home", "Shop", "Playground", "Other")
YES = ("yes",)
# Types that need no Level.
NO_LEVEL = ("Situation", "Photo", "Gap", "Inbox")

COMMON = ("Type", "Level", "Topic", "Situation", "Translation", "Checked", "Source", "Date", "Tag")

PROPERTIES: dict[str, tuple[str, ...]] = {
    "Word": COMMON + ("Article", "Plural", "PluralOnly", "PartOfSpeech", "Forms", "Stress", "Regional", "Family"),
    "Verb": COMMON + ("Present", "Preterite", "Participle", "Auxiliary", "Irregular", "Separable", "Prefix",
                      "Reflexive", "Government", "Preposition", "KonjunktivII", "Stress"),
    "Chunk": COMMON + ("Register",),
    "Grammar": COMMON + ("Area", "Case", "Tense", "Pattern", "Marker"),
    "Text": COMMON + ("Genre", "Received", "Deadline", "Reply"),
    "Conversation": COMMON + ("Kind", "Me", "Register"),
    "Situation": COMMON + ("NextTime",),
    "Photo": COMMON + ("Place",),
    "Mistake": COMMON + ("Pattern",),
    "Gap": COMMON,
    "Inbox": COMMON,
}

SECTIONS: dict[str, tuple[str, ...]] = {
    "Word": ("Examples", "Pronunciation", "False friends", "Notes"),
    "Verb": ("Examples", "Typical mistakes", "Notes"),
    "Chunk": ("Variants", "Usage"),
    "Grammar": ("Explanation", "Simple German", "Typical mistakes"),
    "Text": ("Notes",),
    "Conversation": ("Variations", "Notes"),
    "Situation": ("I can", "Log"),
    "Photo": ("Transcription", "Meaning"),
    "Mistake": ("Wrong", "Right", "Why"),
    "Gap": ("I wanted to say", "In German"),
    "Inbox": (),
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
    # Sentence units: the turns of a Conversation or the paragraphs of a Text.
    units: tuple[Unit, ...] = ()
    variations: tuple[Unit, ...] = ()
    # Lines of malformed turns.
    bad_lines: tuple[int, ...] = ()
    # Ticked and total items of "I can".
    cando: tuple[int, int] = (0, 0)
    # The image of a Photo and the captures of an Inbox document.
    image: str = ""
    inbox: tuple[InboxItem, ...] = ()

    def values(self, key: str) -> tuple[str, ...]:
        return tuple(self.props.get(key, ()))

    def value(self, key: str, default: str = "") -> str:
        values = self.values(key)
        return values[0] if values else default

    @property
    def open_gap(self) -> bool:
        """A Gap that has no German yet."""
        return self.type == "Gap" and not self.sections.get("In German", "").strip()

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
    units, variations, bad = (), (), ()
    if kind == "Conversation":
        units, variations, bad = (tuple(found) for found in turns(markdown))
    elif kind == "Text":
        units = tuple(paragraphs(markdown))
    elif kind == "Photo":
        units = tuple(paragraphs(parts.get("Transcription", ""), prefix="p"))
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
        units=units,
        variations=variations,
        bad_lines=bad,
        cando=tasks(parts.get("I can", "")) if kind == "Situation" else (0, 0),
        image=image(markdown) if kind == "Photo" else "",
        inbox=tuple(inbox_items(markdown)) if kind == "Inbox" else (),
    )
