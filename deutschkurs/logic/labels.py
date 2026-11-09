"""Interface strings, in English; repo.json can override single strings."""

from typing import Mapping

LABELS: dict[str, str] = {
    "home": "Home",
    "today": "Today",
    "vocabulary": "Vocabulary",
    "verbs": "Verbs",
    "chunks": "Chunks",
    "grammar": "Grammar",
    "skill": "Assistant skill",
    "search": "Search",
    "word": "Word",
    "type": "Type",
    "verb": "Verb",
    "chunk": "Chunk",
    "article": "Article",
    "plural": "Plural",
    "plural_only": "Plural only",
    "no_plural": "No plural",
    "translation": "Translation",
    "level": "Level",
    "topic": "Topic",
    "register": "Register",
    "checked": "Checked",
    "part_of_speech": "Part of speech",
    "stress": "Stress",
    "regional": "Also said",
    "family": "Word family",
    "forms": "Forms",
    "examples": "Examples",
    "variants": "Variants",
    "usage": "Usage",
    "notes": "Notes",
    "pronunciation": "Pronunciation",
    "false_friends": "False friends",
    "typical_mistakes": "Typical mistakes",
    "explanation": "Explanation",
    "simple_german": "Simple German",
    "present": "Present",
    "preterite": "Preterite",
    "perfekt": "Perfekt",
    "konjunktiv": "Konjunktiv II",
    "separable": "Separable",
    "irregular": "Irregular",
    "reflexive": "Reflexive",
    "government": "Takes",
    "area": "Area",
    "case": "Case",
    "tense": "Tense",
    "verbs_with_case": "Verbs with this case",
    "listen": "Listen",
    "no_voice": "No German voice is installed on this device, so audio is off. Add a German text-to-speech voice in the device settings.",
    "filter": "Filter",
    "all": "All",
    "count": "Entries",
    "latest": "Latest additions",
    "documents": "Other pages",
    "untitled": "Untitled",
    "filter_placeholder": "Type to filter",
    "not_found_title": "Page not found",
    "not_found_text": "This page does not exist or has moved. Go to the home page:",
    "built_with": "Built with KB4IT on",
    "skill_intro": "This course comes with a skill: instructions an AI assistant follows to help you add entries from real material, correct your German and fix build problems. It removes personal data before anything else.",
    "skill_claude": "Claude Code: copy the folder skills/deutschkurs/ of this site to ~/.claude/skills/deutschkurs/.",
    "skill_other": "Another assistant: give it these instructions and the files in reference/:",
    "skill_site": "This list of the entries of your course helps the assistant reuse their names:",
}


def labels(overrides: Mapping[str, str]) -> tuple[dict[str, str], list[str]]:
    """The labels with overrides applied, and the override keys that name no label."""
    merged = dict(LABELS)
    unknown = []
    for key, text in (overrides or {}).items():
        if key in LABELS:
            merged[key] = str(text)
        else:
            unknown.append(key)
    return merged, sorted(unknown)
