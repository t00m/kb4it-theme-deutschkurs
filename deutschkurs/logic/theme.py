"""deutschkurs: a conversation-centric German course built from your own files."""

from kb4it.theme import BaseTheme

from .config import DeutschkursConfig


class Theme(BaseTheme):
    features = ("search", "not_found", "editor")
    config_class = DeutschkursConfig
    log_area = "DEUTSCHKURS"
    person_pages = False
    profile_skeleton = False
    untitled_label = "Untitled"

    def build(self, site):
        documents = [{"title": doc.title or self.untitled_label, "url": doc.url} for doc in site.documents]
        documents.sort(key=lambda item: item["title"].lower())
        site.page("index", "Home", self.render("PAGE_INDEX", documents=documents))
