# deutschkurs theme

A KB4IT theme that turns your own Markdown files into an offline German course built around real life. Version 0.2.0, for KB4IT 0.12.x.

## Entries

One file per entry in `source/`, with YAML frontmatter, one `#` title and optional `##` sections. The full reference, with an example per type, is in `skill/deutschkurs/reference/entry-types.md`.

| Type | What | Required properties |
|---|---|---|
| Word | A noun, adjective or other word | `Level`, `Translation`, `PartOfSpeech`; `Article` for nouns |
| Verb | A verb | `Level`, `Translation`, `Participle`, `Auxiliary`; `Prefix` when `Separable: yes` |
| Chunk | A fixed phrase | `Level`, `Translation` |
| Grammar | One grammar point | `Level`, `Area`, and a `## Explanation` section |
| Text | Something you read: a letter, a notice, a chat | `Level`; optional `Genre`, `Received`, `Deadline`, `Reply` |
| Conversation | A dialogue from your life, one list item per turn | `Level`, `Kind` (`real`, `reconstructed`, `model`); optional `Me`, `Register` |
| Situation | A moment that comes back, such as the parents' evening | none; optional `NextTime`, sections `## I can` and `## Log` |

Translation pairs are list items: `- German sentence :: translation`. A Conversation turn is `- **Speaker:** German :: translation`. In a Text, a blockquote right after a paragraph is its translation.

Common optional properties: `Checked` (`unchecked`, `assistant`, `reference`, `native`, `attested`), `Topic`, `Situation`, `Source`, `Date`, `Tag`. `Situation` is the `#` title of a Situation entry; the entry is then listed on that situation's page. A value that names no Situation gives `situation_unknown` during the build.

Word, verb and chunk pages show "Where it appears": up to 10 sentences from your texts and conversations that use the entry, each linked to its sentence. A Grammar page with `Marker` values lists sentences that contain those markers, the same way. Text and Conversation pages show coverage: how many of their words your course already knows.

KB4IT splits property values on commas, so sentences and explanations go in the body. A noun without plural has `Plural: none`.

## Settings

In `config/repo.json`, block `"deutschkurs"`:

| Key | Default | Meaning |
|---|---|---|
| `native` | `en` | Language of translations, such as `en` or `es` |
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
| `prepare_days` | `7` | Days before a situation's `NextTime` that the home page and the situation page show it as coming up |
| `known_words` | `[]` | Words you know without an entry; coverage counts them as known |

Settings for later versions (`voice_me`, `slow_rate`, `daily_reviews`, `daily_new`, `weekly_new`, `privacy_allow`) are accepted and not used yet.

## Pages

Home, Situations, Conversations, Texts, Vocabulary, Verbs, Chunks, Grammar, Assistant skill, search, and facet pages `Level.html`, `Topic.html`, `Register.html`, `ConversationKind.html`, `Genre.html` with one page per value. The home page lists situations coming up and texts with an open deadline. Dated blocks are hidden by JavaScript when they are out of range, so a site built last week is still right today.

These names are reserved: a source file named `vocabulary.md`, `verbs.md`, `chunks.md`, `grammar.md`, `texts.md`, `conversations.md`, `situations.md`, `skill.md`, `Level.md`, `Topic.md`, `Register.md`, `Genre.md` (and the others in `logic/theme.py`) is refused. A file whose name starts with a facet name and `_`, such as `Level_` or `Genre_`, gets a `PAGE_NAME_TAKEN` warning. Your own `index.md` replaces the home page.

## German voice

Listen buttons use the voices of your device. Without a German voice the buttons are hidden and the page says so.

- Android: Settings, System, Languages, Text-to-speech output; install German in the speech engine.
- iOS: Settings, Accessibility, Spoken Content, Voices, German.
- Linux: install a German voice for speech-dispatcher, such as `espeak-ng` with its German data, then restart the browser.
- Windows: Settings, Time and language, Speech, Add voices, German.

## Assistant skill

`skill/deutschkurs/` holds instructions for an AI assistant. Each build copies it to `target/skills/deutschkurs/` and adds `reference/site.md`, the list of your entries. For Claude Code, copy that folder to `~/.claude/skills/deutschkurs/`. Other assistants can read `SKILL.md` and the `reference/` files as instructions.
