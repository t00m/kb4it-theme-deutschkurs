from deutschkurs.logic.glossary import build_glossary
from deutschkurs.logic.model import entry_from


def make(doc_id, markdown, **props):
    return entry_from(doc_id, {k: tuple(v.split(", ")) for k, v in props.items()}, markdown)


WORDS = [
    make("termin.md", "# Termin", Type="Word", PartOfSpeech="noun", Article="der", Plural="die Termine"),
    make("anrufen.md", "# anrufen", Type="Verb", Separable="yes", Prefix="an",
         Present="ich rufe an, du rufst an, er ruft an", Participle="angerufen"),
    make("bis-morgen.md", "# Bis morgen", Type="Chunk"),
]
MODEL = make("model.md", "# Modell\n\n- **A:** Ich habe einen Termin. :: I have an appointment.\n"
             "- **ich:** Bis morgen!\n\n## Variations\n\n- 2 **ich:** Ich rufe dich an. :: I will call you.\n",
             Type="Conversation", Kind="model")
REAL = make("real.md", "# Echt\n\n- **A:** Zwei Termine, bitte.\n", Type="Conversation", Kind="real")
REMEMBERED = make("remembered.md", "# Erinnert\n\n- **A:** Der Termin ist morgen.\n", Type="Conversation",
                  Kind="reconstructed")
LETTER = make("brief.md", "# Brief\n\nIhr Termin ist am Montag.\n\n> Your appointment is on Monday.\n\nKein Wort.\n",
              Type="Text")
ENTRIES = [*WORDS, MODEL, REAL, REMEMBERED, LETTER]
G = build_glossary(ENTRIES)


def index():
    from deutschkurs.logic.index import build_index
    return build_index(ENTRIES, G)


def test_index_lists_every_unit_that_holds_a_form():
    found = index()["termin.md"]
    assert {(o.doc, o.anchor) for o in found} == {("brief.md", "s1"), ("real.md", "t1"), ("remembered.md", "t1"),
                                                  ("model.md", "t1")}


def test_index_real_sources_first_model_last():
    assert [o.doc for o in index()["termin.md"]] == ["brief.md", "real.md", "remembered.md", "model.md"]
    assert [o.kind for o in index()["termin.md"]] == ["", "real", "reconstructed", "model"]


def test_index_keeps_sentence_translation_and_title():
    first = index()["termin.md"][0]
    assert (first.german, first.translation, first.title) == ("Ihr Termin ist am Montag.",
                                                              "Your appointment is on Monday.", "Brief")


def test_index_finds_chunks_and_split_verbs_in_variations():
    assert [(o.doc, o.anchor) for o in index()["bis-morgen.md"]] == [("model.md", "t2")]
    assert [(o.doc, o.anchor) for o in index()["anrufen.md"]] == [("model.md", "v1")]


def test_index_has_no_entry_without_sentences():
    assert set(index()) == {"termin.md", "bis-morgen.md", "anrufen.md"}


def test_coverage_counts_distinct_words():
    from deutschkurs.logic.index import coverage
    result = coverage(LETTER.units, G, frozenset())
    # ihr, ist, am and kein are basic words; Termin has an entry.
    assert (result.total, result.covered, result.missing) == (7, 5, ("Montag", "Wort"))
    assert result.percent == 71


def test_coverage_known_words_setting():
    from deutschkurs.logic.index import coverage
    assert coverage(LETTER.units, G, frozenset({"montag"})).missing == ("Wort",)


def test_coverage_leaves_out_names_placeholders_and_letters():
    from deutschkurs.logic.index import coverage
    text = make("x.md", "# X\n\nFrau A. und Herr Müller wohnen in [Adresse]. Frau Schmidt nicht.\n", Type="Text")
    result = coverage(text.units, G, frozenset())
    assert result.missing == ("Frau", "Herr", "wohnen")


def test_coverage_shows_the_form_inside_a_sentence():
    from deutschkurs.logic.index import coverage
    text = make("x.md", "# X\n\nMorgen regnet es. Das Wetter ist morgen schlecht.\n", Type="Text")
    assert coverage(text.units, G, frozenset()).missing == ("morgen", "regnet", "schlecht", "Wetter")


def test_coverage_of_nothing_is_full():
    from deutschkurs.logic.index import coverage
    assert coverage((), G, frozenset()).percent == 100


def test_marker_hits_whole_words_only():
    from deutschkurs.logic.index import marker_hits
    weil = make("weil.md", "# W\n\n- **A:** Ich komme nicht, weil ich krank bin.\n- **B:** Eine Weile, ja.\n",
                Type="Conversation", Kind="real")
    hits = marker_hits(("weil", "dass"), [weil, LETTER])
    assert [(o.doc, o.anchor) for o in hits] == [("weil.md", "t1")]


def test_marker_hits_without_markers():
    from deutschkurs.logic.index import marker_hits
    assert marker_hits((), ENTRIES) == []


def test_photo_sentences_come_after_texts_and_before_real_conversations():
    from deutschkurs.logic.index import build_index
    photo = make("schild.md", "# Schild\n\n![x](resources/photos/s.webp)\n\n## Transcription\n\nTermin heute!\n",
                 Type="Photo")
    found = build_index([*ENTRIES, photo], build_glossary([*ENTRIES, photo]))["termin.md"]
    assert [(o.doc, o.anchor) for o in found][:3] == [("brief.md", "s1"), ("schild.md", "p1"), ("real.md", "t1")]
