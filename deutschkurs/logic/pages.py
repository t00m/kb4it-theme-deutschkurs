"""The theme's own pages: home, lists by type and facet pages."""

from kb4it.theme import page_name

from .course import Course
from .model import AREAS
from .render import GENDER, perfekt

FACET_KEYS = ("Level", "Topic", "Register")
LISTS = (("vocabulary", "Word"), ("verbs", "Verb"), ("chunks", "Chunk"), ("grammar", "Grammar"))


def cell(text="", href="", css=""):
    return {"text": text, "href": href, "css": css}


def word_row(entry, url):
    plural_only = entry.value("PluralOnly") == "yes"
    article = "die" if plural_only else entry.value("Article")
    css = "dk-pl" if plural_only else GENDER.get(article, "")
    plural = entry.value("Plural")
    return [cell(article, css=css), cell(entry.title, url(entry.id), css),
            cell("" if plural in ("none", "-") else plural), cell(entry.translation), cell(entry.level),
            cell(entry.value("PartOfSpeech"))]


def verb_row(entry, url):
    separable = f"{entry.value('Prefix')}-" if entry.value("Separable") == "yes" else ""
    return [cell(entry.title, url(entry.id)), cell(perfekt(entry)), cell(separable), cell(entry.translation),
            cell(entry.level)]


def chunk_row(entry, url):
    return [cell(entry.title, url(entry.id)), cell(entry.value("Register")), cell(entry.translation),
            cell(entry.level)]


def any_row(entry, url):
    return [cell(entry.title, url(entry.id)), cell(entry.type), cell(entry.translation), cell(entry.level)]


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
    ordered = [(area, [(e.title, url(e.id), e.level) for e in groups[area]]) for area in AREAS if area in groups]
    site.page("grammar", L["grammar"], theme.render("DK_GROUPS", dk=dk, heading=L["grammar"], groups=ordered),
              listing=True)

    columns = [L["word"], L["type"], L["translation"], L["level"]]
    for key in FACET_KEYS:
        facet = course.facet(key)
        values = [(value, page_name(key, value), len(entries)) for value, entries in facet.items()]
        heading = L[key.lower()]
        site.page(page_name(key), heading, theme.render("DK_FACET", dk=dk, heading=heading, values=values),
                  listing=True)
        for value, entries in facet.items():
            title = f"{heading}: {value}"
            table(page_name(key, value), title, columns, [any_row(e, url) for e in entries])

    if "index.md" in course.entries:
        return  # the learner's own index.md is the home page
    counts = [(L[name], f"{name}.html", len(course.by_type(kind))) for name, kind in LISTS]
    latest = [e for e in (course.entries.get(doc.id) for doc in site.documents.latest(20)) if e and e.type][:5]
    others = [e for e in course.entries.values() if not e.type]
    home = theme.render("PAGE_INDEX", dk=dk, counts=counts,
                        latest=[(e.title, url(e.id), e.type) for e in latest],
                        others=[(e.title, url(e.id)) for e in others])
    site.page("index", L["home"], home)
