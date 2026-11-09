"""What entry pages show: the card data and the HTML transforms of the body."""

import html
import re
from typing import Callable

from kb4it.theme import page_name

from .config import DeutschkursConfig
from .course import Course
from .model import LEVELS, Entry

GENDER = {"der": "dk-m", "die": "dk-f", "das": "dk-n"}
PERFEKT = {"haben": "hat", "sein": "ist"}
LIST_ITEM = re.compile(r"<li>(.*?)</li>", re.S)
PARAGRAPH = re.compile(r"^\s*<p>(.*)</p>\s*$", re.S)
TAGS = re.compile(r"<[^>]+>")
SECTION_START = re.compile(r'(?=<div class="kb-sect1">)')


def plain(fragment: str) -> str:
    """Text of an HTML fragment, without tags or entities."""
    return html.unescape(TAGS.sub("", fragment)).strip()


def listen_button(text: str, label: str) -> str:
    say = html.escape(text, quote=True)
    return f'<button type="button" class="dk-listen" data-say="{say}">{html.escape(label)}</button>'


def pairs_html(fragment: str, native: str, listen_label: str) -> str:
    """Turn list items 'German :: translation' into a German span, a Listen button and a translation."""
    lang = html.escape(native, quote=True)

    def item(match: re.Match) -> str:
        inner = match.group(1)
        wrapped = PARAGRAPH.match(inner)
        content = wrapped.group(1) if wrapped else inner
        if "::" not in content:
            return match.group(0)
        german, _, translation = content.partition("::")
        german, translation = german.strip(), translation.strip()
        parts = [f'<span class="dk-de" lang="de">{german}</span>', listen_button(plain(german), listen_label)]
        if translation:
            parts.append(f'<span class="dk-tr dk-no-link" lang="{lang}">{translation}</span>')
        body = " ".join(parts)
        return f'<li class="dk-pair">{f"<p>{body}</p>" if wrapped else body}</li>'

    return LIST_ITEM.sub(item, fragment)


def level_at_least(level: str, other: str) -> bool:
    if level not in LEVELS or other not in LEVELS:
        return False
    return LEVELS.index(level) >= LEVELS.index(other)


def fold_sections(fragment: str, first: str, folded: str, summary: str) -> str:
    """Show section `first` and fold section `folded` in <details> right after it."""
    chunks = SECTION_START.split(fragment)
    find = {name: next((i for i, c in enumerate(chunks) if f'id="{name}"' in c), None) for name in (first, folded)}
    if find[first] is None or find[folded] is None:
        return fragment
    shown, hidden = chunks[find[first]], chunks[find[folded]]
    rest = [c for i, c in enumerate(chunks) if i not in (find[first], find[folded])]
    at = min(find[first], find[folded])
    block = [shown, f'<details class="dk-fold"><summary>{html.escape(summary)}</summary>{hidden}</details>']
    return "".join(rest[:at] + block + rest[at:])


def grammar_order(entry: Entry, config: DeutschkursConfig) -> tuple[str, str]:
    """(shown, folded) section ids of a Grammar page."""
    simple_first = "Simple German" in entry.sections and level_at_least(config.learner_level, config.german_from)
    return ("simple-german", "explanation") if simple_first else ("explanation", "simple-german")


def stress(entry: Entry) -> str:
    """The Stress value, or for a separable verb the prefix stressed."""
    if entry.value("Stress"):
        return entry.value("Stress")
    prefix = entry.value("Prefix")
    if entry.type == "Verb" and entry.value("Separable") == "yes" and prefix and entry.title.startswith(prefix):
        return f"{prefix.upper()}-{entry.title[len(prefix):]}"
    return ""


def perfekt(entry: Entry) -> str:
    aux = "/".join(PERFEKT[a] for a in entry.values("Auxiliary") if a in PERFEKT)
    participle = entry.value("Participle")
    return f"{aux} {participle}".strip() if participle else ""


def card(entry: Entry, course: Course, labels: dict[str, str], url: Callable[[str], str]) -> dict:
    """Everything the entry template shows above the body."""
    headline, css = entry.title, ""
    facts: list[tuple[str, str]] = []
    links: list[tuple[str, list[tuple[str, str]]]] = []

    def fact(label: str, value: str) -> None:
        if value:
            facts.append((labels[label], value))

    if entry.is_noun:
        if entry.value("PluralOnly") == "yes":
            headline, css = f"die {entry.title}", "dk-pl"
            fact("plural", labels["plural_only"])
        else:
            article = entry.value("Article")
            headline, css = f"{article} {entry.title}".strip(), GENDER.get(article, "")
            plural = entry.value("Plural")
            fact("plural", labels["no_plural"] if plural in ("none", "-") else plural)
    if entry.type == "Word":
        fact("part_of_speech", entry.value("PartOfSpeech"))
        fact("forms", ", ".join(entry.values("Forms")))
        fact("regional", ", ".join(entry.values("Regional")))
        family = [_find(course, value) for value in entry.values("Family")]
        if family:
            links.append((labels["family"], [(value, url(found) if found else "") for value, found in
                                             zip(entry.values("Family"), family)]))
    if entry.type == "Verb":
        fact("present", ", ".join(entry.values("Present")))
        fact("preterite", ", ".join(entry.values("Preterite")))
        fact("perfekt", perfekt(entry))
        fact("konjunktiv", entry.value("KonjunktivII"))
        if entry.value("Separable") == "yes":
            fact("separable", f"{entry.value('Prefix')}-")
        fact("irregular", "yes" if entry.value("Irregular") == "yes" else "")
        fact("reflexive", "yes" if entry.value("Reflexive") == "yes" else "")
        fact("government", " ".join(v for v in (entry.value("Government"), entry.value("Preposition")) if v))
    if entry.type == "Grammar":
        fact("area", entry.value("Area"))
        fact("case", entry.value("Case"))
        fact("tense", entry.value("Tense"))
        case = entry.value("Case")
        verbs = [v for v in course.by_type("Verb") if case and v.value("Government") == case]
        if verbs:
            links.append((labels["verbs_with_case"], [(v.title, url(v.id)) for v in verbs]))
    fact("stress", stress(entry))
    if entry.values("Topic"):
        links.append((labels["topic"], [(t, page_name("Topic", t)) for t in entry.values("Topic")]))

    badges = []
    if entry.level:
        badges.append(("dk-badge dk-level", entry.level, page_name("Level", entry.level)))
    if entry.value("Register"):
        badges.append(("dk-badge dk-register", entry.value("Register"), page_name("Register", entry.value("Register"))))
    badges.append((f"dk-badge dk-checked dk-checked-{entry.checked}", entry.checked, ""))
    return {"kind": entry.type, "headline": headline, "headline_class": css, "say": headline,
            "translation": entry.translation, "badges": badges, "facts": facts, "links": links}


def _find(course: Course, value: str) -> str:
    """Id of the entry whose title matches a value such as 'der Terminkalender', or ''."""
    title = re.sub(r"^(der|die|das)\s+", "", value.strip())
    for entry in course.entries.values():
        if entry.type and entry.title == title:
            return entry.id
    return ""
