from deutschkurs.logic.config import DeutschkursConfig


def test_defaults():
    c = DeutschkursConfig()
    assert c.native == "es"
    assert c.labels == {}
    assert c.learner_level == "A2"
    assert c.german_from == "B1"
    assert c.strict is False
    assert c.speech is True
    assert c.speech_lang == "de-DE"
    assert c.voice is None
    assert c.voice_me is None
    assert c.slow_rate == 0.75
    assert c.accent == "#c0392b"
    assert c.gender_colors == {"m": "#1f6feb", "f": "#cf222e", "n": "#1a7f37", "pl": "#d4760a"}
    assert c.topics is None
    assert c.daily_reviews == 40
    assert c.daily_new == 5
    assert c.weekly_new == 10
    assert c.prepare_days == 7
    assert c.privacy_allow == []
