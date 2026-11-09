"""Read the parts of a Markdown source the theme needs: H1, sections, translation pairs."""

import re
from dataclasses import dataclass

SECTION = re.compile(r"^## (.+?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")
ITEM = re.compile(r"^\s*[-*+]\s+(.*)$")


@dataclass(frozen=True)
class Pair:
    german: str
    translation: str


def body(markdown: str) -> str:
    """The source without its YAML frontmatter."""
    lines = markdown.splitlines()
    if lines and lines[0].strip() == "---":
        for n, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                return "\n".join(lines[n + 1:])
    return markdown


def _lines_outside_code(text: str):
    """Yield (line, in_code) for every line."""
    in_code = False
    for line in text.splitlines():
        if FENCE.match(line):
            in_code = not in_code
            yield line, True
            continue
        yield line, in_code


def h1(markdown: str) -> str:
    """Text of the first level-1 heading, or ''."""
    for line, in_code in _lines_outside_code(body(markdown)):
        if not in_code and line.startswith("# "):
            return line[2:].strip().rstrip("#").strip()
    return ""


def sections(markdown: str) -> dict[str, str]:
    """Level-2 headings and their raw bodies, in source order."""
    result: dict[str, list[str]] = {}
    current = None
    for line, in_code in _lines_outside_code(body(markdown)):
        match = None if in_code else SECTION.match(line)
        if match:
            current = match.group(1).strip()
            result[current] = []
        elif not in_code and line.startswith("# "):
            current = None
        elif current is not None:
            result[current].append(line)
    return {name: "\n".join(lines).strip("\n") for name, lines in result.items()}


def pairs(text: str) -> list[Pair]:
    """List items written as 'German :: translation'."""
    result = []
    for line in text.splitlines():
        match = ITEM.match(line)
        if not match:
            continue
        german, sep, translation = match.group(1).partition("::")
        result.append(Pair(german.strip(), translation.strip() if sep else ""))
    return result
