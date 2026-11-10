"""Small German helpers: tokens and present tense forms."""

import re

WORD = re.compile(r"[A-Za-zÄÖÜäöüß]+(?:-[A-Za-zÄÖÜäöüß]+)*")
PRONOUNS = {"ich", "du", "er", "sie", "es", "wir", "ihr", "Sie", "man"}
FOLD = str.maketrans({"ä": "a", "ö": "o", "ü": "u", "ß": "ss", "Ä": "a", "Ö": "o", "Ü": "u"})
# Function words every learner meets in the first weeks; coverage counts them as known.
BASIC = frozenset("""
der die das den dem des ein eine einen einem einer eines kein keine keinen keinem keiner
ich du er sie es wir ihr man mich dich sich uns euch mir dir ihm ihn ihnen
mein meine meinen meinem meiner dein deine deinen deinem deiner sein seine seinen seinem seiner
ihre ihren ihrem ihrer unser unsere unseren unserem unserer euer eure euren eurem eurer
dieser diese dieses diesen diesem
und oder aber denn sondern dass ob wenn weil als
nicht ja nein doch auch nur noch schon sehr so da hier dort jetzt dann
in an auf zu mit von bei nach aus für um durch über unter vor hinter neben zwischen bis ohne gegen seit
im am zum zur vom beim ins ans
bin bist ist sind seid war waren habe hast hat haben habt hatte hatten werde wirst wird werden
wie was wer wo wann warum wohin woher
bitte danke hallo
""".split())


def sort_key(text: str) -> tuple[str, str]:
    """Sort German text case-insensitively, umlauts next to their base letter."""
    return text.translate(FOLD).casefold(), text


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
