import subprocess
from pathlib import Path

from conftest import KB4IT, prepare_site
from deutschkurs.logic.config import DeutschkursConfig
from deutschkurs.logic.course import build_course

import yaml

SOURCE = Path(__file__).resolve().parent.parent / "deutschkurs" / "apps" / "default" / "source"


def course():
    docs = []
    for path in sorted(SOURCE.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        front = yaml.load(text.split("---")[1], Loader=yaml.BaseLoader)
        props = {k: tuple(v.strip() for v in str(val).split(",")) for k, val in front.items()}
        docs.append((path.name, props, text))
    return build_course(docs, DeutschkursConfig())


def test_counts():
    c = course()
    assert {kind: len(c.by_type(kind)) for kind in ("Word", "Verb", "Chunk", "Grammar")} == \
        {"Word": 10, "Verb": 5, "Chunk": 4, "Grammar": 2}
    assert c.problems == []


def test_every_word_and_verb_has_two_examples():
    c = course()
    for entry in c.by_type("Word") + c.by_type("Verb"):
        assert len(entry.examples) >= 2, entry.id
        assert all(p.translation for p in entry.examples), entry.id


def test_checked_by_assistant():
    assert {e.checked for e in course().typed()} == {"assistant"}


def test_verify_clean(tmp_path):
    config = prepare_site(tmp_path)
    run = subprocess.run([KB4IT, "verify", str(config)], capture_output=True, text=True)
    assert run.returncode == 0, run.stdout
    assert "META_INVALID" not in run.stdout


def test_examples_link_to_other_entries(built_site):
    page = built_site.page("elternabend.html")
    body = page.split('<div class="dk-body">', 1)[1]
    assert 'class="dk-link' in body
