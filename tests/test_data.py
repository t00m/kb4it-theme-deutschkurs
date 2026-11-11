"""The practice data file: one record per practisable entry, the sentences and the situations."""

import json

from deutschkurs.logic.config import DeutschkursConfig
from deutschkurs.logic.course import build_course
from deutschkurs.logic.data import LIMIT, build_data, site_id, too_large

TERMIN = ("termin.md", {"Type": ("Word",), "Level": ("A1",), "PartOfSpeech": ("noun",), "Article": ("der",),
                        "Plural": ("die Termine",), "Forms": ("Termins",), "Translation": ("appointment",),
                        "Checked": ("assistant",), "Situation": ("Am Schultor",), "Topic": ("Schule",),
                        "Regional": ("Verabredung",)},
          "# Termin\n\n## Examples\n\n- Ich habe einen Termin. :: I have an appointment.\n")
ELTERN = ("eltern.md", {"Type": ("Word",), "Level": ("A1",), "PartOfSpeech": ("noun",), "PluralOnly": ("yes",),
                        "Translation": ("parents",), "Checked": ("assistant",)},
          "# Eltern\n\n## Examples\n\n- Die Eltern kommen. :: The parents come.\n")
KRANK = ("krank.md", {"Type": ("Word",), "Level": ("A1",), "PartOfSpeech": ("adjective",), "Translation": ("ill",),
                      "Checked": ("assistant",)}, "# krank\n")
NEU = ("neu.md", {"Type": ("Word",), "Level": ("A1",), "PartOfSpeech": ("adjective",), "Translation": ("new",)},
       "# neu\n\n## Examples\n\n- Das ist neu. :: That is new.\n")
ANRUFEN = ("anrufen.md", {"Type": ("Verb",), "Level": ("A1",), "Translation": ("to call",), "Separable": ("yes",),
                          "Prefix": ("an",), "Participle": ("angerufen",), "Auxiliary": ("haben",),
                          "Present": ("ich rufe an", "du rufst an", "er ruft an"), "Checked": ("assistant",)},
           "# anrufen\n\n## Examples\n\n- Ich rufe dich morgen an. :: I will call you tomorrow.\n"
           "- Ich will dich anrufen. :: I want to call you.\n")
TALK = ("talk.md", {"Type": ("Conversation",), "Level": ("A1",), "Kind": ("model",), "Checked": ("assistant",),
                    "Me": ("Mutter",)},
        "# Gespräch\n\n- **Lehrerin:** Haben Sie einen Termin? :: Do you have an appointment?\n"
        "- **Mutter:** Ja, morgen. :: Yes, tomorrow.\n")
MISTAKE = ("mistake.md", {"Type": ("Mistake",), "Level": ("A1",), "Pattern": ("es-tener-haben",),
                          "Checked": ("assistant",)},
           "# Ich habe 40 Jahre\n\n## Wrong\n\nIch habe 40 Jahre.\n\n## Right\n\nIch bin 40 Jahre alt.\n")
GAP = ("gap.md", {"Type": ("Gap",), "Checked": ("assistant",)},
       "# Krank\n\n## I wanted to say\n\nMy daughter is sick.\n\n## In German\n\nMeine Tochter ist krank.\n")
PHOTO = ("photo.md", {"Type": ("Photo",)}, "# Schild\n\n![x](resources/photos/a.webp)\n\n## Transcription\n\nBaustelle\n")
INBOX = ("inbox-2026-11.md", {"Type": ("Inbox",)}, "# Inbox\n\n- 2026-11-09 Pfand\n")
SITUATION = ("schultor.md", {"Type": ("Situation",), "NextTime": ("2026-11-20",)},
             "# Am Schultor\n\n## I can\n\n- [x] grüßen\n- [ ] fragen\n")
DOCS = [TERMIN, ELTERN, KRANK, NEU, ANRUFEN, TALK, MISTAKE, GAP, PHOTO, INBOX, SITUATION]


def data(docs=DOCS):
    course = build_course(docs, DeutschkursConfig())
    return build_data(course, DeutschkursConfig(), "Mein Deutschkurs", "0.4.0")


def record(payload, doc_id):
    return next(e for e in payload["entries"] if e["id"] == doc_id)


def test_site_id_stable_and_short():
    assert site_id("Mein Deutschkurs") == site_id("Mein Deutschkurs")
    assert site_id("Mein Deutschkurs") != site_id("Other")
    assert len(site_id("x")) == 12 and all(c in "0123456789abcdef" for c in site_id("x"))


def test_payload_head():
    payload = data()
    assert payload["version"] == "0.4.0" and payload["site"] == site_id("Mein Deutschkurs")
    assert payload["settings"] == {"learner_level": "A2", "daily_reviews": 40, "daily_new": 5, "weekly_new": 10,
                                   "prepare_days": 7, "native": "en"}


def test_word_record_has_article_plural_forms():
    termin = record(data(), "termin.md")
    assert termin["type"] == "Word" and termin["article"] == "der" and termin["plural"] == "die Termine"
    assert termin["plural_only"] is False and "Termins" in termin["forms"] and "Termine" in termin["forms"]
    assert termin["regional"] == ["Verabredung"] and termin["situations"] == ["Am Schultor"]
    assert termin["topics"] == ["Schule"] and termin["url"] == "termin.html"
    assert termin["examples"] == [{"german": "Ich habe einen Termin.", "translation": "I have an appointment."}]


def test_plural_only_word_has_no_article():
    eltern = record(data(), "eltern.md")
    assert eltern["article"] == "" and eltern["plural_only"] is True


def test_unchecked_entry_not_ready():
    assert record(data(), "neu.md")["ready"] is False
    assert record(data(), "termin.md")["ready"] is True


def test_word_without_sentence_not_ready():
    assert record(data(), "krank.md")["ready"] is False


def test_sentence_rows_point_at_the_span():
    rows = [r for r in data()["sentences"] if r["entry"] == "termin.md"]
    assert {r["doc"] for r in rows} == {"talk.md", "termin.md"}
    for row in rows:
        assert row["german"][row["start"]:row["end"]] == "Termin"
    talk = next(r for r in rows if r["doc"] == "talk.md")
    assert talk["anchor"] == "t1" and talk["translation"] == "Do you have an appointment?"


def test_separable_rows_only_for_split_sentences():
    anrufen = record(data(), "anrufen.md")
    assert len(anrufen["separable"]) == 1
    row = anrufen["separable"][0]
    assert [row["german"][s:e] for s, e in row["parts"]] == ["rufe", "an"]
    assert anrufen["participle"] == "angerufen" and anrufen["auxiliary"] == ["haben"]


def test_conversation_turns_mark_me():
    talk = record(data(), "talk.md")
    assert talk["turns"] == [
        {"speaker": "Lehrerin", "german": "Haben Sie einen Termin?", "translation": "Do you have an appointment?",
         "me": False, "audio": ""},
        {"speaker": "Mutter", "german": "Ja, morgen.", "translation": "Yes, tomorrow.", "me": True, "audio": ""}]


def test_mistake_and_gap_records():
    payload = data()
    mistake = record(payload, "mistake.md")
    assert mistake["wrong"] == "Ich habe 40 Jahre." and mistake["right"] == "Ich bin 40 Jahre alt."
    assert mistake["pattern"] == "es-tener-haben"
    gap = record(payload, "gap.md")
    assert gap["wanted"] == "My daughter is sick." and gap["german"] == "Meine Tochter ist krank."


def test_inbox_and_photo_not_in_entries():
    ids = {e["id"] for e in data()["entries"]}
    assert "photo.md" not in ids and "inbox-2026-11.md" not in ids and "schultor.md" not in ids


def test_situations():
    assert data()["situations"] == [{"title": "Am Schultor", "url": "schultor.html", "next_time": "2026-11-20",
                                     "cando": [1, 2]}]


def test_data_large_limit():
    assert LIMIT == 2 * 1024 * 1024
    assert too_large(LIMIT + 1) and not too_large(LIMIT)


def test_data_file_written_and_parsable(built_site):
    text = (built_site.target / "deutschkurs-data.js").read_text(encoding="utf-8")
    assert text.startswith("window.DEUTSCHKURS_DATA = ") and text.rstrip().endswith(";")
    payload = json.loads(text[len("window.DEUTSCHKURS_DATA = "):].rstrip().rstrip(";"))
    assert {"version", "site", "settings", "entries", "sentences", "situations"} <= payload.keys()
    assert any(e["id"] == "termin.md" for e in payload["entries"])


def utf16(text, start, end):
    """The text between two UTF-16 offsets, as JavaScript's slice reads it."""
    raw = text.encode("utf-16-le")
    return raw[start * 2:end * 2].decode("utf-16-le")


def test_offsets_are_utf16_after_an_emoji():
    talk = ("talk.md", {"Type": ("Conversation",), "Level": ("A1",), "Kind": ("real",), "Checked": ("assistant",)},
            "# Chat\n\n- **A:** 😊 Der Termin ist morgen. :: The appointment is tomorrow.\n"
            "- **B:** 😊 Ich rufe dich an. :: I call you.\n")
    payload = data([TERMIN, ANRUFEN, talk])
    row = next(r for r in payload["sentences"] if r["doc"] == "talk.md" and r["entry"] == "termin.md")
    assert utf16(row["german"], row["start"], row["end"]) == "Termin"
    split = next(s for s in record(payload, "anrufen.md")["separable"] if "😊" in s["german"])
    assert [utf16(split["german"], s, e) for s, e in split["parts"]] == ["rufe", "an"]


def test_perfekt_bracket_gives_a_participle_row_and_no_separable_split():
    perfekt = (ANRUFEN[0], ANRUFEN[1], "# anrufen\n\n## Examples\n\n- Ich habe dich gestern angerufen. :: I called you.\n")
    payload = data([perfekt])
    rows = [r for r in payload["sentences"] if r["entry"] == "anrufen.md"]
    assert [r["german"][r["start"]:r["end"]] for r in rows] == ["angerufen"]
    assert record(payload, "anrufen.md")["separable"] == []
