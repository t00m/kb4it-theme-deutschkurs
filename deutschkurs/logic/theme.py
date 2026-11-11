"""deutschkurs: a conversation-centric German course built from your own files."""

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path

from kb4it.core.checks import Problem
from kb4it.theme import BaseTheme, ThemeError

from .config import DeutschkursConfig, valid_color
from .data import build_data, too_large, write_data
from .course import Course, build_course
from .glossary import link_html
from .labels import labels
from .model import TYPES
from .pages import write_pages
from .privacy import has_gps, image_path, photo_files, scan
from .skill import PUBLISHED, publish, skill_html
from .render import (AUDIO_FILE, ARTICLE_KEY, FACET_KEYS, card, dialogue_html, extras, facet_page, fold_sections, grammar_order, mistake_html,
                     pairs_html, photo_html, text_html)

# File names of the facet pages, without their extension.
FACET_NAMES = tuple(facet_page(key)[:-len(".html")] for key in FACET_KEYS) + (ARTICLE_KEY,)
# Types whose sentences other pages show, so a change in their text relinks every page.
SENTENCE_TYPES = ("Text", "Conversation", "Photo")


def whole_days(value, default: int = 7) -> int:
    """A number of days from the settings, or the default when it is no whole number from 0 up."""
    return value if type(value) is int and value >= 0 else default


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
        """Settings with every invalid colour and slow_rate replaced by its default, each one logged."""
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
        rate = self.config.slow_rate
        if type(rate) not in (int, float) or not 0 < rate <= 2:
            self.log.warning("[DEUTSCHKURS] SETTING_INVALID key=slow_rate")
            rate = defaults.slow_rate
        return replace(self.config, accent=accent, gender_colors=colors, slow_rate=rate)

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
        hits = self._privacy(site)
        if self.config.strict and (self.course.problems or hits):
            raise ThemeError(f"{len(self.course.problems)} metadata problems, {hits} privacy hits and strict is on")

    def _privacy(self, site) -> int:
        """Log suspected personal data in the sources and GPS data in photos; return the number of hits."""
        allow = [str(a) for a in (self.config.privacy_allow or [])]
        count = 0
        for doc in site.documents:
            for hit in scan(doc.source(), allow):
                count += 1
                self.log.warning(f"[DEUTSCHKURS] PRIVACY_SUSPECT doc={doc.id} reason={hit.reason} line={hit.line}")
        source = Path(site.paths.source)
        for path in photo_files(source):
            try:
                gps = has_gps(path)
            except OSError:
                self.log.warning(f"[DEUTSCHKURS] PHOTO_UNREADABLE doc={path.relative_to(source).as_posix()}")
                continue
            if gps is None:
                self.log.info("[DEUTSCHKURS] Pillow is not installed: photos are not checked for GPS data")
                break
            if gps:
                count += 1
                self.log.warning(f"[DEUTSCHKURS] PHOTO_GPS doc={path.relative_to(source).as_posix()}")
        return count

    def checks(self, site):
        problems = list(super().checks(site))
        source = Path(site.paths.source)
        for entry in self.course.by_type("Photo"):
            if not entry.image:
                reason = "none"
            else:
                path = image_path(source, entry.image)
                reason = "remote" if path is None else "" if path.is_file() else "missing"
            if reason:
                problems.append(Problem("PHOTO_MISSING", entry.id, f"reason={reason}", label="doc"))
        for entry in self.course.entries.values():
            # A recording that is missing or on the web plays nothing (spec 8); one problem per reason.
            recordings = [entry.value("Audio")] if entry.type in ("Word", "Verb", "Chunk") else []
            recordings += [u.audio for u in (*entry.units, *entry.variations)]
            reasons = []
            for src in filter(None, recordings):
                path = image_path(source, src)
                reason = ("remote" if path is None else "type" if not AUDIO_FILE.search(src.strip())
                          else "" if path.is_file() else "missing")
                if reason and reason not in reasons:
                    reasons.append(reason)
            for reason in reasons:
                problems.append(Problem("AUDIO_MISSING", entry.id, f"reason={reason}", label="doc"))
        for entry in self.course.by_type("Inbox"):
            if any(image_path(source, c.image) is None for c in entry.inbox if c.image):
                problems.append(Problem("PHOTO_MISSING", entry.id, "reason=remote", label="doc"))
        return problems

    def dk_var(self, entry=None):
        """The var['dk'] of every page the theme renders."""
        data = {"labels": self.labels, "settings": self.config, "native": self.config.native, "entry": entry,
                "card": None, "extras": None, "prepare_days": whole_days(self.config.prepare_days)}
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
        target = Path(site.paths.target)
        publish(target, self.course)
        payload = build_data(self.course, self.config, site.repo.get("title", ""), site.theme.get("version", ""))
        size = write_data(target, payload)
        if too_large(size):
            self.log.warning(f"[DEUTSCHKURS] DATA_LARGE size={size}")

    def search_record(self, doc):
        entry = self.course.entries.get(doc.id)
        # Inbox documents are raw captures: the Inbox page lists them, search does not.
        if entry is not None and entry.type == "Inbox":
            return None
        record = self.site.features.search.search_record(doc)
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
        if entry is not None and entry.type == "Photo":
            transforms.append(lambda html: photo_html(html, entry.units, config.native, labels_))
        if entry is not None and entry.type == "Mistake":
            transforms.append(mistake_html)
        transforms.append(lambda html: pairs_html(html, config.native, labels_))
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
