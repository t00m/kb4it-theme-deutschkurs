"""Small German helpers: tokens and present tense forms."""

import re

WORD = re.compile(r"[A-Za-zÄÖÜäöüß]+(?:-[A-Za-zÄÖÜäöüß]+)*")
PRONOUNS = {"ich", "du", "er", "sie", "es", "wir", "ihr", "Sie", "man"}


def tokens(text: str) -> list[str]:
    """Word tokens of a text: letters, umlauts, inner hyphens."""
    return WORD.findall(text)


def _unique(items: list[str]) -> list[str]:
    seen: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.append(item)
    return seen


def regular_present(infinitive: str, prefix: str = "") -> list[str]:
    """Present forms of a regular verb without pronouns; a separable prefix is removed first."""
    base = infinitive.strip()
    if prefix and base.startswith(prefix) and len(base) > len(prefix):
        base = base[len(prefix):]
    stem = base[:-2] if base.endswith("en") else base[:-1]
    if not stem:
        return []
    if stem.endswith(("t", "d")):
        du, er = stem + "est", stem + "et"
    elif stem.endswith(("s", "ß", "z", "x")):
        du, er = stem + "t", stem + "t"
    else:
        du, er = stem + "st", stem + "t"
    return _unique([stem + "e", du, er, base])


def present_forms(values, prefix: str = "") -> list[str]:
    """Verb forms of 'Present' values such as 'ich rufe an': pronoun and prefix removed."""
    forms = []
    for value in values:
        words = value.split()
        if words and words[0] in PRONOUNS:
            words = words[1:]
        if prefix and len(words) > 1 and words[-1] == prefix:
            words = words[:-1]
        if words:
            forms.append(words[0])
    return _unique(forms)
