"""Theme settings: the "deutschkurs" block of repo.json."""

import re
from dataclasses import dataclass, field
from typing import Optional


COLOR = re.compile(r"^(#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})|[a-zA-Z]+"
                   r"|(?:rgb|rgba|hsl|hsla)\([0-9.,%\s/]+\))$")


def valid_color(value) -> bool:
    """True for a CSS colour: hex, a colour name, or rgb()/hsl() with numbers only."""
    return isinstance(value, str) and bool(COLOR.match(value.strip()))


def _gender_colors() -> dict:
    return {"m": "#1f6feb", "f": "#cf222e", "n": "#1a7f37", "pl": "#d4760a"}


@dataclass
class DeutschkursConfig:
    native: str = "en"
    labels: dict = field(default_factory=dict)
    learner_level: str = "A2"
    german_from: str = "B1"
    strict: bool = False
    speech: bool = True
    speech_lang: str = "de-DE"
    voice: Optional[str] = None
    voice_me: Optional[str] = None
    slow_rate: float = 0.75
    accent: str = "#c0392b"
    gender_colors: dict = field(default_factory=_gender_colors)
    topics: Optional[list] = None
    daily_reviews: int = 40
    daily_new: int = 5
    weekly_new: int = 10
    prepare_days: int = 7
    privacy_allow: list = field(default_factory=list)
