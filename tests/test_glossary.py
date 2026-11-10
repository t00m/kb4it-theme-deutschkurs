from deutschkurs.logic.glossary import build_glossary, link_html
from deutschkurs.logic.model import entry_from


def make(doc_id, markdown, **props):
    return entry_from(doc_id, {k: tuple(v.split(", ")) for k, v in props.items()}, markdown)


ENTRIES = [
    make("termin", "# Termin", Type="Word", PartOfSpeech="noun", Article="der", Plural="die Termine"),
    make("kind", "# Kind", Type="Word", PartOfSpeech="noun", Article="das", Plural="die Kinder"),
    make("eltern", "# Eltern", Type="Word", PartOfSpeech="noun", PluralOnly="yes"),
    make("krank", "# krank", Type="Word", PartOfSpeech="adjective"),
    make("anrufen", "# anrufen", Type="Verb", Separable="yes", Prefix="an",
         Present="ich rufe an, du rufst an, er ruft an", Participle="angerufen"),
    make("lernen", "# lernen", Type="Verb", Participle="gelernt"),
    make("bescheid-sagen", "# Bescheid sagen", Type="Chunk"),
]
G = build_glossary(ENTRIES)


def link(html, self_id="none"):
    return link_html(html, G, self_id, lambda i: f"{i}.html")


def test_links_noun_with_gender():
    out = link("<p>Ein Termin</p>")
    assert '<a class="dk-link dk-m" href="termin.html">Termin</a>' in out


def test_links_plural_form():
    assert '<a class="dk-link dk-pl" href="termin.html">Termine</a>' in link("<p>Zwei Termine</p>")


def test_plural_only_noun():
    assert 'class="dk-link dk-pl" href="eltern.html"' in link("<p>Die Eltern</p>")


def test_non_noun_has_no_gender():
    assert '<a class="dk-link" href="krank.html">krank</a>' in link("<p>Ich bin krank.</p>")


def test_non_noun_case_insensitive():
    assert 'href="krank.html">Krank</a>' in link("<p>Krank bin ich.</p>")


def test_whole_tokens_only():
    assert link("<p>Kindergarten</p>") == "<p>Kindergarten</p>"


def test_noun_needs_capital():
    assert link("<p>kind</p>") == "<p>kind</p>"


def test_skips_headings_code_links_blockquote():
    for html in ("<h2>Termin</h2>", "<code>Termin</code>", '<a href="x">Termin</a>',
                 "<blockquote><p>Termin</p></blockquote>", '<span class="dk-no-link">Termin</span>'):
        assert link(html) == html


def test_no_self_link():
    assert link("<p>Termin</p>", self_id="termin") == "<p>Termin</p>"


def test_chunk_phrase_longest_first():
    out = link("<p>Sag mir Bescheid sagen</p>")
    assert out.count("<a ") == 1
    assert 'href="bescheid-sagen.html">Bescheid sagen</a>' in out


def test_split_separable():
    out = link("<p>Ich rufe dich morgen an.</p>")
    assert '<a class="dk-link dk-bracket" href="anrufen.html">rufe</a>' in out
    assert '<a class="dk-link dk-bracket" href="anrufen.html">an</a>' in out


def test_separable_prefix_alone_not_linked():
    assert link("<p>Ich denke an dich.</p>") == "<p>Ich denke an dich.</p>"


def test_participle():
    assert 'href="anrufen.html">angerufen</a>' in link("<p>Ich habe angerufen.</p>")


def test_generated_present_of_regular_verb():
    assert 'href="lernen.html">lernt</a>' in link("<p>Sie lernt Deutsch.</p>")


def test_attributes_untouched():
    assert link('<p title="Termin">x</p>') == '<p title="Termin">x</p>'


def test_entities_kept():
    assert link("<p>Termin &amp; Kind</p>").count("&amp;") == 1


def test_quoted_attribute_with_greater_than():
    html = '<span title="a > Kind">x</span>'
    assert link(html) == html


def test_unmatched_closing_tag_keeps_skip():
    for html in ("<pre></span>Termin</pre>", "<h2>Termin</b> Kind</h2>"):
        assert link(html) == html


def test_separable_verbs_sharing_a_stem():
    g = build_glossary(ENTRIES + [make("zurueckrufen", "# zurückrufen", Type="Verb", Separable="yes",
                                       Prefix="zurück", Present="ich rufe zurück, du rufst zurück",
                                       Participle="zurückgerufen")])
    back = link_html("<p>Ich rufe dich zurück.</p>", g, "none", lambda i: f"{i}.html")
    assert 'href="zurueckrufen.html">rufe</a>' in back and 'href="zurueckrufen.html">zurück</a>' in back
    on = link_html("<p>Ich rufe dich an.</p>", g, "none", lambda i: f"{i}.html")
    assert 'href="anrufen.html">rufe</a>' in on


def test_find_spans_gives_positions_and_entries():
    from deutschkurs.logic.glossary import find_spans
    text = "Ich rufe das Kind an."
    assert [(text[a:b], doc) for a, b, doc, _ in find_spans(text, G)] == [
        ("rufe", "anrufen"), ("Kind", "kind"), ("an", "anrufen")]
    assert find_spans("Das Kind.", G, "kind") == []
