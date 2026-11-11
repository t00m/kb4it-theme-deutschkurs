import subprocess
from pathlib import Path

from conftest import KB4IT, prepare_site
from deutschkurs.logic.config import DeutschkursConfig
from deutschkurs.logic.course import build_course, default_url
from deutschkurs.logic.model import TYPES

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
    assert {kind: len(c.by_type(kind)) for kind in TYPES} == \
        {"Word": 10, "Verb": 5, "Chunk": 4, "Grammar": 2, "Text": 1, "Conversation": 1, "Situation": 3,
         "Photo": 1, "Mistake": 1, "Gap": 1, "Inbox": 1}
    assert c.problems == []


def test_every_word_and_verb_has_two_examples():
    c = course()
    for entry in c.by_type("Word") + c.by_type("Verb"):
        assert len(entry.examples) >= 2, entry.id
        assert all(p.translation for p in entry.examples), entry.id


def test_checked_by_assistant():
    # Inbox captures are raw notes of the learner: nobody checks them.
    assert {e.checked for e in course().typed() if e.type != "Inbox"} == {"assistant"}


def test_verify_clean(tmp_path):
    config = prepare_site(tmp_path)
    run = subprocess.run([KB4IT, "verify", str(config)], capture_output=True, text=True)
    assert run.returncode == 0, run.stdout
    assert "META_INVALID" not in run.stdout


def test_examples_link_to_other_entries(built_site):
    page = built_site.page("elternabend.html")
    body = page.split('<div class="dk-body ', 1)[1]
    assert 'class="dk-link' in body


SPANISH = set("¿¡ñáíóú")


def test_starter_translations_are_english():
    for entry in course().typed():
        texts = [entry.translation, *(p.translation for p in entry.examples), *entry.sections.values(),
                 *(u.translation for u in (*entry.units, *entry.variations))]
        for text in texts:
            assert not SPANISH & set(text), (entry.id, text)


def test_starter_uses_the_default_language():
    import json
    repo = json.loads((SOURCE.parent / "config" / "repo.json").read_text(encoding="utf-8"))
    assert "native" not in repo.get("deutschkurs", {})


def test_starter_conversation_is_a_model():
    gruss = course().entries["gruss-am-schultor.md"]
    assert gruss.value("Kind") == "model"
    assert gruss.bad_lines == ()
    assert len(gruss.units) >= 4 and gruss.variations
    assert all(u.translation for u in (*gruss.units, *gruss.variations))


def test_starter_text_has_a_translation_for_every_paragraph():
    brief = course().entries["elternbrief-ausflug.md"]
    assert len(brief.units) >= 5
    assert all(u.translation for u in brief.units)


def test_every_situation_has_entries_and_open_tasks():
    c = course()
    for situation in c.by_type("Situation"):
        ticked, total = situation.cando
        assert total >= 2 and ticked == 0, situation.id
        kinds = {e.type for e in c.in_situation(situation.title)}
        assert kinds & {"Word", "Chunk"}, situation.id
    assert {e.type for e in c.in_situation("Am Schultor")} >= {"Conversation", "Chunk"}
    assert "Text" in {e.type for e in c.in_situation("Elternbrief")}


def test_starter_has_no_dated_blocks_that_grow_old():
    for entry in course().typed():
        assert not entry.value("Deadline") and not entry.value("NextTime"), entry.id


def test_every_indexed_sentence_has_its_anchor_in_the_page(built_site):
    c = course()
    found = [o for occurrences in c.index.values() for o in occurrences]
    assert found
    for o in found:
        assert f'id="{o.anchor}"' in built_site.page(default_url(o.doc)), (o.doc, o.anchor)
    for entry in c.typed():
        for unit in (*entry.units, *entry.variations):
            assert f'id="{unit.anchor}"' in built_site.page(default_url(entry.id)), (entry.id, unit.anchor)


def test_starter_sentences_show_on_word_pages(built_site):
    page = built_site.page("elternabend.html")
    assert 'href="gruss-am-schultor.html#t3"' in page
    assert 'href="elternbrief-ausflug.html#' in built_site.page("brotdose.html")


PHOTO = SOURCE / "resources" / "photos" / "2026-11-09-baustelle.webp"


def test_starter_photo_is_self_made_without_gps(tmp_path):
    from deutschkurs.logic.privacy import has_gps
    from PIL import Image
    assert PHOTO.is_file() and has_gps(PHOTO) is False
    script = Path(__file__).resolve().parent.parent / "scripts" / "make_starter_photo.py"
    out = tmp_path / "made.webp"
    run = subprocess.run(["python3", str(script), str(out)], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    with Image.open(out) as made, Image.open(PHOTO) as shipped:
        assert made.size == shipped.size


def test_starter_photo_points_to_its_image():
    photo = course().entries["photo-baustelle.md"]
    assert photo.image == "resources/photos/2026-11-09-baustelle.webp"
    assert len(photo.units) >= 1


def test_starter_mistake_and_gap():
    c = course()
    mistake = c.entries["mistake-ich-habe-40-jahre.md"]
    assert mistake.value("Pattern") == "es-tener-haben" and mistake.values("Situation") == ("Am Schultor",)
    assert c.entries["gap-krankmeldung.md"].open_gap


def test_starter_inbox_has_three_captures():
    inbox = course().entries["inbox-2026-11.md"]
    assert len(inbox.inbox) == 3
    assert sum(1 for item in inbox.inbox if item.image) == 1


def test_starter_gallery_image_resolves(built_site):
    import re
    html = built_site.page("photos.html")
    srcs = re.findall(r'<img loading="lazy" src="([^"]+)"', html)
    assert srcs == ["resources/photos/2026-11-09-baustelle.webp"]
    assert (built_site.target / srcs[0]).is_file()


def test_starter_inbox_marks_a_known_word(built_site):
    assert "already in the course" in built_site.page("inbox.html")


def test_starter_has_no_privacy_or_photo_warning(built_site):
    for code in ("PRIVACY_SUSPECT", "PHOTO_GPS", "PHOTO_MISSING"):
        assert code not in built_site.log
