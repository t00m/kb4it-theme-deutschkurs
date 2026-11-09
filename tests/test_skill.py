import json
import re
from pathlib import Path

import pytest
import yaml

from deutschkurs.logic import model
from deutschkurs.logic.checks import REASONS, check_body, check_properties
from deutschkurs.logic.model import entry_from

THEME = Path(__file__).resolve().parent.parent / "deutschkurs"
SKILL = THEME / "skill" / "deutschkurs"
REFERENCE = SKILL / "reference"
SKELETONS = THEME / "templates" / "skeletons"
FENCED = re.compile(r"```markdown\n(.*?)```", re.S)


def props_of(markdown):
    """Frontmatter as KB4IT reads it: values split on commas."""
    front = yaml.load(markdown.split("---")[1], Loader=yaml.BaseLoader)
    return {k: tuple(v.strip() for v in str(val).split(",")) for k, val in front.items() if val is not None}


def entry_types():
    return (REFERENCE / "entry-types.md").read_text(encoding="utf-8")


def test_frontmatter():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    front = yaml.safe_load(text.split("---")[1])
    assert front["name"] == "deutschkurs"
    assert front["description"].strip()
    assert len(text.splitlines()) < 300


def test_reference_files_exist():
    for name in ("entry-types.md", "conventions.md", "privacy.md", "checks.md", "lingua.md"):
        assert (REFERENCE / name).is_file(), name


def test_skill_names_its_reference_files():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    for name in ("entry-types.md", "conventions.md", "privacy.md", "checks.md", "lingua.md", "site.md"):
        assert f"reference/{name}" in text, name


def test_types_documented():
    for kind in model.TYPES:
        assert re.search(rf"^## {kind}$", entry_types(), re.M), kind


def test_properties_documented():
    text = entry_types()
    for kind, props in model.PROPERTIES.items():
        for prop in props:
            assert f"`{prop}`" in text, (kind, prop)


@pytest.mark.parametrize("name", ["LEVELS", "CHECKED", "REGISTERS", "PARTS_OF_SPEECH", "AREAS", "GOVERNMENTS",
                                  "AUXILIARIES", "ARTICLES"])
def test_values_documented(name):
    text = entry_types()
    for value in getattr(model, name):
        assert f"`{value}`" in text, (name, value)


def test_sections_documented():
    text = entry_types()
    for kind, sections in model.SECTIONS.items():
        for section in sections:
            assert f"## {section}" in text, (kind, section)


def test_reasons_documented():
    text = (REFERENCE / "checks.md").read_text(encoding="utf-8")
    for reason in REASONS:
        assert f"`{reason}`" in text, reason


def test_examples_are_valid():
    examples = FENCED.findall(entry_types())
    kinds = set()
    for example in examples:
        props = props_of(example)
        entry = entry_from("example.md", props, example)
        assert check_properties("example.md", props, None) == [], example[:80]
        assert check_body(entry) == [], example[:80]
        kinds.add(entry.type)
    assert kinds == set(model.TYPES)


def test_skeletons_valid():
    listing = json.loads((SKELETONS / "skeletons.json").read_text(encoding="utf-8"))
    assert [e["id"] for e in listing] == ["word", "verb", "chunk", "grammar"]
    for item in listing:
        text = (SKELETONS / f"{item['id'].upper()}-SKELETON.md").read_text(encoding="utf-8")
        props = props_of(text)
        assert check_properties("x.md", props, None) == [], item["id"]
        assert check_body(entry_from("x.md", props, text)) == [], item["id"]


def test_no_em_dash():
    for path in [*SKILL.rglob("*.md"), *SKELETONS.glob("*")]:
        assert "\u2014" not in path.read_text(encoding="utf-8"), path.name


def test_published(built_site):
    page = built_site.page("skill.html")
    assert 'href="skills/deutschkurs/SKILL.md"' in page
    assert "~/.claude/skills/deutschkurs/" in page
    assert (built_site.target / "skills" / "deutschkurs" / "SKILL.md").is_file()
    assert (built_site.target / "skills" / "deutschkurs" / "reference" / "entry-types.md").is_file()
    site_md = (built_site.target / "skills" / "deutschkurs" / "reference" / "site.md").read_text(encoding="utf-8")
    assert "`termin.md`" in site_md


def test_site_appendix_has_no_body_text(tmp_path):
    from conftest import build_site
    from test_pages import TERMIN
    site = build_site(tmp_path, {"termin.md": TERMIN}, starter=False)
    site_md = (site.target / "skills" / "deutschkurs" / "reference" / "site.md").read_text(encoding="utf-8")
    assert "Termin" in site_md
    assert "morgen" not in site_md and "cita" not in site_md


def test_nav_links_skill(built_site):
    assert 'href="skill.html"' in built_site.page("index.html")


def test_add_page_skeletons(built_site):
    page = built_site.page("add.html")
    for name in ("Word", "Verb", "Chunk", "Grammar"):
        assert f'"name": "{name}"' in page, name
    assert '"person"' not in page.lower()


def test_word_skeleton_is_correct_german():
    text = (SKELETONS / "WORD-SKELETON.md").read_text(encoding="utf-8")
    props = props_of(text)
    assert props["Article"] == ("das",) and props["Plural"] == ("die Wörter",)


def test_examples_do_not_name_unconsulted_sources():
    assert "Source: Duden" not in entry_types()


def test_reference_examples_are_english():
    for example in FENCED.findall(entry_types()):
        assert not set("¿¡ñáíóú") & set(example), example[:60]
