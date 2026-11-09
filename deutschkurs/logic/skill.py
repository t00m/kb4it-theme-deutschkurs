"""The assistant skill: its page in the site and its files in target/skills/deutschkurs."""

import shutil
from pathlib import Path

import markdown

from .course import Course
from .parse import body

SKILL_DIR = Path(__file__).resolve().parent.parent / "skill" / "deutschkurs"
PUBLISHED = "skills/deutschkurs"


def skill_html() -> str:
    """SKILL.md without its frontmatter, as HTML."""
    text = body((SKILL_DIR / "SKILL.md").read_text(encoding="utf-8"))
    return markdown.markdown(text, extensions=["tables", "fenced_code"])


def site_appendix(course: Course) -> str:
    """Markdown listing the learner's entries: ids, titles, levels and topics, never body text."""
    lines = ["# Your course", "", "Written by the deutschkurs theme on every build. Titles and ids only.", ""]
    for kind in ("Word", "Verb", "Chunk", "Grammar"):
        entries = course.by_type(kind)
        lines += [f"## {kind}", ""]
        lines += [f"- `{e.id}`: {e.title} ({e.level or 'no level'})" for e in entries] or ["- none yet"]
        lines.append("")
    for key in ("Topic", "Level"):
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
