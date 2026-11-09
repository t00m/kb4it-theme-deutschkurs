from deutschkurs.logic.render import pairs_html

MISTAKES = '<div class="kb-sect1">\n<h2 class="kb-h2" id="typical-mistakes">Typical mistakes</h2><div class="sectionbody">\n'


def test_loose_list_under_typical_mistakes():
    html = MISTAKES + "<ul>\n<li>\n<p>Ich anrufe dich. :: Ich rufe dich an.</p>\n</li>\n</ul></div></div>"
    out = pairs_html(html, "es", "Listen")
    assert '<p><span class="dk-wrong" lang="de">Ich anrufe dich.</span> ' in out
    assert '<span class="dk-right" lang="de">Ich rufe dich an.</span>' in out
    assert out.count("<p>") == out.count("</p>") == 1
    assert "<p>Ich" not in out


def test_loose_list_in_examples():
    out = pairs_html("<ul>\n<li>\n<p>Hallo! :: ¡Hola!</p>\n</li>\n</ul>", "es", "Listen")
    assert '<p><span class="dk-de" lang="de">Hallo!</span>' in out


def test_nested_list_item_left_alone():
    html = "<ul>\n<li>Outer :: exterior<ul>\n<li>inner :: interior</li>\n</ul>\n</li>\n</ul>"
    out = pairs_html(html, "es", "Listen")
    assert '<span class="dk-tr dk-no-link" lang="es">exterior<ul>' not in out
    assert out.count("<ul>") == 2 and out.count("</ul>") == 2


def test_double_colon_inside_code_is_not_a_separator():
    html = "<ul>\n<li>Use <code>a::b</code> here</li>\n</ul>"
    assert pairs_html(html, "es", "Listen") == html


def test_separator_after_code():
    out = pairs_html("<ul>\n<li>Sag <code>Hallo</code> :: di hola</li>\n</ul>", "es", "Listen")
    assert '<span class="dk-de" lang="de">Sag <code>Hallo</code></span>' in out
    assert '<span class="dk-tr dk-no-link" lang="es">di hola</span>' in out
