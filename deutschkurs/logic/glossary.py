"""Glossary: every surface form of an entry, and the transform that links them in HTML."""

import re
from dataclasses import dataclass, field
from typing import Callable, Iterable

from .german import WORD, present_forms, regular_present
from .model import Entry

GENDER = {"der": "dk-m", "die": "dk-f", "das": "dk-n"}
SKIP_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6", "a", "code", "pre", "blockquote", "script", "style",
             "button", "textarea", "select", "head", "title"}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
TAG = re.compile(r"(<!--.*?-->|<[^>]+>)", re.S)
TAG_NAME = re.compile(r"^<\s*(/)?\s*([a-zA-Z][a-zA-Z0-9]*)")
ENTITY = re.compile(r"(&#?\w+;)")
CLAUSE_END = re.compile(r"[.,;:!?]")
ARTICLE = re.compile(r"^(der|die|das)\s+", re.I)


@dataclass
class Glossary:
    # Exact noun forms to (entry id, css class).
    nouns: dict[str, tuple[str, str]] = field(default_factory=dict)
    # Lower-cased forms of other words to entry id.
    forms: dict[str, str] = field(default_factory=dict)
    # Chunk text, lower-cased, to entry id; longest first.
    phrases: list[tuple[str, str]] = field(default_factory=list)
    # Finite form of a separable verb, lower-cased, to (prefix, entry id).
    separable: dict[str, tuple[str, str]] = field(default_factory=dict)

    def lookup(self, token: str) -> tuple[str, str] | None:
        """(entry id, css class) of a token, or None."""
        if token in self.nouns:
            return self.nouns[token]
        if token.lower() in self.forms and token not in self.nouns:
            return self.forms[token.lower()], ""
        return None


def _strip_article(value: str) -> str:
    return ARTICLE.sub("", value.strip())


def build_glossary(entries: Iterable[Entry]) -> Glossary:
    """Index the surface forms of every Word, Verb and Chunk."""
    g = Glossary()
    phrases = {}
    for e in entries:
        if e.type == "Word" and e.is_noun:
            plural_only = e.value("PluralOnly") == "yes"
            gender = "dk-pl" if plural_only else GENDER.get(e.value("Article"), "")
            for form in [e.title, *e.values("Forms")]:
                g.nouns.setdefault(form.strip(), (e.id, gender))
            for plural in e.values("Plural"):
                if plural.strip() not in ("none", "-"):
                    g.nouns.setdefault(_strip_article(plural), (e.id, "dk-pl"))
        elif e.type == "Word":
            for form in [e.title, *e.values("Forms")]:
                g.forms.setdefault(form.strip().lower(), e.id)
        elif e.type == "Verb":
            prefix = e.value("Prefix") if e.value("Separable") == "yes" else ""
            finite = present_forms(e.values("Present"), prefix) or regular_present(e.title, prefix)
            finite += present_forms(e.values("Preterite"), prefix)
            for form in [e.title, *e.values("Participle")]:
                g.forms.setdefault(form.strip().lower(), e.id)
            for form in finite:
                if prefix:
                    g.separable.setdefault(form.lower(), (prefix, e.id))
                else:
                    g.forms.setdefault(form.lower(), e.id)
        elif e.type == "Chunk" and e.title:
            phrases[e.title.lower()] = e.id
    g.phrases = sorted(phrases.items(), key=lambda item: -len(item[0]))
    return g


def _anchor(text: str, href: str, css: str) -> str:
    classes = " ".join(c for c in ("dk-link", css) if c)
    return f'<a class="{classes}" href="{href}">{text}</a>'


def _link_text(text: str, g: Glossary, self_id: str, url: Callable[[str], str]) -> str:
    """Link the words of one plain text piece (no tags, no entities)."""
    spans: list[tuple[int, int, str, str]] = []
    taken = [False] * len(text)

    def free(start: int, end: int) -> bool:
        return not any(taken[start:end])

    def take(start: int, end: int, doc_id: str, css: str) -> None:
        spans.append((start, end, doc_id, css))
        for i in range(start, end):
            taken[i] = True

    lower = text.lower()
    for phrase, doc_id in g.phrases:
        for m in re.finditer(r"(?<![\wÄÖÜäöüß])" + re.escape(phrase) + r"(?![\wÄÖÜäöüß])", lower):
            if doc_id != self_id and free(m.start(), m.end()):
                take(m.start(), m.end(), doc_id, "")

    words = list(WORD.finditer(text))
    for i, m in enumerate(words):
        sep = g.separable.get(m.group().lower())
        if not sep or not free(m.start(), m.end()):
            continue
        prefix, doc_id = sep
        end = CLAUSE_END.search(text, m.end())
        limit = end.start() if end else len(text)
        clause = [w for w in words[i + 1:] if w.end() <= limit]
        if clause and clause[-1].group() == prefix and doc_id != self_id:
            take(m.start(), m.end(), doc_id, "dk-bracket")
            take(clause[-1].start(), clause[-1].end(), doc_id, "dk-bracket")

    for m in words:
        if not free(m.start(), m.end()):
            continue
        found = g.lookup(m.group())
        if found and found[0] != self_id:
            take(m.start(), m.end(), found[0], found[1])

    out, pos = [], 0
    for start, end, doc_id, css in sorted(spans):
        out.append(text[pos:start])
        out.append(_anchor(text[start:end], url(doc_id), css))
        pos = end
    out.append(text[pos:])
    return "".join(out)


def link_html(html: str, glossary: Glossary, self_id: str, url: Callable[[str], str]) -> str:
    """Link glossary forms in the text of html, outside headings, links, code and quotes."""
    stack: list[tuple[str, bool]] = []
    out = []
    for piece in TAG.split(html):
        if not piece:
            continue
        if piece.startswith("<"):
            out.append(piece)
            m = TAG_NAME.match(piece)
            if not m:
                continue
            closing, name = m.group(1), m.group(2).lower()
            if closing:
                while stack:
                    if stack.pop()[0] == name:
                        break
            elif name not in VOID_TAGS and not piece.rstrip().endswith("/>"):
                skip = name in SKIP_TAGS or "dk-no-link" in piece
                stack.append((name, skip))
            continue
        if any(skip for _, skip in stack):
            out.append(piece)
            continue
        for part in ENTITY.split(piece):
            out.append(part if ENTITY.fullmatch(part) else _link_text(part, glossary, self_id, url))
    return "".join(out)
