"""The assistant skill: its page in the site and its files in target/skills/deutschkurs."""

import shutil
from pathlib import Path

import markdown

from .course import Course
from .model import NO_LEVEL
from .parse import body

SKILL_DIR = Path(__file__).resolve().parent.parent / "skill" / "deutschkurs"
PUBLISHED = "skills/deutschkurs"
# Inbox documents are raw captures and stay out of the appendix.
TYPES_IN_ORDER = ("Situation", "Conversation", "Text", "Word", "Verb", "Chunk", "Grammar", "Photo", "Mistake", "Gap")


def skill_html() -> str:
    """SKILL.md without its frontmatter, as HTML."""
    text = body((SKILL_DIR / "SKILL.md").read_text(encoding="utf-8"))
    return markdown.markdown(text, extensions=["tables", "fenced_code"])


def _facts(entry) -> str:
    """Level and kind, genre or pattern of an entry, in brackets; the place of a photo; the state of a gap."""
    if entry.type == "Photo":
        return f" ({entry.value('Place')})" if entry.value("Place") else ""
    if entry.type == "Gap":
        return " (to process)" if entry.open_gap else " (processed)"
    if entry.type in NO_LEVEL:
        return ""
    facts = [entry.level or "no level", entry.value("Kind") or entry.value("Genre") or entry.value("Pattern")]
    return f" ({', '.join(fact for fact in facts if fact)})"


def site_appendix(course: Course) -> str:
    """Markdown listing the learner's entries: ids, titles, levels and topics, never body text."""
    lines = ["# Your course", "", "Written by the deutschkurs theme on every build. Titles and ids only.", "",
             "A `Situation` property takes a title of the Situation list, exactly as written here.", ""]
    for kind in TYPES_IN_ORDER:
        entries = course.by_type(kind)
        lines += [f"## {kind}", ""]
        lines += [f"- `{e.id}`: {e.title}{_facts(e)}" for e in entries] or ["- none yet"]
        lines.append("")
    for key in ("Topic", "Level", "Pattern"):
        values = list(course.facet(key))
        lines += [f"## {key} values in use", "", *(f"- {v}" for v in values or ["none yet"]), ""]
    return "\n".join(lines)


def publish(target: Path, course: Course) -> None:
    """Copy the skill into the site and add the learner's appendix."""
    folder = Path(target) / PUBLISHED
    if folder.exists():
        shutil.rmtree(folder)
    shutil.copytree(SKILL_DIR, folder)
    (folder / "reference" / "site.md").write_text(site_appendix(course), encoding="utf-8")
