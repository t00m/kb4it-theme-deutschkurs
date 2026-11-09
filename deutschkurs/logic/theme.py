"""deutschkurs: a conversation-centric German course built from your own files."""

import hashlib
import json
from dataclasses import asdict

from kb4it.theme import BaseTheme, ThemeError

from .config import DeutschkursConfig
from .course import Course, build_course
from .glossary import link_html
from .labels import labels
from .render import card, fold_sections, grammar_order, pairs_html

ENTRY_TYPES = ("Word", "Verb", "Chunk", "Grammar")


class Theme(BaseTheme):
    features = ("search", "not_found", "editor")
    config_class = DeutschkursConfig
    log_area = "DEUTSCHKURS"
    person_pages = False
    profile_skeleton = False
    untitled_label = "Untitled"

    def setup(self):
        # KB4IT sets self.config after setup(), so settings are read in prepare().
        self.course = Course()
        self.labels, _ = labels({})

    def prepare(self, site):
        self.labels, unknown = labels(self.config.labels)
        for key in unknown:
            self.log.warning(f"[DEUTSCHKURS] LABEL_UNKNOWN key={key}")
        docs = [(doc.id, doc.properties, doc.source()) for doc in site.documents]
        self.course = build_course(docs, self.config, url=lambda doc_id: site.doc(doc_id).url)
        for problem in self.course.problems:
            self.log.warning(f"[DEUTSCHKURS] {problem}")
        if self.config.strict and self.course.problems:
            raise ThemeError(f"{len(self.course.problems)} metadata problems and strict is on")

    def dk_var(self, entry=None):
        """The var['dk'] of every page the theme renders."""
        data = {"labels": self.labels, "settings": self.config, "native": self.config.native, "entry": entry,
                "card": None}
        if entry is not None and entry.type in ENTRY_TYPES:
            data["card"] = card(entry, self.course, self.labels, self.course.url)
        return data

    def build(self, site):
        documents = [{"title": doc.title or self.untitled_label, "url": doc.url} for doc in site.documents]
        documents.sort(key=lambda item: item["title"].lower())
        site.page("index", self.labels["home"], self.render("PAGE_INDEX", documents=documents, dk=self.dk_var()))

    def page_context(self, doc, var):
        var["dk"] = self.dk_var(self.course.entries.get(doc.id))
        return var

    def page_template(self, doc, var):
        entry = self.course.entries.get(doc.id)
        return "DK_ENTRY" if entry is not None and entry.type in ENTRY_TYPES else "HTML_BODY"

    def body_transforms(self, doc, var):
        course, labels_, config = self.course, self.labels, self.config
        entry = course.entries.get(doc.id)
        transforms = [*super().body_transforms(doc, var)]
        transforms.append(lambda html: pairs_html(html, config.native, labels_["listen"]))
        if entry is not None and entry.type == "Grammar":
            shown, folded = grammar_order(entry, config)
            summary = labels_["simple_german"] if folded == "simple-german" else labels_["explanation"]
            transforms.append(lambda html: fold_sections(html, shown, folded, summary))
        transforms.append(lambda html: link_html(html, course.glossary, doc.id, course.url))
        return transforms

    def site_signature(self):
        # Called before prepare(), so it reads the documents itself; any property change relinks every page.
        props = [[doc.id, {k: list(v) for k, v in sorted(doc.properties.items())}] for doc in self.site.documents]
        settings = asdict(self.config)
        version = self.site.theme.get("version", "")
        data = json.dumps([sorted(props), settings, version], sort_keys=True, ensure_ascii=False, default=str)
        return hashlib.sha256(data.encode()).hexdigest()[:16]
