from deutschkurs.logic.labels import LABELS, labels


def test_override():
    merged, unknown = labels({"vocabulary": "Wörter"})
    assert merged["vocabulary"] == "Wörter"
    assert unknown == []
    assert LABELS["vocabulary"] == "Vocabulary"


def test_unknown_override_reported():
    assert labels({"nope": "x"})[1] == ["nope"]


def test_no_em_dash():
    assert not any("—" in text for text in LABELS.values())
