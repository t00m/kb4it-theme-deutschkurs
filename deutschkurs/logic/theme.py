"""deutschkurs: a conversation-centric German course built from your own files."""

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path

from kb4it.theme import BaseTheme, ThemeError

from .config import DeutschkursConfig, valid_color
from .course import Course, build_course
from .glossary import link_html
from .labels import labels
from .model import TYPES
from .pages import write_pages
from .skill import PUBLISHED, publish, skill_html
from .render import (FACET_KEYS, card, dialogue_html, extras, facet_page, fold_sections, grammar_order, pairs_html,
                     text_html)

# File names of the facet pages, without their extension.
FACET_NAMES = tuple(facet_page(key)[:-len(".html")] for key in FACET_KEYS)
# Types whose sentences other pages show, so a change in their text relinks every page.
SENTENCE_TYPES = ("Text", "Conversation")


class Theme(BaseTheme):
    features = ("search", "not_found", "editor")
    config_class = DeutschkursConfig
    log_area = "DEUTSCHKURS"
    person_pages = False
    profile_skeleton = False
    untitled_label = "Untitled"
    reserved_pages = tuple(f"{name}.md" for name in (
        "vocabulary", "verbs", "chunks", "grammar", "texts", "conversations", "situations", "photos", "mistakes",
        "inbox", "practice", "progress", "skill", "search", "404", *FACET_NAMES))

    def setup(self):
        # KB4IT sets self.config after setup(), so settings are read in prepare().
        self.course = Course()
        self.labels, _ = labels({})

    def _checked_colors(self):
        """Settings with every invalid colour replaced by its default, each one logged."""
        defaults = DeutschkursConfig()
        accent = self.config.accent
        if not valid_color(accent):
            self.log.warning("[DEUTSCHKURS] COLOR_INVALID key=accent")
            accent = defaults.accent
        colors = dict(defaults.gender_colors)
        for key, value in (self.config.gender_colors or {}).items():
            if key in colors and valid_color(value):
                colors[key] = value
            else:
                self.log.warning(f"[DEUTSCHKURS] COLOR_INVALID key=gender_colors.{key}")
        return replace(self.config, accent=accent, gender_colors=colors)

    def prepare(self, site):
        self.config = self._checked_colors()
        self.labels, unknown = labels(self.config.labels)
        for key in unknown:
            self.log.warning(f"[DEUTSCHKURS] LABEL_UNKNOWN key={key}")
        docs = [(doc.id, doc.properties, doc.source()) for doc in site.documents]
        self.course = build_course(docs, self.config, url=lambda doc_id: site.doc(doc_id).url)
        for problem in self.course.problems:
            self.log.warning(f"[DEUTSCHKURS] {problem}")
        # Facet pages are Name.html and Name_Value.html; a file system may ignore the case of file names.
        taken = tuple(name.lower() for name in FACET_NAMES)
        for doc_id in self.course.entries:
            name = doc_id.lower()
            if name.startswith(tuple(f"{t}_" for t in taken)) or name.rsplit(".", 1)[0] in taken:
                self.log.warning(f"[DEUTSCHKURS] PAGE_NAME_TAKEN doc={doc_id} reason=facet_page_name")
        if self.config.strict and self.course.problems:
            raise ThemeError(f"{len(self.course.problems)} metadata problems and strict is on")

    def dk_var(self, entry=None):
        """The var['dk'] of every page the theme renders."""
        data = {"labels": self.labels, "settings": self.config, "native": self.config.native, "entry": entry,
                "card": None, "extras": None}
        if entry is not None and entry.type in TYPES:
            data["card"] = card(entry, self.course, self.labels, self.course.url)
            data["extras"] = extras(entry, self.course, self.labels, self.course.url)
        return data

    def base_var(self):
        var = super().base_var()
        var.setdefault("dk", self.dk_var())
        return var

    def build(self, site):
        write_pages(self, site, self.course)
        html = self.render("DK_SKILL", dk=self.dk_var(), skill_html=skill_html(),
                           skill_url=f"{PUBLISHED}/SKILL.md", site_url=f"{PUBLISHED}/reference/site.md")
        site.page("skill", self.labels["skill"], html)

    def after_deploy(self, site):
        publish(Path(site.paths.target), self.course)

    def search_record(self, doc):
        record = self.site.features.search.search_record(doc)
        entry = self.course.entries.get(doc.id)
        if record is not None and entry is not None and entry.type:
            facets = {"Type": [entry.type]}
            if entry.level:
                facets["Level"] = [entry.level]
            if entry.value("Article"):
                facets["Article"] = [entry.value("Article")]
            record["f"] = facets
            record["s"] = entry.translation
        return record

    def page_context(self, doc, var):
        var["dk"] = self.dk_var(self.course.entries.get(doc.id))
        return var

    def page_template(self, doc, var):
        entry = self.course.entries.get(doc.id)
        return "DK_ENTRY" if entry is not None and entry.type in TYPES else "HTML_BODY"

    def body_transforms(self, doc, var):
        course, labels_, config = self.course, self.labels, self.config
        entry = course.entries.get(doc.id)
        transforms = [*super().body_transforms(doc, var)]
        # Turns and sentences first: they are list items and paragraphs the next steps must not touch.
        if entry is not None and entry.type == "Conversation":
            me = entry.value("Me") or "ich"
            transforms.append(lambda html: dialogue_html(html, me, config.native, labels_))
        if entry is not None and entry.type == "Text":
            transforms.append(lambda html: text_html(html, entry.units, config.native, labels_))
        transforms.append(lambda html: pairs_html(html, config.native, labels_["listen"]))
        if entry is not None and entry.type == "Grammar":
            shown, folded = grammar_order(entry, config)
            summary = labels_["simple_german"] if folded == "simple-german" else labels_["explanation"]
            transforms.append(lambda html: fold_sections(html, shown, folded, summary))
        transforms.append(lambda html: link_html(html, course.glossary, doc.id, course.url))
        return transforms

    def site_signature(self):
        # Called before prepare(), so it reads the documents itself. Every page is relinked when a property
        # changes (the title is one), or the text of a document whose sentences other pages show.
        props = []
        for doc in self.site.documents:
            shown = doc.source() if set(doc.properties.get("Type", ())) & set(SENTENCE_TYPES) else ""
            props.append([doc.id, {k: list(v) for k, v in sorted(doc.properties.items())}, shown])
        settings = asdict(self.config)
        version = self.site.theme.get("version", "")
        data = json.dumps([sorted(props), settings, version], sort_keys=True, ensure_ascii=False, default=str)
        return hashlib.sha256(data.encode()).hexdigest()[:16]
