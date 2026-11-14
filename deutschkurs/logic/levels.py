"""The study path of each level: what to learn, in which order."""

from urllib.parse import quote

from .checks import step
from .course import Course
from .german import sort_key
from .model import LEVELS, PARTS_OF_SPEECH, Entry
from .render import GENDER, cued, facet_page

# Sections of a level page, in study order: label key, entry type and the hint shown under the heading.
STUDY = (("grammar", "Grammar"), ("conversations", "Conversation"), ("texts", "Text"), ("chunks", "Chunk"),
         ("verbs", "Verb"), ("vocabulary", "Word"), ("mistakes", "Mistake"), ("photos", "Photo"),
         ("situations", "Situation"))
# Sections whose entries are listed one per line with their details; the others are short inline lists.
DETAILED = ("Grammar", "Conversation", "Text", "Mistake")
# What the overview counts for each level.
COUNTED = ("Grammar", "Conversation", "Text", "Chunk", "Verb", "Word")


def study_order(entry: Entry, course: Course) -> tuple:
    """Entries with a Step first, by that number; then the others, the best covered first, then by title.

    Coverage (the share of words the course already knows) only exists for texts and conversations, so it puts
    the easiest of them first; every other entry has none and keeps the order of its title."""
    number = step(entry.value("Step"))
    if number is not None:
        return (0, number, 0, sort_key(entry.title))
    found = course.coverage.get(entry.id)
    percent = found.percent if found is not None and found.total else 0
    return (1, 0, -percent, sort_key(entry.title))


def levels_in_use(course: Course) -> list[str]:
    """The levels that typed entries use, from A1 up."""
    used = {e.level for e in course.typed() if e.level}
    return [level for level in LEVELS if level in used]


def practice_link(level: str) -> str:
    return f"practice.html#level={quote(level, safe='')}"


def _item(entry: Entry, course: Course) -> dict:
    found = course.coverage.get(entry.id)
    title, css = entry.title, ""
    if entry.is_noun:
        plural_only = entry.value("PluralOnly") == "yes"
        article = "die" if plural_only else entry.value("Article")
        css = cued("dk-pl" if plural_only else GENDER.get(article, ""))
        title = f"{article} {entry.title}" if article else entry.title
    return {"title": title, "href": course.url(entry.id), "css": css, "translation": entry.translation,
            "situations": list(entry.values("Situation")),
            "coverage": f"{found.percent} %" if found is not None and found.total else ""}


def level_plan(course: Course, level: str, labels) -> list[dict]:
    """The sections of the study page of one level, in study order, without the empty ones."""
    entries = [e for e in course.typed() if e.level == level]
    sections = []
    for key, kind in STUDY:
        found = sorted((e for e in entries if e.type == kind), key=lambda e: study_order(e, course))
        if not found:
            continue
        section = {"key": key, "label": labels[key], "hint": labels.get(f"study_{key}", ""), "count": len(found),
                   "detailed": kind in DETAILED, "items": [], "groups": []}
        if kind == "Word":
            # Words by part of speech, in the order of the word classes; nouns with their article.
            for pos in PARTS_OF_SPEECH + ("",):
                words = [e for e in found if (e.value("PartOfSpeech") if e.value("PartOfSpeech") in PARTS_OF_SPEECH
                                              else "") == pos]
                if words:
                    section["groups"].append((pos or labels["other"], [_item(e, course) for e in words]))
        else:
            section["items"] = [_item(e, course) for e in found]
        sections.append(section)
    return sections


def level_cards(course: Course, labels, learner_level: str) -> list[dict]:
    """One card per level in use: its counts, its page and whether it is the learner's level."""
    cards = []
    for level in levels_in_use(course):
        entries = [e for e in course.typed() if e.level == level]
        counts = [(labels[key], sum(1 for e in entries if e.type == kind))
                  for key, kind in STUDY if kind in COUNTED]
        cards.append({"level": level, "href": facet_page("Level", level), "practice": practice_link(level),
                      "counts": [(label, n) for label, n in counts if n], "mine": level == learner_level})
    return cards
