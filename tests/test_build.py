import re

import subprocess

from conftest import KB4IT, build_site, prepare_site, warnings

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


KRANK = """---
Level: A1
PartOfSpeech: adjective
Translation: enfermo
Type: Word
---

# krank

## Examples

- Ich bin krank und habe einen Termin beim Arzt. :: Estoy enfermo y tengo cita con el médico.
"""


def test_word_linked_in_other_page(tmp_path):
    site = build_site(tmp_path, {"krank-test.md": KRANK})
    assert 'href="termin.html"' in site.page("krank-test.html")


def test_untyped_document_builds(tmp_path):
    site = build_site(tmp_path, {"notiz.md": "---\nTopic: Schule\n---\n\n# Notiz\n\nText.\n"})
    assert (site.target / "notiz.html").is_file()
    problems = [line for line in warnings(site.log) if "META_INVALID" in line]
    assert len(problems) == 1
    assert problems[0].endswith("META_INVALID doc=notiz.md key=Type reason=type_missing")


def test_new_word_relinks_unchanged_pages(tmp_path):
    config = prepare_site(tmp_path, {"krank-test.md": KRANK.replace("einen Termin beim Arzt", "Fieber")})
    subprocess.run([KB4IT, "build", str(config)], check=True, capture_output=True)
    source = config.parent.parent / "source"
    (source / "fieber.md").write_text(
        "---\nArticle: das\nLevel: A2\nPartOfSpeech: noun\nTranslation: fiebre\nType: Word\n---\n\n# Fieber\n",
        encoding="utf-8")
    subprocess.run([KB4IT, "build", str(config)], check=True, capture_output=True)
    page = (config.parent.parent / "target" / "krank-test.html").read_text(encoding="utf-8")
    assert 'href="fieber.html"' in page


TALK = """---
Kind: model
Level: A1
Type: Conversation
---

# Testgespräch

- **Mutter:** {line}
"""


def rebuild(tmp_path, name, first, second, extra={}):
    """Build, replace one source file and build again; return the target folder."""
    config = prepare_site(tmp_path, {name: first, **extra})
    subprocess.run([KB4IT, "build", str(config)], check=True, capture_output=True)
    (config.parent.parent / "source" / name).write_text(second, encoding="utf-8")
    subprocess.run([KB4IT, "build", str(config)], check=True, capture_output=True)
    return config.parent.parent / "target"


def test_conversation_edit_rebuilds_the_word_page(tmp_path):
    target = rebuild(tmp_path, "gespraech-test.md", TALK.format(line="Hallo!"),
                     TALK.format(line="Hast du einen Termin?"))
    assert 'href="gespraech-test.html#t1"' in (target / "termin.html").read_text(encoding="utf-8")


def test_renamed_word_relinks_unchanged_pages(tmp_path):
    word = "---\nArticle: das\nLevel: A2\nPartOfSpeech: noun\nTranslation: fever\nType: Word\n---\n\n# {title}\n"
    target = rebuild(tmp_path, "fieber.md", word.format(title="Hitze"), word.format(title="Fieber"),
                     {"krank-test.md": KRANK.replace("einen Termin beim Arzt", "Fieber")})
    assert 'href="fieber.html"' in (target / "krank-test.html").read_text(encoding="utf-8")
