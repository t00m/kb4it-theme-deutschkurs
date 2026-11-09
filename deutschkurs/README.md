# deutschkurs theme

A KB4IT theme that turns your own Markdown files into an offline German course built around real life. Version 0.1.0, for KB4IT 0.12.x.

## Entries

One file per entry in `source/`, with YAML frontmatter, one `#` title and optional `##` sections. The full reference, with an example per type, is in `skill/deutschkurs/reference/entry-types.md`.

| Type | What | Required properties |
|---|---|---|
| Word | A noun, adjective or other word | `Level`, `Translation`, `PartOfSpeech`; `Article` for nouns |
| Verb | A verb | `Level`, `Translation`, `Participle`, `Auxiliary`; `Prefix` when `Separable: yes` |
| Chunk | A fixed phrase | `Level`, `Translation` |
| Grammar | One grammar point | `Level`, `Area`, and a `## Explanation` section |

Translation pairs are list items: `- German sentence :: translation`.

Common optional properties: `Checked` (`unchecked`, `assistant`, `reference`, `native`, `attested`), `Topic`, `Source`, `Date`, `Tag`.

KB4IT splits property values on commas, so sentences and explanations go in the body. A noun without plural has `Plural: none`.

## Settings

In `config/repo.json`, block `"deutschkurs"`:

| Key | Default | Meaning |
|---|---|---|
| `native` | `es` | Language of translations |
| `labels` | `{}` | Overrides of single interface strings |
| `learner_level` | `A2` | Your level |
| `german_from` | `B1` | From this level, grammar pages show the simple German version first |
| `strict` | `false` | Metadata problems stop the build |
| `speech` | `true` | Listen buttons |
| `speech_lang` | `de-DE` | Preferred voice language |
| `voice` | none | Name of a preferred voice |
| `accent` | `#c0392b` | Accent colour |
| `gender_colors` | `{"m": "#1f6feb", "f": "#cf222e", "n": "#1a7f37", "pl": "#d4760a"}` | Colours of der, die, das and plural |
| `topics` | none | When set, the only allowed `Topic` values |

Settings for later versions (`voice_me`, `slow_rate`, `daily_reviews`, `daily_new`, `weekly_new`, `prepare_days`, `privacy_allow`) are accepted and not used yet.

## Pages

Home, Vocabulary, Verbs, Chunks, Grammar, Assistant skill, search, and facet pages `Level.html`, `Topic.html`, `Register.html` with one page per value. These names are reserved: a source file named `vocabulary.md`, `verbs.md`, `chunks.md`, `grammar.md`, `skill.md` (and the others in `logic/theme.py`) is refused.

## German voice

Listen buttons use the voices of your device. Without a German voice the buttons are hidden and the page says so.

- Android: Settings, System, Languages, Text-to-speech output; install German in the speech engine.
- iOS: Settings, Accessibility, Spoken Content, Voices, German.
- Linux: install a German voice for speech-dispatcher, such as `espeak-ng` with its German data, then restart the browser.
- Windows: Settings, Time and language, Speech, Add voices, German.

## Assistant skill

`skill/deutschkurs/` holds instructions for an AI assistant. Each build copies it to `target/skills/deutschkurs/` and adds `reference/site.md`, the list of your entries. For Claude Code, copy that folder to `~/.claude/skills/deutschkurs/`. Other assistants can read `SKILL.md` and the `reference/` files as instructions.
