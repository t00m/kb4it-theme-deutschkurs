import subprocess

import pytest

from conftest import KB4IT, build_site, prepare_site, warnings
from deutschkurs.logic.config import valid_color
from test_pages import TERMIN


def test_valid_color():
    for good in ("#c0392b", "#fff", "red", "rgb(1, 2, 3)", "hsl(10 50% 50%)"):
        assert valid_color(good), good
    for bad in ("red;} body{display:none", "url(x)", "#12345", "", "expression(alert(1))"):
        assert not valid_color(bad), bad


def test_bad_colour_is_replaced_and_warned(tmp_path):
    site = build_site(tmp_path, {"termin.md": TERMIN},
                      {"accent": "red;} body{display:none", "gender_colors": {"m": "blue", "f": "x;y"}},
                      starter=False)
    page = site.page("termin.html")
    assert "display:none" not in page
    assert "--dk-accent: #c0392b" in page and "--dk-m: blue" in page and "--dk-f: #cf222e" in page
    log = "\n".join(warnings(site.log))
    assert "COLOR_INVALID key=accent" in log and "COLOR_INVALID key=gender_colors.f" in log


def test_strict_stops_the_build(tmp_path):
    config = prepare_site(tmp_path, {"bad.md": "---\nType: Word\n---\n\n# Bad\n"}, {"strict": True}, starter=False)
    run = subprocess.run([KB4IT, "build", str(config)], capture_output=True, text=True)
    assert run.returncode != 0


def test_labels_reach_every_text(tmp_path):
    labels = {"not_found_title": "Nicht gefunden", "built_with": "Gebaut mit KB4IT am", "level": "Stufe",
              "skill_intro": "Eine Anleitung."}
    site = build_site(tmp_path, {"termin.md": TERMIN}, {"labels": labels}, starter=False)
    assert "Nicht gefunden" in site.page("404.html")
    assert "Gebaut mit KB4IT am" in site.page("termin.html")
    assert "<h1>Stufe</h1>" in site.page("Level.html")
    assert "Stufe: A1" in site.page("Level_A1.html")
    assert "Eine Anleitung." in site.page("skill.html")
    assert not [line for line in warnings(site.log) if "LABEL_UNKNOWN" in line]


def test_slow_rate_reaches_the_page(tmp_path):
    site = build_site(tmp_path, {"termin.md": TERMIN}, {"slow_rate": 0.6}, starter=False)
    assert 'data-slow-rate="0.6"' in site.page("termin.html")
    assert not [line for line in warnings(site.log) if "SETTING_INVALID" in line]


@pytest.mark.parametrize("rate", [0, -1, 2.5])
def test_bad_slow_rate_is_replaced_and_warned(tmp_path, rate):
    site = build_site(tmp_path, {"termin.md": TERMIN}, {"slow_rate": rate}, starter=False)
    assert 'data-slow-rate="0.75"' in site.page("termin.html")
    assert [line for line in warnings(site.log) if "SETTING_INVALID key=slow_rate" in line]
