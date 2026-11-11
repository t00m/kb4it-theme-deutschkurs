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
                                  "AUXILIARIES", "ARTICLES", "KINDS", "GENRES", "PLACES"])
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
    assert [e["id"] for e in listing] == ["situation", "conversation", "text", "word", "verb", "chunk", "grammar",
                                            "photo", "mistake", "gap", "inbox"]
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
    for name in ("Situation", "Conversation", "Text", "Word", "Verb", "Chunk", "Grammar"):
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


def test_conversation_skeleton_names_roles_and_asks_for_its_kind():
    text = (SKELETONS / "CONVERSATION-SKELETON.md").read_text(encoding="utf-8")
    entry = entry_from("x.md", props_of(text), text)
    assert entry.value("Kind") == "reconstructed"
    assert [u.speaker for u in entry.units] == ["Lehrerin", "ich"]


def test_situation_skeleton_starts_with_open_tasks():
    text = (SKELETONS / "SITUATION-SKELETON.md").read_text(encoding="utf-8")
    assert entry_from("x.md", props_of(text), text).cando == (0, 2)


def skill_text():
    return (SKILL / "SKILL.md").read_text(encoding="utf-8")


def workflow(name):
    """Text of one workflow of SKILL.md."""
    return re.search(rf"^### {name}\n(.*?)(?=^##)", skill_text(), re.S | re.M).group(1)


def test_skill_names_every_type_it_may_write():
    intro = skill_text().split("## Before you start")[0]
    for kind in model.TYPES:
        assert kind in intro, kind
    assert "four entry types" not in intro


def test_skill_has_the_rule_honest_conversations():
    rule = re.search(r"\*\*Honest conversations\.\*\*(.*)", skill_text()).group(1)
    for kind in model.KINDS:
        assert f"`{kind}`" in rule, kind


@pytest.mark.parametrize("name", ["Capture", "Prepare a situation", "Debrief", "Correct my German", "Fix problems",
                                  "Convert lingua files"])
def test_skill_workflows(name):
    assert workflow(name).strip()


def test_capture_stores_the_material_as_a_text():
    text = workflow("Capture")
    assert "`Type: Text`" in text
    assert "not stored" not in text


def test_prepare_writes_a_model_and_never_ticks():
    text = workflow("Prepare a situation")
    assert "`Kind: model`" in text and "## I can" in text
    assert "tick" in text


def test_debrief_writes_a_reconstructed_conversation_and_a_log_line():
    text = workflow("Debrief")
    assert "`Kind: reconstructed`" in text and "## Log" in text
    assert "`real`" in text


def test_conventions_list_reserved_names_and_flags():
    from deutschkurs.logic.checks import FLAGS
    from deutschkurs.logic.theme import Theme
    text = (REFERENCE / "conventions.md").read_text(encoding="utf-8")
    for page in Theme.reserved_pages:
        assert f"`{page[:-3]}`" in text, page
    for flag in FLAGS:
        assert f"`{flag}`" in text, flag


def test_conventions_explain_sentence_units():
    text = (REFERENCE / "conventions.md").read_text(encoding="utf-8")
    assert "## Sentence units" in text
    for mark in ("`#t1`", "`#s1`", "`#v1`"):
        assert mark in text, mark


def test_lingua_texts_convert():
    text = (REFERENCE / "lingua.md").read_text(encoding="utf-8")
    assert "Not supported yet" not in text
    kinds = set()
    for example in FENCED.findall(text):
        props = props_of(example)
        entry = entry_from("example.md", props, example)
        assert check_properties("example.md", props, None) == [], example[:80]
        assert check_body(entry) == [], example[:80]
        kinds.add(entry.type)
    assert kinds == {"Word", "Text"}


def test_site_appendix_lists_situations_conversations_and_texts(built_site):
    site_md = (built_site.target / "skills" / "deutschkurs" / "reference" / "site.md").read_text(encoding="utf-8")
    for heading in ("## Situation", "## Conversation", "## Text"):
        assert heading in site_md, heading
    assert "- `situation-elternabend.md`: Elternabend\n" in site_md
    assert "- `gruss-am-schultor.md`: Gruß am Schultor (A1, model)" in site_md
    assert "- `elternbrief-ausflug.md`: Elternbrief zum Ausflug (A2, School letter)" in site_md


def test_site_appendix_has_no_sentence_of_a_conversation_or_a_text(built_site):
    site_md = (built_site.target / "skills" / "deutschkurs" / "reference" / "site.md").read_text(encoding="utf-8")
    assert "Liebe Eltern" not in site_md and "wie geht" not in site_md
    assert "Ich kann" not in site_md


def test_skill_no_longer_defers_real_life_types():
    text = skill_text()
    assert "Do not create files of those types yet" not in text
    assert "A Mistake entry type comes in a later version" not in text


def test_skill_has_inbox_and_letter_workflows():
    text = skill_text()
    assert "### Process the inbox" in text and "### Answer a letter" in text
    letter = text.split("### Answer a letter")[1].split("### ")[0]
    assert "`Reply: yes`" in letter and "never send" in letter.lower()
    inbox = text.split("### Process the inbox")[1].split("### ")[0]
    assert "## In German" in inbox


def test_debrief_and_correct_write_gaps_and_mistakes():
    text = skill_text()
    debrief = text.split("### Debrief")[1].split("### ")[0]
    assert "`Type: Gap`" in debrief and "`Type: Mistake`" in debrief
    correct = text.split("### Correct my German")[1].split("### ")[0]
    assert "`Type: Mistake`" in correct


def test_capture_writes_a_photo_without_location_data():
    capture = skill_text().split("### Capture")[1].split("### ")[0]
    assert "`Type: Photo`" in capture and "location" in capture


def test_privacy_reference_names_every_reason():
    text = (REFERENCE / "privacy.md").read_text(encoding="utf-8")
    for word in ("`iban`", "`email`", "`phone`", "`address`", "`PRIVACY_SUSPECT", "`PHOTO_GPS", "`privacy_allow`"):
        assert word in text, word


def test_checks_reference_names_build_codes():
    text = (REFERENCE / "checks.md").read_text(encoding="utf-8")
    for code in ("`PRIVACY_SUSPECT", "`PHOTO_GPS", "`PHOTO_MISSING"):
        assert code in text, code


def test_skill_stays_short():
    assert len(skill_text().splitlines()) < 300


def test_site_appendix_lists_photos_mistakes_and_gaps(built_site):
    site_md = (built_site.target / "skills" / "deutschkurs" / "reference" / "site.md").read_text(encoding="utf-8")
    assert "- `photo-baustelle.md`: Baustelle betreten verboten (Street)" in site_md
    assert "- `mistake-ich-habe-40-jahre.md`: Ich habe 40 Jahre (A1, es-tener-haben)" in site_md
    assert "- `gap-krankmeldung.md`: Mein Kind ist krank (to process)" in site_md
    assert "## Pattern values in use" in site_md and "- es-tener-haben" in site_md
    assert "Pfand" not in site_md


def test_skill_explains_what_makes_an_entry_ready_to_practise():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    rule = text.split("**Ready to practise.**", 1)[1].split("\n", 1)[0]
    assert "`Checked: unchecked`" in rule and "## Examples" in rule and "## In German" in rule
