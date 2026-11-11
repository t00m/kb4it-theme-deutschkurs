"""The theme's own pages: home, lists by type and facet pages."""

from .checks import real_date
from .course import Course
from .german import sort_key
from .glossary import find_spans
from .model import AREAS, GENRES
from .render import FACET_KEYS, GENDER, UNVERIFIED, day, facet_page, perfekt, plain_date

LISTS = (("situations", "Situation"), ("conversations", "Conversation"), ("texts", "Text"), ("vocabulary", "Word"),
         ("verbs", "Verb"), ("chunks", "Chunk"), ("grammar", "Grammar"), ("photos", "Photo"), ("mistakes", "Mistake"))
INBOX = "inbox"
# Lists of a situation card: label and type.
IN_SITUATION = (("conversations", "Conversation"), ("texts", "Text"), ("chunks", "Chunk"), ("vocabulary", "Word"))


def cell(text="", href="", css=""):
    return {"text": text, "href": href, "css": css}


def translation(entry):
    """The translation cell; dotted when nobody has checked the entry yet."""
    return cell(entry.translation, css="dk-unverified" if entry.checked in UNVERIFIED else "")


def word_row(entry, url):
    plural_only = entry.value("PluralOnly") == "yes"
    article = "die" if plural_only else entry.value("Article")
    css = "dk-pl" if plural_only else GENDER.get(article, "")
    plural = entry.value("Plural")
    return [cell(article, css=css), cell(entry.title, url(entry.id), css),
            cell("" if plural in ("none", "-") else plural), translation(entry), cell(entry.level),
            cell(entry.value("PartOfSpeech"))]


def verb_row(entry, url):
    separable = f"{entry.value('Prefix')}-" if entry.value("Separable") == "yes" else ""
    return [cell(entry.title, url(entry.id)), cell(perfekt(entry)), cell(separable), translation(entry),
            cell(entry.level)]


def chunk_row(entry, url):
    return [cell(entry.title, url(entry.id)), cell(entry.value("Register")), translation(entry),
            cell(entry.level)]


def any_row(entry, url):
    return [cell(entry.title, url(entry.id)), cell(entry.type), translation(entry), cell(entry.level)]


def item(entry, course: Course, url) -> dict:
    """One line of a grouped list."""
    found = course.coverage.get(entry.id)
    return {"title": entry.title, "href": url(entry.id), "level": entry.level, "kind": entry.value("Kind"),
            "coverage": f"{found.percent} %" if found is not None and found.total else "",
            "deadline": day(entry.value("Deadline")) if entry.type == "Text" else ""}


def situation_card(entry, course: Course, labels, url) -> dict:
    ticked, total = entry.cando
    inside = course.in_situation(entry.title)
    facts = []
    if total:
        facts.append((labels["i_can"], f"{ticked} / {total}"))
    if entry.value("NextTime"):
        facts.append((labels["next_time"], plain_date(entry.value("NextTime"))))
    facts += [(labels[label], sum(1 for e in inside if e.type == kind)) for label, kind in IN_SITUATION]
    return {"title": entry.title, "href": url(entry.id), "facts": facts}


def by_situation(course: Course, labels, url) -> list[tuple]:
    """Conversations under each of their situations; the ones without a situation come last."""
    groups, loose = {}, []
    for entry in course.by_type("Conversation"):
        for name in entry.values("Situation"):
            groups.setdefault(name, []).append(entry)
        if not entry.values("Situation"):
            loose.append(entry)
    ordered = [(name, url(course.situations[name]) if name in course.situations else "",
                [item(e, course, url) for e in groups[name]]) for name in sorted(groups, key=sort_key)]
    if loose:
        ordered.append((labels["no_situation"], "", [item(e, course, url) for e in loose]))
    return ordered


def by_genre(course: Course, url) -> list[tuple]:
    """Texts under their genre, in the order of the model; a text without a genre goes to Other."""
    groups = {}
    for entry in course.by_type("Text"):
        groups.setdefault(entry.value("Genre") or "Other", []).append(entry)
    names = [g for g in GENRES if g in groups] + sorted((g for g in groups if g not in GENRES), key=sort_key)
    return [(name, "", [item(e, course, url) for e in groups[name]]) for name in names]


def dated(entries, key, url) -> list[tuple]:
    """(title, url, day) of the entries with a real date in a property, soonest first."""
    found = [(day(e.value(key)), e) for e in entries]
    return [(e.title, url(e.id), when) for when, e in sorted(found, key=lambda pair: pair[0]) if when]


def gallery(course: Course) -> list[dict]:
    """Photos that have a local image, by title."""
    photos = [e for e in course.by_type("Photo") if e.image and not e.image.startswith(("http://", "https://", "//"))]
    return [{"title": e.title, "href": course.url(e.id), "src": e.image, "place": e.value("Place"),
             "situations": "|".join(e.values("Situation"))} for e in sorted(photos, key=lambda e: sort_key(e.title))]


def by_pattern(course: Course, labels) -> list[tuple]:
    """Mistakes under their pattern, newest first, with the grammar points of that pattern; no pattern last."""
    groups: dict[str, list] = {}
    for entry in course.by_type("Mistake"):
        groups.setdefault(entry.value("Pattern"), []).append(entry)
    names = sorted((g for g in groups if g), key=sort_key) + ([""] if "" in groups else [])
    found = []
    for name in names:
        entries = sorted(groups[name], key=lambda e: day(e.value("Date")), reverse=True)
        points = [(g.title, course.url(g.id)) for g in course.by_type("Grammar") if name and name in g.values("Pattern")]
        found.append((name or labels["no_pattern"], facet_page("Pattern", name) if name else "",
                      [{"title": e.title, "href": course.url(e.id), "level": e.level, "kind": "", "coverage": "",
                        "deadline": "", "date": plain_date(e.value("Date"))} for e in entries], points))
    return found


def _known(text: str, course: Course) -> str:
    """Id of the entry whose form is the first word of a capture, or ''."""
    words = text.split()
    if not words:
        return ""
    first = words[0].strip(".,;:!?|\"'()")
    spans = find_spans(first, course.glossary)
    return spans[0][2] if spans and spans[0][0] == 0 and spans[0][1] == len(first) else ""


def inbox_items(course: Course) -> list[dict]:
    """Captures of every Inbox document and the Gaps without German, newest first, undated last."""
    found = []
    for entry in course.by_type("Inbox"):
        for capture in entry.inbox:
            known = _known(capture.text, course)
            found.append({"date": capture.date if real_date(capture.date) else "", "text": capture.text,
                          "image": capture.image, "href": "", "known": course.url(known) if known else "",
                          "known_title": course.entries[known].title if known else ""})
    for entry in course.by_type("Gap"):
        if entry.open_gap:
            found.append({"date": day(entry.value("Date")), "text": entry.title, "image": "",
                          "href": course.url(entry.id), "known": "", "known_title": ""})
    dated = sorted((i for i in found if i["date"]), key=lambda i: i["date"], reverse=True)
    return dated + [i for i in found if not i["date"]]


def inbox_count(course: Course) -> int:
    """Captures plus Gaps that wait to be processed."""
    return sum(len(e.inbox) for e in course.by_type("Inbox")) + sum(1 for e in course.by_type("Gap") if e.open_gap)


def write_pages(theme, site, course: Course) -> None:
    """Write every list, facet and home page."""
    L, url, dk = theme.labels, course.url, theme.dk_var()

    def table(name, title, columns, rows, filters=()):
        html = theme.render("DK_TABLE", dk=dk, heading=title, columns=columns, rows=rows, filters=filters)
        site.page(name, title, html, listing=True)

    words = course.by_type("Word")
    table("vocabulary", L["vocabulary"],
          [L["article"], L["word"], L["plural"], L["translation"], L["level"], L["part_of_speech"]],
          [word_row(e, url) for e in words], filters=(4, 5))
    table("verbs", L["verbs"], [L["verb"], L["perfekt"], L["separable"], L["translation"], L["level"]],
          [verb_row(e, url) for e in course.by_type("Verb")], filters=(4,))
    table("chunks", L["chunks"], [L["chunk"], L["register"], L["translation"], L["level"]],
          [chunk_row(e, url) for e in course.by_type("Chunk")], filters=(1, 3))

    groups = {}
    for entry in course.by_type("Grammar"):
        groups.setdefault(entry.value("Area") or "Other", []).append(entry)
    ordered = [(area, "", [item(e, course, url) for e in groups[area]]) for area in AREAS if area in groups]

    def grouped(name, found):
        site.page(name, L[name], theme.render("DK_GROUPS", dk=dk, heading=L[name], groups=found), listing=True)

    grouped("grammar", ordered)
    grouped("conversations", by_situation(course, L, url))
    grouped("texts", by_genre(course, url))
    grouped("mistakes", by_pattern(course, L))
    photos = gallery(course)
    places = sorted({p["place"] for p in photos if p["place"]}, key=sort_key)
    names = sorted({n for p in photos for n in p["situations"].split("|") if n}, key=sort_key)
    site.page("photos", L["photos"], theme.render("DK_GALLERY", dk=dk, heading=L["photos"], photos=photos,
                                                    places=places, situations=names), listing=True)
    site.page(INBOX, L["inbox"], theme.render("DK_INBOX", dk=dk, heading=L["inbox"], items=inbox_items(course)),
              listing=True)
    situations = [situation_card(e, course, L, url) for e in course.by_type("Situation")]
    site.page("situations", L["situations"],
              theme.render("DK_SITUATIONS", dk=dk, heading=L["situations"], situations=situations), listing=True)

    columns = [L["word"], L["type"], L["translation"], L["level"]]
    for key in FACET_KEYS:
        facet = course.facet(key)
        values = [(value, facet_page(key, value), len(entries)) for value, entries in facet.items()]
        heading = L[key.lower()]
        site.page(facet_page(key), heading, theme.render("DK_FACET", dk=dk, heading=heading, values=values),
                  listing=True)
        for value, entries in facet.items():
            title = f"{heading}: {value}"
            table(facet_page(key, value), title, columns, [any_row(e, url) for e in entries])

    if "index.md" in course.entries:
        return  # the learner's own index.md is the home page
    counts = [(L[name], f"{name}.html", len(course.by_type(kind))) for name, kind in LISTS]
    latest = [e for e in (course.entries.get(doc.id) for doc in site.documents.latest(20)) if e and e.type and e.type != "Inbox"][:5]
    others = [e for e in course.entries.values() if not e.type]
    home = theme.render("PAGE_INDEX", dk=dk, counts=counts,
                        coming=dated(course.by_type("Situation"), "NextTime", url),
                        deadlines=dated(course.by_type("Text"), "Deadline", url),
                        latest=[(e.title, url(e.id), e.type) for e in latest],
                        others=[(e.title, url(e.id)) for e in others],
                        inbox=L["inbox_count"].replace("{n}", str(inbox_count(course))) if inbox_count(course) else "")
    site.page("index", L["home"], home)
