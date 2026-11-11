from deutschkurs.logic.labels import LABELS
from deutschkurs.logic.render import pairs_html

MISTAKES = '<div class="kb-sect1">\n<h2 class="kb-h2" id="typical-mistakes">Typical mistakes</h2><div class="sectionbody">\n'


def test_loose_list_under_typical_mistakes():
    html = MISTAKES + "<ul>\n<li>\n<p>Ich anrufe dich. :: Ich rufe dich an.</p>\n</li>\n</ul></div></div>"
    out = pairs_html(html, "es", LABELS)
    assert '<p><span class="dk-wrong" lang="de">Ich anrufe dich.</span> ' in out
    assert '<span class="dk-right" lang="de">Ich rufe dich an.</span>' in out
    assert out.count("<p>") == out.count("</p>") == 1
    assert "<p>Ich" not in out


def test_loose_list_in_examples():
    out = pairs_html("<ul>\n<li>\n<p>Hallo! :: ¡Hola!</p>\n</li>\n</ul>", "es", LABELS)
    assert '<p><span class="dk-de" lang="de">Hallo!</span>' in out


def test_nested_list_item_left_alone():
    html = "<ul>\n<li>Outer :: exterior<ul>\n<li>inner :: interior</li>\n</ul>\n</li>\n</ul>"
    out = pairs_html(html, "es", LABELS)
    assert '<span class="dk-tr dk-no-link" lang="es">exterior<ul>' not in out
    assert out.count("<ul>") == 2 and out.count("</ul>") == 2


def test_double_colon_inside_code_is_not_a_separator():
    html = "<ul>\n<li>Use <code>a::b</code> here</li>\n</ul>"
    assert pairs_html(html, "es", LABELS) == html


def test_separator_after_code():
    out = pairs_html("<ul>\n<li>Sag <code>Hallo</code> :: di hola</li>\n</ul>", "es", LABELS)
    assert '<span class="dk-de" lang="de">Sag <code>Hallo</code></span>' in out
    assert '<span class="dk-tr dk-no-link" lang="es">di hola</span>' in out


from deutschkurs.logic.config import DeutschkursConfig
from deutschkurs.logic.course import build_course
from deutschkurs.logic.labels import LABELS
from deutschkurs.logic.parse import Unit
from deutschkurs.logic.render import card, dialogue_html, extras, text_html

TOC = '<div id="toc" class="toc">\n<ul class="sectlevel1">\n<li><a href="#notes">Notes</a></li>\n</ul>\n</div>\n'
DIALOGUE = TOC + """<p>Intro.</p>
<ul>
<li><strong>Mutter:</strong> Hallo! Na, wie geht's? :: Hello! How are you?</li>
<li><strong>ich</strong>: Hallo! <em>Gut</em>, danke. :: Hello! Fine, thanks.</li>
<li>
<p>kein Turn</p>
<ul>
<li>nested item</li>
</ul>
</li>
<li>
<p><strong>Mutter:</strong> Bis morgen!</p>
</li>
</ul>
<p>Ende.</p>
<ul>
<li>zweite Liste</li>
</ul>
<div class="kb-sect1">
<h2 class="kb-h2" id="variations">Variations</h2><div class="sectionbody">
<ul>
<li>2 <strong>ich:</strong> Es geht. :: So-so.</li>
<li>ohne Nummer</li>
<li>9 <strong>ich:</strong> Nie.</li>
</ul>
</div></div><div class="kb-sect1">
<h2 class="kb-h2" id="notes">Notes</h2><div class="sectionbody">
<ul>
<li><strong>Kein:</strong> Turn hier.</li>
</ul></div></div>"""


def dialogue(me="ich"):
    return dialogue_html(DIALOGUE, me, "en", LABELS)


def test_turns_get_anchor_side_and_listen():
    out = dialogue()
    assert '<li id="t1" class="dk-turn dk-other"><span class="dk-speaker dk-no-link">Mutter</span> ' in out
    assert '<span class="dk-de" lang="de">Hallo! Na, wie geht\'s?</span>' in out
    assert 'data-say="Hallo! Na, wie geht&#x27;s?"' in out
    assert '<span class="dk-tr dk-no-link" lang="en">Hello! How are you?</span>' in out
    assert '<li id="t2" class="dk-turn dk-me"><span class="dk-speaker dk-no-link">ich</span> ' in out
    assert '<span class="dk-de" lang="de">Hallo! <em>Gut</em>, danke.</span>' in out
    assert 'data-say="Hallo! Gut, danke."' in out


def test_malformed_turn_keeps_its_number_and_content():
    out = dialogue()
    bad = out.split('<li id="t3" class="dk-turn dk-invalid">', 1)[1].split('<li id="t4"', 1)[0]
    assert "kein Turn" in bad and "<li>nested item</li>" in bad
    assert '<li id="t4" class="dk-turn dk-other">' in out
    assert 'data-say="Bis morgen!"' in out
    assert 'id="t5"' not in out


def test_only_the_first_list_before_the_sections_is_the_dialogue():
    out = dialogue()
    assert out.startswith(TOC + "<p>Intro.</p>")
    assert out.count('<ol class="dk-dialogue">') == 1
    assert "<li>zweite Liste</li>" in out
    assert "<li><strong>Kein:</strong> Turn hier.</li>" in out


def test_toggle_button_is_hidden_until_the_script_shows_it():
    assert ('<button type="button" class="dk-toggle-tr uk-button uk-button-default uk-button-small" hidden data-show="Show translations" '
            'data-hide="Hide translations">') in dialogue()


def test_dialogue_without_translations_has_no_toggle():
    out = dialogue_html("<ul>\n<li><strong>A:</strong> Hallo.</li>\n</ul>", "ich", "en", LABELS)
    assert 'id="t1"' in out and "dk-toggle-tr" not in out


def test_me_names_the_learner():
    out = dialogue(me="mutter")
    assert '<li id="t1" class="dk-turn dk-me">' in out
    assert '<li id="t2" class="dk-turn dk-other">' in out


def test_variations_link_to_the_turn_they_replace():
    out = dialogue()
    assert ('<li id="v1" class="dk-turn dk-variation dk-me"><a class="dk-replaces" href="#t2">2</a> '
            '<span class="dk-speaker dk-no-link">ich</span>') in out
    assert "<li>ohne Nummer</li>" in out
    assert '<li id="v2" class="dk-turn dk-variation dk-me"><span class="dk-replaces">9</span> ' in out
    assert 'href="#t9"' not in out


def test_page_without_a_list_is_left_alone():
    html = TOC + "<p>Nur Text.</p>"
    assert dialogue_html(html, "ich", "en", LABELS) == html


TEXT = TOC + """<p>Liebe Eltern,</p>
<blockquote>
<p>Dear parents,</p>
</blockquote>
<p>am Freitag machen wir einen <em>Ausflug</em>.
Bitte geben Sie Ihrem Kind eine Brotdose mit.</p>
<blockquote>
<p>On Friday we are going on a trip.</p>
</blockquote>
<p><img alt="Foto" src="resources/foto.png" /></p>
<ul>
<li>eine Liste</li>
</ul>
<div>html block <p>Viele Grüße</p></div>
<p>Kein Satz im Index.</p>
<blockquote>
<p>Zitat ohne Satz davor.</p>
</blockquote>
<div class="kb-sect2">
<h3 class="kb-h3" id="u">U</h3><div class="sectionbody">
<p>Viele Grüße</p>
</div></div><div class="kb-sect1">
<h2 class="kb-h2" id="notes">Notes</h2><div class="sectionbody">
<p>Liebe Eltern,</p></div></div>"""
UNITS = (Unit("s1", "Liebe Eltern,"),
         Unit("s2", "am Freitag machen wir einen Ausflug. Bitte geben Sie Ihrem Kind eine Brotdose mit."),
         Unit("s3", "Fehlt auf der Seite."),
         Unit("s4", "Viele Grüße"))


def text():
    return text_html(TEXT, UNITS, "en", LABELS)


def test_paragraphs_get_the_anchor_of_their_unit():
    out = text()
    assert ('<p id="s1" class="dk-sentence"><span class="dk-de" lang="de">Liebe Eltern,</span> '
            '<button type="button" class="dk-listen uk-button uk-button-default uk-button-small" data-say="Liebe Eltern,">Listen</button> '
            '<button type="button" class="dk-listen dk-slow uk-button uk-button-default uk-button-small" data-say="Liebe Eltern," '
            'data-rate="slow">Slow</button></p>') in out
    assert '<p id="s2" class="dk-sentence"><span class="dk-de" lang="de">am Freitag machen wir einen <em>' in out
    assert 'data-say="am Freitag machen wir einen Ausflug. Bitte geben Sie Ihrem Kind eine Brotdose mit."' in out


def test_anchor_follows_the_unit_not_the_position():
    out = text()
    assert 'id="s3"' not in out
    assert '<div class="sectionbody">\n<p id="s4" class="dk-sentence">' in out
    assert "<div>html block <p>Viele Grüße</p></div>" in out


def test_other_blocks_and_sections_are_left_alone():
    out = text()
    assert '<p><img alt="Foto" src="resources/foto.png" /></p>' in out
    assert "<p>Kein Satz im Index.</p>" in out
    assert out.endswith("<p>Liebe Eltern,</p></div></div>")
    assert out.count('id="s1"') == 1


def test_translation_right_after_a_sentence_is_folded():
    out = text()
    fold = '<details class="dk-fold dk-tr-fold" lang="en"><summary>Translation</summary><blockquote>'
    assert out.count(fold) == 2
    assert fold + "\n<p>Dear parents,</p>\n</blockquote></details>" in out
    assert "</p>\n<blockquote>\n<p>Zitat ohne Satz davor.</p>" in out


def doc(doc_id, text, **props):
    return doc_id, {k: tuple(v.split(", ")) for k, v in props.items()}, text


WORD = dict(Type="Word", Level="A1", PartOfSpeech="noun", Article="der", Translation="x")
GRUSS = ("# Gruß\n\n- **Mutter:** Hast du einen Termin? :: Do you have an appointment?\n"
         "- **ich:** Ja, weil ich krank bin.\n")
BRIEF = "# Brief\n\nDer Termin ist am Freitag.\n\n> The appointment is on Friday.\n\nViele Grüße\n"
SCHULTOR = "# Am Schultor\n\n## I can\n\n- [x] Ich kann grüßen.\n- [ ] Ich kann fragen.\n"
DOCS = [
    doc("termin.md", "# Termin\n", Situation="Am Schultor", **WORD),
    doc("weil.md", "# weil\n\n## Explanation\n\nx\n", Type="Grammar", Level="A2", Area="Sentences", Marker="weil, dass"),
    doc("gruss.md", GRUSS, Type="Conversation", Level="A1", Kind="model", Situation="Am Schultor, Nirgendwo"),
    doc("brief.md", BRIEF, Type="Text", Level="A2", Genre="School letter", Received="2026-11-09",
        Deadline="2026-11-20", Reply="yes", Situation="Am Schultor", Checked="attested"),
    doc("situation-am-schultor.md", SCHULTOR, Type="Situation", NextTime="2026-11-10"),
]


def built(docs=DOCS):
    course = build_course(docs, DeutschkursConfig())
    return course, {name: entry for name, entry in course.entries.items()}


def test_conversation_card_shows_kind_and_situations():
    course, entries = built()
    data = card(entries["gruss.md"], course, LABELS, course.url)
    assert data["badges"][0] == ("dk-badge dk-kind dk-kind-model", "model", "ConversationKind_model.html")
    assert ("Situation", [("Am Schultor", "situation-am-schultor.html"), ("Nirgendwo", "")]) in data["links"]


def test_text_card_shows_genre_dates_and_reply():
    course, entries = built()
    data = card(entries["brief.md"], course, LABELS, course.url)
    assert ("dk-badge dk-genre", "School letter", "Genre_School_letter.html") in data["badges"]
    assert ("dk-badge dk-reply", "Needs a reply", "") in data["badges"]
    assert ("Received", "2026-11-09") in data["facts"] and ("Deadline", "2026-11-20") in data["facts"]
    assert ("dk-badge dk-checked dk-checked-attested", "attested", "") in data["badges"]


def test_situation_card_has_no_level_and_no_checked_badge():
    course, entries = built()
    data = card(entries["situation-am-schultor.md"], course, LABELS, course.url)
    assert data["badges"] == []
    assert ("I can", "1 / 2") in data["facts"] and ("Next time", "2026-11-10") in data["facts"]


def test_word_card_links_its_situation():
    course, entries = built()
    data = card(entries["termin.md"], course, LABELS, course.url)
    assert ("Situation", [("Am Schultor", "situation-am-schultor.html")]) in data["links"]


def test_situation_lists_its_entries_by_type():
    course, entries = built()
    data = extras(entries["situation-am-schultor.md"], course, LABELS, course.url)
    assert data["related"] == [
        ("Conversations", [("Gruß", "gruss.html", "model")]),
        ("Texts", [("Brief", "brief.html", "")]),
        ("Vocabulary", [("Termin", "termin.html", "")]),
    ]
    assert data["next_time"] == "2026-11-10"


def test_where_it_appears_real_sources_first():
    course, entries = built()
    data = extras(entries["termin.md"], course, LABELS, course.url)
    assert [(o["href"], o["title"], o["kind"]) for o in data["occurrences"]] == [
        ("brief.html#s1", "Brief", ""), ("gruss.html#t1", "Gruß", "model")]
    assert data["occurrences"][0]["german"] == "Der Termin ist am Freitag."
    assert data["occurrences"][0]["translation"] == "The appointment is on Friday."
    assert data["more"] == 0


def test_where_it_appears_shows_at_most_ten():
    lines = "".join(f"- **A:** Termin {n}.\n" for n in range(13))
    docs = [DOCS[0], doc("lang.md", "# Lang\n\n" + lines, Type="Conversation", Level="A1", Kind="real")]
    course, entries = built(docs)
    data = extras(entries["termin.md"], course, LABELS, course.url)
    assert len(data["occurrences"]) == 10 and data["more"] == 3


def test_grammar_lists_marker_candidates():
    course, entries = built()
    data = extras(entries["weil.md"], course, LABELS, course.url)
    assert [o["href"] for o in data["candidates"]] == ["gruss.html#t2"]
    assert data["occurrences"] == []


def test_text_shows_coverage_and_deadline():
    course, entries = built()
    data = extras(entries["brief.md"], course, LABELS, course.url)
    assert data["deadline"] == "2026-11-20"
    assert data["coverage"].total == course.coverage["brief.md"].total
    assert "Freitag" in data["coverage"].missing and "Termin" not in data["coverage"].missing
    assert extras(entries["termin.md"], course, LABELS, course.url)["coverage"] is None


def test_task_list_item_keeps_its_checkbox():
    html = ('<ul class="task-list">\n<li class="task-list-item"><input type="checkbox" disabled checked/> '
            'Ich kann grüßen. :: I can greet.</li>\n</ul>')
    out = pairs_html(html, "en", LABELS)
    assert ('<li class="dk-pair task-list-item"><input type="checkbox" disabled checked/> '
            '<span class="dk-de" lang="de">Ich kann grüßen.</span>') in out
    assert '<span class="dk-tr dk-no-link" lang="en">I can greet.</span>' in out
    assert "::" not in out


def test_dates_with_a_time_keep_only_the_day():
    docs = [doc("brief.md", BRIEF, Type="Text", Level="A2", Deadline="2026-11-20 14:00"),
            doc("alt.md", BRIEF, Type="Text", Level="A2", Deadline="20.11.2026")]
    course, entries = built(docs)
    assert extras(entries["brief.md"], course, LABELS, course.url)["deadline"] == "2026-11-20"
    assert extras(entries["alt.md"], course, LABELS, course.url)["deadline"] == ""


def test_word_family_links_a_word_not_a_situation_with_the_same_title():
    word = "---\nArticle: der\nLevel: A1\nPartOfSpeech: noun\nType: Word\n---\n\n# Abend\n"
    family = {"Type": ("Word",), "Level": ("A1",), "Article": ("der",), "PartOfSpeech": ("noun",),
              "Family": ("der Abend",)}
    docs = [("a-abend.md", {"Type": ("Situation",)}, "---\nType: Situation\n---\n\n# Abend\n"),
            ("abend.md", {"Type": ("Word",), "Level": ("A1",), "Article": ("der",), "PartOfSpeech": ("noun",)}, word),
            ("feierabend.md", family, word.replace("# Abend", "# Feierabend"))]
    course, entries = built(docs)
    data = card(entries["feierabend.md"], course, LABELS, course.url)
    assert ("Word family", [("der Abend", "abend.html")]) in data["links"]


def test_every_listen_button_has_a_slow_button():
    out = pairs_html("<ul>\n<li>Hallo! :: Hello!</li>\n</ul>", "en", LABELS)
    assert ('<button type="button" class="dk-listen dk-slow uk-button uk-button-default uk-button-small" data-say="Hallo!" '
            'data-rate="slow">Slow</button>') in out


def test_my_turns_speak_with_my_voice():
    out = dialogue()
    mine = out.split('<li id="t2"', 1)[1].split("</li>", 1)[0]
    other = out.split('<li id="t1"', 1)[1].split("</li>", 1)[0]
    assert mine.count('data-me="true"') == 2
    assert "data-me" not in other


def test_dialogue_has_play_all():
    out = dialogue()
    assert ('<div class="dk-dialogue-box"><button type="button" class="dk-play-all uk-button uk-button-primary uk-button-small" '
            'data-play=".dk-dialogue .dk-turn">Play all</button>') in out


def test_text_has_play_all_before_the_first_sentence():
    out = text()
    bar = ('<p class="dk-play-bar"><button type="button" class="dk-play-all uk-button uk-button-primary uk-button-small" '
           'data-play=".dk-sentence">Play all</button></p>')
    assert out.count(bar) == 1
    assert out.index(bar) < out.index('<p id="s1"')
