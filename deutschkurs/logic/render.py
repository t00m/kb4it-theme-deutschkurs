"""What entry pages show: the card data and the HTML transforms of the body."""

import html
import re
from urllib.parse import quote
from typing import Callable, Mapping, Sequence

from kb4it.theme import page_name

from .checks import real_date
from .config import DeutschkursConfig
from .course import Course
from .glossary import TAG, TAG_NAME, VOID_TAGS
from .index import Occurrence, marker_hits
from .model import KINDS, LEVELS, Entry
from .parse import AUDIO_EXTENSIONS, Unit

GENDER = {"der": "dk-m", "die": "dk-f", "das": "dk-n"}
PERFEKT = {"haben": "hat", "sein": "ist"}
FACET_KEYS = ("Level", "Topic", "Register", "Kind", "Genre", "Place", "Pattern", "PartOfSpeech")
# Label of a facet whose key is not its label key in lower case.
FACET_LABELS = {"PartOfSpeech": "part_of_speech"}
# The article pages Article.html and Article_<article>.html.
ARTICLE_KEY = "Article"
# Kind.html and the Word page kind.html are one file where file names ignore case.
FACET_PAGES = {"Kind": "ConversationKind"}
# Lists a Situation page shows, in order: label and entry type.
RELATED = (("conversations", "Conversation"), ("texts", "Text"), ("vocabulary", "Word"), ("verbs", "Verb"),
           ("chunks", "Chunk"), ("grammar", "Grammar"))
INDEXED = ("Word", "Verb", "Chunk")
MAX_SENTENCES = 10
# Checked values whose facts no person or reference has confirmed.
UNVERIFIED = ("unchecked", "assistant")
IMG_TAG = re.compile(r"<img\b(?![^>]*\bloading=)")
LIST_ITEM = re.compile(r'<li( class="task-list-item")?>(.*?)</li>', re.S)
PARAGRAPH = re.compile(r"^\s*<p>(.*)</p>\s*$", re.S)
CHECKBOX = re.compile(r"^\s*(<input\b[^>]*>)\s*")
TAGS = re.compile(r"<[^>]+>")
SECTION_START = re.compile(r'(?=<div class="kb-sect1">)')
SECTION_WRAPPER = re.compile(r'^<div class="(kb-sect\d+|sectionbody)[" ]')
VARIATIONS = re.compile(r'<h2\b[^>]*\bid="variations"')
BLOCK = re.compile(r"<(ul|ol|p|div|blockquote|pre|table|details)\b")
TURN = re.compile(r"^<(strong|b)>([^<]+?)(?::</\1>|</\1>:)\s*(.*)$", re.S)
NUMBERED = re.compile(r"^(\d+)\s+(.*)$", re.S)
NOT_A_LETTER = re.compile(r"[\W_]+")
# The [audio](...) link of a turn after Markdown.
RENDERED_AUDIO = re.compile(rf'\s*<a href="([^"]+{AUDIO_EXTENSIONS})"[^>]*>audio</a>', re.I)
REMOTE = ("http://", "https://", "//")
AUDIO_FILE = re.compile(rf"{AUDIO_EXTENSIONS}$", re.I)


def cued(css: str) -> str:
    """A gender class with the cue that names the gender in letters (spec 6.1), or '' without a gender."""
    return f"{css} dk-cued" if css else ""


def has_plural(value: str) -> bool:
    """True for a Plural value that names a plural form."""
    return bool(value) and value not in ("none", "-")


def facet_page(key: str, value: str | None = None) -> str:
    """File name of the page of a facet or of one of its values."""
    return page_name(FACET_PAGES.get(key, key), value)


def plain(fragment: str) -> str:
    """Text of an HTML fragment, without tags or entities."""
    return html.unescape(TAGS.sub("", fragment)).strip()


# UIkit classes of the small buttons (Listen, show or hide translations).
BUTTON = "uk-button uk-button-default uk-button-small"


# UIkit classes of the Play all button.
PLAY_BUTTON = "uk-button uk-button-primary uk-button-small"


def listen_button(text: str, labels: Mapping[str, str], me: bool = False) -> str:
    """The Listen and Slow buttons of a German text; me speaks it with voice_me."""
    say = html.escape(text, quote=True)
    mine = ' data-me="true"' if me else ""
    return (f'<button type="button" class="dk-listen {BUTTON}" data-say="{say}"{mine}>'
            f'{html.escape(labels["listen"])}</button> '
            f'<button type="button" class="dk-listen dk-slow {BUTTON}" data-say="{say}"{mine} data-rate="slow">'
            f'{html.escape(labels["slow"])}</button>')


def local_audio(src: str) -> str:
    """The path of a recording inside the site, or '' for a web address: pages load nothing from the internet."""
    src = src.strip()
    return "" if not src or src.lower().startswith(REMOTE) or not AUDIO_FILE.search(src) else src


def audio_html(src: str, labels: Mapping[str, str]) -> str:
    """A recording with its player and the real badge."""
    return (f'<audio class="dk-audio" controls preload="none" src="{html.escape(src, quote=True)}"></audio> '
            f'<span class="dk-badge dk-real">{html.escape(labels["real_audio"])}</span>')


def play_all_button(selector: str, labels: Mapping[str, str]) -> str:
    """A button that plays every element the selector finds, in page order."""
    return (f'<button type="button" class="dk-play-all {PLAY_BUTTON}" data-play="{html.escape(selector, quote=True)}">'
            f'{html.escape(labels["play_all"])}</button>')


def pairs_html(fragment: str, native: str, labels: Mapping[str, str]) -> str:
    """Turn 'German :: translation' items into spans and Listen buttons; 'wrong :: right' under Typical mistakes."""
    chunks = SECTION_START.split(fragment)
    return "".join(_mistakes_html(c, labels) if 'id="typical-mistakes"' in c
                   else _pairs_html(c, native, labels) for c in chunks)


def split_pair(content: str) -> tuple[str, str] | None:
    """Split 'left :: right' at the first '::' outside any element; None when there is none."""
    depth, pos = 0, 0
    for piece in re.split(r"(<[^>]+>)", content):
        if piece.startswith("<"):
            if piece.startswith("</"):
                depth = max(0, depth - 1)
            elif not piece.endswith("/>") and not re.match(r"<(br|img|hr|wbr)\b", piece):
                depth += 1
        elif depth == 0 and "::" in piece:
            at = pos + piece.index("::")
            return content[:at].strip(), content[at + 2:].strip()
        pos += len(piece)
    return None


def _list_items(fragment: str, render: Callable[[str, str], str]) -> str:
    """Apply render(left, right) to each simple list item 'left :: right', keeping a <p> wrapper."""

    def item(match: re.Match) -> str:
        inner = match.group(2)
        if re.search(r"<(ul|ol|li)\b", inner):
            return match.group(0)
        wrapped = PARAGRAPH.match(inner)
        content = wrapped.group(1) if wrapped else inner
        # The checkbox of a task list item stays in front of the pair.
        box = CHECKBOX.match(content) if match.group(1) else None
        pair = split_pair(content[box.end():] if box else content)
        if pair is None:
            return match.group(0)
        css, body = render(*pair)
        if box:
            css, body = f"{css} task-list-item", f"{box.group(1)} {body}"
        return f'<li class="{css}">{f"<p>{body}</p>" if wrapped else body}</li>'

    return LIST_ITEM.sub(item, fragment)


def _mistakes_html(fragment: str, labels: Mapping[str, str]) -> str:
    """List items 'wrong :: right': both German, only the right form gets a Listen button."""

    def render(wrong: str, right: str) -> tuple[str, str]:
        return "dk-mistake", (f'<span class="dk-wrong" lang="de">{wrong}</span> '
                              f'<span class="dk-right" lang="de">{right}</span> '
                              f'{listen_button(plain(right), labels)}')

    return _list_items(fragment, render)


def _pairs_html(fragment: str, native: str, labels: Mapping[str, str]) -> str:
    lang = html.escape(native, quote=True)

    def render(german: str, translation: str) -> tuple[str, str]:
        parts = [f'<span class="dk-de" lang="de">{german}</span>', listen_button(plain(german), labels)]
        if translation:
            parts.append(f'<span class="dk-tr dk-no-link" lang="{lang}">{translation}</span>')
        return "dk-pair", " ".join(parts)

    return _list_items(fragment, render)


def _top_elements(fragment: str, names: Sequence[str]) -> list[tuple[str, int, int, int, int]]:
    """(name, start, inner start, inner end, end) of the named elements that sit inside no other element.

    The section wrappers of KB4IT do not count as elements.
    """
    found = []
    stack: list[tuple[str, bool, int, int]] = []
    for match in TAG.finditer(fragment):
        piece = match.group()
        tag = TAG_NAME.match(piece)
        if not tag:
            continue
        closing, name = tag.group(1), tag.group(2).lower()
        if not closing:
            if name not in VOID_TAGS and not piece.rstrip().endswith("/>"):
                stack.append((name, bool(SECTION_WRAPPER.match(piece)), match.start(), match.end()))
            continue
        # A closing tag with no matching open tag is ignored.
        if not any(item[0] == name for item in stack):
            continue
        while True:
            open_name, wrapper, start, inner = stack.pop()
            if open_name == name:
                break
        if name in names and not wrapper and all(item[1] for item in stack):
            found.append((name, start, inner, match.start(), match.end()))
    return sorted(found, key=lambda element: element[1])


def _replace(fragment: str, changes: list[tuple[int, int, str]]) -> str:
    """Put each (start, end, text) change into the fragment."""
    for start, end, text in sorted(changes, reverse=True):
        fragment = fragment[:start] + text + fragment[end:]
    return fragment


def _item_parts(inner: str) -> tuple[str, str, str]:
    """(before, first line, after) of a list item: its first paragraph, or its text up to the first block."""
    lead = len(inner) - len(inner.lstrip())
    if inner.startswith("<p>", lead):
        end = inner.find("</p>", lead)
        if end >= 0:
            return inner[:lead + 3], inner[lead + 3:end], inner[end:]
    block = BLOCK.search(inner, lead)
    line = inner[lead:block.start() if block else len(inner)].rstrip()
    return inner[:lead], line, inner[lead + len(line):]


def _turn(line: str, me: str, native: str, labels: Mapping[str, str]) -> tuple[str, str, bool] | None:
    """(side class, HTML, has a translation) of a line '<strong>Speaker:</strong> German :: translation'."""
    match = TURN.match(line)
    if not match:
        return None
    speaker = match.group(2).strip()
    recordings = RENDERED_AUDIO.findall(match.group(3))
    content = RENDERED_AUDIO.sub("", match.group(3))
    german, translation = split_pair(content) or (content.strip(), "")
    mine = plain(speaker).lower() == me.strip().lower()
    recording = local_audio(html.unescape(recordings[-1])) if recordings else ""
    voice = audio_html(recording, labels) if recording else listen_button(plain(german), labels, mine)
    parts = [f'<span class="dk-speaker dk-no-link">{speaker}</span>',
             f'<span class="dk-de" lang="de">{german}</span>', voice]
    if translation:
        parts.append(f'<span class="dk-tr dk-no-link" lang="{html.escape(native, quote=True)}">{translation}</span>')
    side = "dk-me" if mine else "dk-other"
    return side, " ".join(parts), bool(translation)


def dialogue_html(fragment: str, me: str, native: str, labels: dict[str, str]) -> str:
    """Turn the first list before the sections into a dialogue, and number the items under Variations.

    Every item of that list is a turn and keeps its number, also when it is malformed.
    """
    chunks = SECTION_START.split(fragment)
    lists = _top_elements(chunks[0], ("ul",))
    if not lists:
        return fragment
    _, start, inner_start, inner_end, end = lists[0]
    inner = chunks[0][inner_start:inner_end]
    changes, translated, count = [], False, 0
    for count, (_, li_start, body_start, body_end, li_end) in enumerate(_top_elements(inner, ("li",)), start=1):
        before, line, after = _item_parts(inner[body_start:body_end])
        turn = _turn(line, me, native, labels)
        if turn is None:
            changes.append((li_start, body_start, f'<li id="t{count}" class="dk-turn dk-invalid">'))
            continue
        side, body, has_translation = turn
        translated = translated or has_translation
        changes.append((li_start, li_end, f'<li id="t{count}" class="dk-turn {side}">{before}{body}{after}</li>'))
    turns_html = _replace(inner, changes)

    for n, chunk in enumerate(chunks):
        if n == 0 or not VARIATIONS.search(chunk):
            continue
        changes, number = [], 0
        for _, _, list_start, list_end, _ in _top_elements(chunk, ("ul",)):
            for _, li_start, body_start, body_end, li_end in _top_elements(chunk[list_start:list_end], ("li",)):
                before, line, after = _item_parts(chunk[list_start + body_start:list_start + body_end])
                numbered = NUMBERED.match(line)
                turn = _turn(numbered.group(2), me, native, labels) if numbered else None
                if turn is None:
                    continue
                number += 1
                side, body, has_translation = turn
                translated = translated or has_translation
                target = int(numbered.group(1))
                replaces = (f'<a class="dk-replaces" href="#t{target}">{target}</a>' if 1 <= target <= count
                            else f'<span class="dk-replaces">{target}</span>')
                changes.append((list_start + li_start, list_start + li_end,
                                f'<li id="v{number}" class="dk-turn dk-variation {side}">{before}{replaces} {body}'
                                f'{after}</li>'))
        chunks[n] = _replace(chunk, changes)

    button = ""
    if translated:
        show, hide = (html.escape(labels[key], quote=True) for key in ("show_translations", "hide_translations"))
        button = (f'<button type="button" class="dk-toggle-tr {BUTTON}" hidden data-show="{show}" data-hide="{hide}">'
                  f'{hide}</button>')
    play = play_all_button(".dk-dialogue .dk-turn", labels)
    box = f'<div class="dk-dialogue-box">{play}{button}<ol class="dk-dialogue">{turns_html}</ol></div>'
    chunks[0] = chunks[0][:start] + box + chunks[0][end:]
    return "".join(chunks)


def _letters(text: str) -> str:
    return NOT_A_LETTER.sub("", text).lower()


def text_html(fragment: str, units: Sequence[Unit], native: str, labels: dict[str, str]) -> str:
    """Give each paragraph before the sections the anchor of its sentence unit, and fold its translation.

    A paragraph is matched to a unit by its text, so a paragraph the index left out gets no anchor.
    """
    chunks = SECTION_START.split(fragment)
    chunks[0] = _sentence_paragraphs(chunks[0], units, native, labels, play_all=True)
    return "".join(chunks)


def _sentence_paragraphs(head: str, units: Sequence[Unit], native: str, labels: Mapping[str, str],
                         play_all: bool = False) -> str:
    """Paragraphs of head that match a unit get its anchor and a Listen button; a following quote is folded.

    With play_all, a Play all button stands before the first of them."""
    keys = [_letters(unit.german) for unit in units]
    lang = html.escape(native, quote=True)
    changes, at, sentence_end = [], 0, -1
    for name, start, inner_start, inner_end, end in _top_elements(head, ("p", "blockquote")):
        after_sentence = sentence_end >= 0 and not head[sentence_end:start].strip()
        sentence_end = -1
        if name == "blockquote":
            if after_sentence:
                changes.append((start, end, f'<details class="dk-fold dk-tr-fold" lang="{lang}"><summary>'
                                            f'{html.escape(labels["translation"])}</summary>{head[start:end]}'
                                            f'</details>'))
            continue
        content = RENDERED_AUDIO.sub("", head[inner_start:inner_end])
        key = _letters(plain(content))
        if head[start:inner_start] != "<p>" or not key or key not in keys[at:]:
            continue
        at = keys.index(key, at) + 1
        unit = units[at - 1]
        first = play_all and not any('class="dk-sentence"' in change[2] for change in changes)
        bar = f'<p class="dk-play-bar">{play_all_button(".dk-sentence", labels)}</p>' if first else ""
        recording = local_audio(unit.audio)
        voice = audio_html(recording, labels) if recording else listen_button(unit.german, labels)
        changes.append((start, end, f'{bar}<p id="{unit.anchor}" class="dk-sentence"><span class="dk-de" lang="de">'
                                    f'{content.strip()}</span> {voice}</p>'))
        sentence_end = end
    return _replace(head, changes)


def photo_html(fragment: str, units: Sequence[Unit], native: str, labels: dict[str, str]) -> str:
    """Load images lazily and give the paragraphs of the Transcription section their sentence anchors."""
    chunks = SECTION_START.split(IMG_TAG.sub('<img loading="lazy"', fragment))
    for i, chunk in enumerate(chunks):
        if 'id="transcription"' in chunk:
            chunks[i] = _sentence_paragraphs(chunk, units, native, labels)
    return "".join(chunks)


def mistake_html(fragment: str) -> str:
    """Mark the Wrong and Right sections, so the wrong form is struck through and the right one stands out."""
    chunks = SECTION_START.split(fragment)
    for i, chunk in enumerate(chunks):
        for name in ("wrong", "right"):
            if re.search(rf'<h2\b[^>]*\bid="{name}"', chunk):
                chunks[i] = chunk.replace('<div class="kb-sect1">', f'<div class="kb-sect1 dk-mistake-{name}">', 1)
    return "".join(chunks)


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
    # Classes of single facts, by label: the plural in its colour.
    fact_css: dict[str, str] = {}
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
            fact("plural", plural if has_plural(plural) else labels["no_plural"])
            if has_plural(plural):
                fact_css[labels["plural"]] = cued("dk-pl")
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
    if entry.type == "Conversation":
        fact("date", plain_date(entry.value("Date")))
    if entry.type == "Text":
        fact("received", plain_date(entry.value("Received")))
        fact("deadline", plain_date(entry.value("Deadline")))
    if entry.type == "Photo" and entry.value("Place"):
        links.append((labels["place"], [(entry.value("Place"), facet_page("Place", entry.value("Place")))]))
    if entry.type in ("Mistake", "Gap"):
        fact("date", plain_date(entry.value("Date")))
    if entry.type == "Mistake" and entry.value("Pattern"):
        pattern = entry.value("Pattern")
        links.append((labels["pattern"], [(pattern, facet_page("Pattern", pattern))]))
        points = [g for g in course.by_type("Grammar") if pattern in g.values("Pattern")]
        if points:
            links.append((labels["grammar_point"], [(g.title, url(g.id)) for g in points]))
    if entry.type == "Gap":
        fact("gap_state", labels["to_process"] if entry.open_gap else labels["processed"])
    if entry.type == "Situation":
        ticked, total = entry.cando
        fact("i_can", f"{ticked} / {total}" if total else "")
        fact("next_time", plain_date(entry.value("NextTime")))
    fact("source", ", ".join(entry.values("Source")))
    if entry.values("Situation"):
        # A value that names no Situation page is shown without a link.
        links.append((labels["situation"], [(title, url(course.situations[title]) if title in course.situations
                                             else "") for title in entry.values("Situation")]))
    if entry.values("Topic"):
        links.append((labels["topic"], [(t, facet_page("Topic", t)) for t in entry.values("Topic")]))

    badges = []
    if entry.is_noun:
        said = "die" if entry.value("PluralOnly") == "yes" else entry.value("Article")
        if said in GENDER:
            css_article = "dk-pl" if entry.value("PluralOnly") == "yes" else GENDER[said]
            badges.append((f"dk-badge dk-article {cued(css_article)}", said, facet_page(ARTICLE_KEY, said)))
    kind, genre = entry.value("Kind"), entry.value("Genre")
    if entry.type == "Conversation" and kind:
        css_kind = f" dk-kind-{kind}" if kind in KINDS else ""
        badges.append((f"dk-badge dk-kind{css_kind}", kind, facet_page("Kind", kind)))
    if entry.type == "Text" and genre:
        badges.append(("dk-badge dk-genre", genre, facet_page("Genre", genre)))
    if entry.level:
        badges.append(("dk-badge dk-level", entry.level, facet_page("Level", entry.level)))
    if entry.value("Register"):
        badges.append(("dk-badge dk-register", entry.value("Register"), facet_page("Register", entry.value("Register"))))
    if entry.type == "Text" and entry.value("Reply") == "yes":
        badges.append(("dk-badge dk-reply", labels["reply"], ""))
    if entry.type not in ("Situation", "Inbox"):
        badges.append((f"dk-badge dk-checked dk-checked-{entry.checked}", entry.checked, ""))
    unverified = entry.type not in ("Situation", "Inbox") and entry.checked in UNVERIFIED
    hint = f' title="{html.escape(labels["unverified_hint"], quote=True)}"' if unverified else ""
    # Only a German word, verb or chunk is read aloud from the card.
    say = headline if entry.type in INDEXED or entry.type == "Grammar" else ""
    recording = local_audio(entry.value("Audio")) if entry.type in INDEXED else ""
    return {"kind": entry.type, "headline": headline, "headline_class": cued(css), "say": say, "audio": recording,
            "translation": entry.translation, "badges": badges, "facts": facts, "fact_css": fact_css, "links": links,
            "unverified": unverified, "hint_attr": hint}


def plain_date(value: str) -> str:
    """A date as written, without the midnight time KB4IT adds to a bare day."""
    return value.removesuffix(" 00:00:00")


def day(value: str) -> str:
    """The YYYY-MM-DD part of a real date, or ''."""
    return value[:10] if real_date(value) else ""


def extras(entry: Entry, course: Course, labels: dict[str, str], url: Callable[[str], str]) -> dict:
    """What an entry page shows around its body: dated banners, related entries, sentences and coverage."""

    def sentences(found: Sequence[Occurrence]) -> list[dict]:
        return [{"href": f"{url(o.doc)}#{o.anchor}", "title": o.title, "kind": o.kind, "german": o.german,
                 "translation": o.translation} for o in found[:MAX_SENTENCES]]

    related = []
    if entry.type == "Situation":
        inside = course.in_situation(entry.title)
        for label, kind in RELATED:
            items = [(e.title, url(e.id), e.value("Kind") if kind == "Conversation" else "")
                     for e in inside if e.type == kind]
            if items:
                related.append((labels[label], items))
    found = course.index.get(entry.id, []) if entry.type in INDEXED else []
    hits = marker_hits(entry.values("Marker"), course.entries.values()) if entry.type == "Grammar" else []
    return {
        "deadline": day(entry.value("Deadline")) if entry.type == "Text" else "",
        "next_time": day(entry.value("NextTime")) if entry.type == "Situation" else "",
        "prepare": f"practice.html#situation={quote(entry.title, safe='')}" if entry.type == "Situation" else "",
        "related": related,
        "occurrences": sentences(found),
        "more": max(0, len(found) - MAX_SENTENCES),
        "candidates": sentences(hits),
        "more_candidates": max(0, len(hits) - MAX_SENTENCES),
        "coverage": course.coverage.get(entry.id) if entry.type in ("Text", "Conversation") else None,
        "see_inbox": entry.type == "Inbox",
    }


def _find(course: Course, value: str) -> str:
    """Id of the Word, Verb or Chunk whose title matches a value such as 'der Terminkalender', or ''."""
    title = re.sub(r"^(der|die|das)\s+", "", value.strip())
    for entry in course.entries.values():
        if entry.type in INDEXED and entry.title == title:
            return entry.id
    return ""
