import re

from conftest import warnings

EXTERNAL = re.compile(r"<(?:script|link|img)\b[^>]*\b(?:src|href)=\"https?://", re.I)


def test_no_warnings(built_site):
    assert warnings(built_site.log) == []


def test_pages_exist(built_site):
    for name in ("index.html", "termin.html", "search.html", "404.html", "add.html"):
        assert (built_site.target / name).is_file(), name


def test_no_external_resources(built_site):
    for page in built_site.target.glob("*.html"):
        assert not EXTERNAL.search(page.read_text(encoding="utf-8")), page.name


def test_warnings_helper_matches_log_format():
    log = ("2026-11-09 19:08:19 |       INFO | MainThread | X | a:1 | ok\n"
           "2026-11-09 19:08:19 |    WARNING | MainThread | X | a:1 | bad")
    assert warnings(log) == [log.splitlines()[1]]
