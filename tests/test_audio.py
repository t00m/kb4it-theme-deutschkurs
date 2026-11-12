"""Real recordings: the Audio property and [audio](...) at the end of a turn (spec 8)."""

import json
import re
import subprocess

import pytest

from conftest import KB4IT, BuiltSite, prepare_site, warnings
from deutschkurs.logic.parse import turns

WORD = """---
Article: der
Audio: resources/audio/termin.m4a
Checked: native
Level: A1
PartOfSpeech: noun
Plural: die Termine
Translation: appointment
Type: Word
---

# Termin

## Examples

- Ich habe einen Termin. :: I have an appointment.
"""

CALL = """---
Checked: native
Kind: real
Level: A1
Type: Conversation
---

# Am Telefon

- **Ärztin:** Praxis Weber, guten Tag. [audio](resources/audio/praxis.m4a) :: Doctor's office, hello.
- **ich:** Guten Tag, ich brauche einen Termin.
- **Ärztin:** Geht es morgen? :: Is tomorrow fine? [audio](resources/audio/morgen.mp3)
- **ich:** Ja, gerne. [audio](https://example.org/ja.m4a)
"""


LETTER = """---
Checked: native
Genre: Letter
Level: A1
Type: Text
---

# Brief

Liebe Eltern, [audio](resources/audio/praxis.m4a)

> Dear parents,

Bitte kommen Sie morgen.
"""

LOUD = """---
Checked: native
Kind: real
Level: A1
Type: Conversation
---

# Laut

- **Anna:** Hallo! [audio](HTTPS://example.org/hallo.m4a)
"""

NOTE = WORD.replace("Audio: resources/audio/termin.m4a", "Audio: resources/audio/notiz.txt").replace("# Termin", "# Notiz")


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    config = prepare_site(tmp_path_factory.mktemp("audio"), {"termin.md": WORD, "am-telefon.md": CALL, "brief.md": LETTER,
                                                           "laut.md": LOUD, "notiz.md": NOTE}, starter=False)
    root = config.parent.parent
    audio = root / "source" / "resources" / "audio"
    audio.mkdir(parents=True)
    for name in ("termin.m4a", "praxis.m4a"):
        (audio / name).write_bytes(b"\x00\x00\x00\x18ftypM4A ")
    run = subprocess.run([KB4IT, "build", str(config)], capture_output=True, text=True)
    assert run.returncode == 0, run.stdout[-3000:]
    return BuiltSite(root, root / "target", (root / "var" / "log" / "kb4it.log").read_text(encoding="utf-8"))


def main(page):
    return page.split("<main", 1)[1].split("</main>", 1)[0]


def payload(site):
    text = (site.target / "deutschkurs-data.js").read_text(encoding="utf-8")
    return json.loads(text[len("window.DEUTSCHKURS_DATA = "):].rstrip().rstrip(";"))


def test_turn_audio_link_is_not_part_of_the_text():
    found, _, bad = turns(CALL.split("---", 2)[2])
    assert not bad
    assert [u.german for u in found] == ["Praxis Weber, guten Tag.", "Guten Tag, ich brauche einen Termin.",
                                        "Geht es morgen?", "Ja, gerne."]
    assert [u.translation for u in found] == ["Doctor's office, hello.", "", "Is tomorrow fine?", ""]
    assert [u.audio for u in found] == ["resources/audio/praxis.m4a", "", "resources/audio/morgen.mp3",
                                       "https://example.org/ja.m4a"]


def test_word_card_plays_the_recording(site):
    head = main(site.page("termin.html")).split('<div class="dk-body', 1)[0]
    assert '<audio class="dk-audio" controls preload="none" src="resources/audio/termin.m4a"></audio>' in head
    assert '<span class="dk-badge dk-real">real</span>' in head
    assert "data-say" not in head
    assert (site.target / "resources" / "audio" / "termin.m4a").is_file()


def test_examples_keep_the_voice(site):
    assert 'data-say="Ich habe einen Termin."' in site.page("termin.html")


def test_recorded_turns_play_the_recording(site):
    page = main(site.page("am-telefon.html"))
    first = page.split('<li id="t1"', 1)[1].split("</li>", 1)[0]
    assert '<audio class="dk-audio" controls preload="none" src="resources/audio/praxis.m4a"></audio>' in first
    assert '<span class="dk-badge dk-real">real</span>' in first
    assert "data-say" not in first
    assert "Doctor&#x27;s office, hello." in first or "Doctor's office, hello." in first
    third = page.split('<li id="t3"', 1)[1].split("</li>", 1)[0]
    assert 'src="resources/audio/morgen.mp3"' in third
    assert re.search(r'lang="en">Is tomorrow fine\?\s*</span>', third)
    assert ">audio</a>" not in page


def test_remote_recording_is_not_loaded(site):
    page = site.page("am-telefon.html")
    # The source dialog shows the Markdown as text; no element loads or links the address.
    assert not re.search(r'(src|href)="[^"]*example\.org', page)
    fourth = main(page).split('<li id="t4"', 1)[1].split("</li>", 1)[0]
    assert 'data-say="Ja, gerne."' in fourth


def test_missing_and_remote_recordings_are_reported(site):
    log = "\n".join(warnings(site.log))
    assert "AUDIO_MISSING doc=am-telefon.md reason=missing" in log
    assert "AUDIO_MISSING doc=am-telefon.md reason=remote" in log
    assert "AUDIO_MISSING doc=termin.md" not in log


def test_data_carries_recordings(site):
    entries = {e["id"]: e for e in payload(site)["entries"]}
    assert entries["termin.md"]["audio"] == "resources/audio/termin.m4a"
    assert [t["audio"] for t in entries["am-telefon.md"]["turns"]] == [
        "resources/audio/praxis.m4a", "", "resources/audio/morgen.mp3", ""]
    assert entries["am-telefon.md"]["turns"][2]["translation"] == "Is tomorrow fine?"


def test_turn_audio_link_with_angle_brackets_or_title():
    text = ("# T\n\n- **Anna:** Ja [audio](resources/audio/a.m4a \"Titel\") :: Yes\n"
            "- **ich:** Wie? :: How? [audio](<resources/audio/c d.m4a>)\n")
    found, _, _ = turns(text)
    assert [(u.german, u.translation, u.audio) for u in found] == [
        ("Ja", "Yes", "resources/audio/a.m4a"), ("Wie?", "How?", "resources/audio/c d.m4a")]


def test_text_paragraph_with_a_recording():
    from deutschkurs.logic.parse import paragraphs
    units = paragraphs("# Brief\n\nLiebe Eltern, [audio](resources/audio/brief.m4a)\n\n> Dear parents,\n")
    assert [(u.german, u.translation, u.audio) for u in units] == [
        ("Liebe Eltern,", "Dear parents,", "resources/audio/brief.m4a")]


def test_text_page_plays_the_recording_of_a_paragraph(site):
    page = main(site.page("brief.html"))
    first = re.search(r'<p id="s1" class="dk-sentence">.*?</p>', page, re.S).group()
    assert 'src="resources/audio/praxis.m4a"' in first and "data-say" not in first and ">audio</a>" not in first
    assert 'data-say="Bitte kommen Sie morgen."' in page


def test_upper_case_web_address_is_remote(site):
    log = "\n".join(warnings(site.log))
    assert "AUDIO_MISSING doc=laut.md reason=remote" in log


def test_audio_property_must_be_a_sound_file(site):
    log = "\n".join(warnings(site.log))
    assert "AUDIO_MISSING doc=notiz.md reason=type" in log
    assert "<audio" not in main(site.page("notiz.html"))
