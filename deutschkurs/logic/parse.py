"""Read the parts of a Markdown source the theme needs: H1, sections, translation pairs."""

import re
from dataclasses import dataclass

SECTION = re.compile(r"^## (.+?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")
ITEM = re.compile(r"^\s*[-*+]\s+(.*)$")
TOP_ITEM = re.compile(r"^[-*+]\s+(.*)$")
TURN = re.compile(r"^(\*\*|__)([^*_]+?)(?::\1|\1:)\s*(.*)$")
VARIATION = re.compile(r"^(\d+)\s+(.*)$")
TASK = re.compile(r"^\s*[-*+]\s+\[([ xX])\]\s")
MARKUP = re.compile(r"[*_`]")
IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
IMAGE_SRC = re.compile(r"!\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
LEADING_DATE = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:\s+|$)")
LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
HTML_TAG = re.compile(r"<[^>]+>")
INLINE_TAGS = "a|abbr|b|br|code|em|i|img|kbd|mark|s|small|span|strong|sub|sup|u"
# First lines of blocks that are no paragraph: headings, quotes, lists, tables, code, rules, boxes, block HTML.
NOT_A_PARAGRAPH = re.compile(r"^(#|>|[-*+]\s|\d+[.)]\s|\||```|~~~|!!!|\s{4}|\t|(-{3,}|\*{3,}|_{3,})\s*$"
                             rf"|<(?!/?(?:{INLINE_TAGS})\b))")


@dataclass(frozen=True)
class Pair:
    german: str
    translation: str


@dataclass(frozen=True)
class Unit:
    """One German sentence unit: a turn, a variation of a turn or a paragraph of a text."""
    anchor: str
    german: str
    translation: str = ""
    speaker: str = ""
    line: int = 0
    replaces: int = 0


@dataclass(frozen=True)
class InboxItem:
    """One capture of an Inbox document: its date as written, its text and the src of an image in it."""
    date: str
    text: str
    image: str = ""
    line: int = 0


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


def _numbered_body(markdown: str):
    """Yield (line number in the file, line, in_code) for the lines after the frontmatter."""
    lines = markdown.splitlines()
    start = 0
    if lines and lines[0].strip() == "---":
        for n, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                start = n + 1
                break
    in_code = False
    for n, line in enumerate(lines[start:], start=start + 1):
        if FENCE.match(line):
            in_code = not in_code
            yield n, line, True
            continue
        yield n, line, in_code


def clean(text: str) -> str:
    """German text without Markdown emphasis marks, on one line."""
    text = HTML_TAG.sub("", LINK.sub(r"\1", IMAGE.sub("", text)))
    return " ".join(MARKUP.sub("", text).split())


def _split(text: str) -> tuple[str, str]:
    german, sep, translation = text.partition("::")
    return clean(german), translation.strip() if sep else ""


def turns(markdown: str) -> tuple[list[Unit], list[Unit], list[int]]:
    """Turns of a conversation, its variations and the lines of malformed items.

    The turns are the items of the first list before any section. A malformed item keeps its number.
    """
    found: list[Unit] = []
    variations: list[Unit] = []
    bad: list[int] = []
    section = None
    list_open, list_done = False, False
    for n, line, in_code in _numbered_body(markdown):
        if in_code:
            continue
        heading = SECTION.match(line)
        if heading:
            section = heading.group(1).strip()
            continue
        item = TOP_ITEM.match(line)
        if section is None:
            if list_done:
                continue
            if not item:
                # A paragraph after the list closes it; blank and indented lines do not.
                if list_open and line.strip() and not line.startswith((" ", "\t")):
                    list_done = True
                continue
            list_open = True
            turn = TURN.match(item.group(1))
            anchor = f"t{len(found) + 1}"
            if turn:
                german, translation = _split(turn.group(3))
                found.append(Unit(anchor, german, translation, turn.group(2).strip(), n))
            else:
                german, translation = _split(item.group(1))
                found.append(Unit(anchor, german, translation, "", n))
                bad.append(n)
        elif section == "Variations" and item:
            numbered = VARIATION.match(item.group(1))
            turn = TURN.match(numbered.group(2)) if numbered else None
            if not turn:
                bad.append(n)
                continue
            german, translation = _split(turn.group(3))
            variations.append(Unit(f"v{len(variations) + 1}", german, translation, turn.group(2).strip(), n,
                                   int(numbered.group(1))))
    return found, variations, bad


def paragraphs(markdown: str, prefix: str = "s") -> list[Unit]:
    """German paragraphs of a text before its first section, each with the blockquote that follows it."""
    blocks: list[tuple[int, list[str]]] = []
    current: list[str] = []
    seen_title = False
    for n, line, in_code in _numbered_body(markdown):
        if not in_code and SECTION.match(line):
            break
        if not in_code and not seen_title and line.startswith("# "):
            seen_title = True
            continue
        if not line.strip() and not in_code:
            current = []
            continue
        text = "```" if in_code else line
        # A quote or a code block right after a paragraph starts a block of its own, and so does text after code.
        if current and text.startswith((">", "```")) != current[0].startswith((">", "```")):
            if not current[0].startswith(">"):
                current = []
        if not current:
            blocks.append((n, current))
        current.append(text)
    units: list[Unit] = []
    for i, (n, lines) in enumerate(blocks):
        german = clean(" ".join(lines))
        # A paragraph that holds only images has no text.
        if NOT_A_PARAGRAPH.match(lines[0]) or not german:
            continue
        translation = ""
        if i + 1 < len(blocks) and blocks[i + 1][1][0].startswith(">"):
            translation = " ".join(l.lstrip(">").strip() for l in blocks[i + 1][1]).strip()
        units.append(Unit(f"{prefix}{len(units) + 1}", german, translation, "", n))
    return units


def tasks(text: str) -> tuple[int, int]:
    """(ticked, total) task list items of a section."""
    marks = [m.group(1) for m in map(TASK.match, text.splitlines()) if m]
    return sum(1 for mark in marks if mark in "xX"), len(marks)


def image(markdown: str) -> str:
    """The src of the first image before the first section, or ''."""
    for _, line, in_code in _numbered_body(markdown):
        if in_code:
            continue
        if SECTION.match(line):
            break
        match = IMAGE_SRC.search(line)
        if match:
            return match.group(1)
    return ""


def inbox_items(markdown: str) -> list[InboxItem]:
    """Top-level list items of an Inbox document, one capture each."""
    items = []
    for n, line, in_code in _numbered_body(markdown):
        match = None if in_code else TOP_ITEM.match(line)
        if not match:
            continue
        text = match.group(1).strip()
        date = ""
        dated = LEADING_DATE.match(text)
        if dated:
            date, text = dated.group(1), text[dated.end():]
        found = IMAGE_SRC.search(text)
        src = found.group(1) if found else ""
        text = " ".join(IMAGE.sub("", text).split())
        items.append(InboxItem(date, text, src, n))
    return items
