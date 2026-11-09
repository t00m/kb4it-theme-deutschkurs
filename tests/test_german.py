from deutschkurs.logic.german import present_forms, regular_present, tokens


def test_regular_present_lernen():
    assert regular_present("lernen") == ["lerne", "lernst", "lernt", "lernen"]


def test_regular_present_arbeiten():
    forms = regular_present("arbeiten")
    assert "arbeitest" in forms
    assert "arbeitet" in forms


def test_regular_present_separable():
    assert regular_present("anmelden", "an") == ["melde", "meldest", "meldet", "melden"]


def test_present_forms_strip_pronoun_and_prefix():
    assert present_forms(["ich rufe an", "du rufst an"], "an") == ["rufe", "rufst"]


def test_present_forms_without_prefix():
    assert present_forms(["ich gehe", "er geht", "Sie gehen"]) == ["gehe", "geht", "gehen"]


def test_tokens_umlaut_and_hyphen():
    assert tokens("Die Eltern-Info für Mädchen.") == ["Die", "Eltern-Info", "für", "Mädchen"]
