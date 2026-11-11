# deutschkurs theme

A KB4IT theme that turns your own Markdown files into an offline German course built around real life. Version 0.3.2, for KB4IT 0.12.x.

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
| Photo | A photo of German text, such as a sign | none; an image under the title, optional `Place`, sections `## Transcription` and `## Meaning` |
| Mistake | Something you said or wrote wrong | `Level`, sections `## Wrong` and `## Right`; optional `Pattern`, `## Why` |
| Gap | Something you wanted to say and could not | none; sections `## I wanted to say` and `## In German` (empty until processed) |
| Inbox | Quick captures of one month, in `inbox-YYYY-MM.md` | none; one list item per capture, starting with its day |

Translation pairs are list items: `- German sentence :: translation`. A Conversation turn is `- **Speaker:** German :: translation`. In a Text, a blockquote right after a paragraph is its translation.

Common optional properties: `Checked` (`unchecked`, `assistant`, `reference`, `native`, `attested`), `Topic`, `Situation`, `Source`, `Date`, `Tag`. `Situation` is the `#` title of a Situation entry; the entry is then listed on that situation's page. A value that names no Situation gives `situation_unknown` during the build.

Word, verb and chunk pages show "Where it appears": up to 10 sentences from your texts, photos and conversations that use the entry, each linked to its sentence. A Grammar page with `Marker` values lists sentences that contain those markers, the same way. Text and Conversation pages show coverage: how many of their words your course already knows.

Images live in `source/resources/photos/`, without location data and without people. A Mistake shows the Grammar entries that have the same `Pattern`. Facts with `Checked: unchecked` or `assistant` get a dotted underline.

KB4IT splits property values on commas, so sentences and explanations go in the body. A noun without plural has `Plural: none`.

## Settings

In `config/repo.json`, block `"deutschkurs"`:

| Key | Default | Meaning |
|---|---|---|
| `native` | `en` | Language of translations, such as `en` or `es` |
| `labels` | `{}` | Overrides of single interface strings |
| `learner_level` | `A2` | Your level |
| `german_from` | `B1` | From this level, grammar pages show the simple German version first |
| `strict` | `false` | Metadata problems and privacy hits stop the build |
| `speech` | `true` | Listen buttons |
| `speech_lang` | `de-DE` | Preferred voice language |
| `voice` | none | Name of a preferred voice |
| `accent` | `#c0392b` | Accent colour |
| `gender_colors` | `{"m": "#1f6feb", "f": "#cf222e", "n": "#1a7f37", "pl": "#d4760a"}` | Colours of der, die, das and plural |
| `topics` | none | When set, the only allowed `Topic` values |
| `prepare_days` | `7` | Days before a situation's `NextTime` that the home page and the situation page show it as coming up |
| `known_words` | `[]` | Words you know without an entry; coverage counts them as known |
| `privacy_allow` | `[]` | Exact texts the privacy check accepts, such as the public address of an office |

`daily_reviews` (40), `daily_new` (5) and `weekly_new` (10) set the size of practice sessions. `voice_me` is the voice of your own turns in roleplay. `slow_rate` is accepted and not used yet.

## Pages

The pages use UIkit, the same library as the techdoc theme. KB4IT ships it and each build copies it to `target/resources/vendor/uikit/`, so the site needs no Internet connection. The top bar has Home, two menus (Real life and Course) and the Assistant skill; on a phone the links are in a side menu. The search icon, `/` or Ctrl+K open the search box. The labels `menu_life`, `menu_course` and `menu` rename the menus.

Home, Situations, Conversations, Texts, Photos, Mistakes, Inbox, Vocabulary, Verbs, Chunks, Grammar, Assistant skill, search, and facet pages `Level.html`, `Topic.html`, `Register.html`, `ConversationKind.html`, `Genre.html`, `Place.html`, `Pattern.html` with one page per value. Photos is a gallery with filters by place and situation. Mistakes groups mistakes by `Pattern`, newest first. Inbox lists the captures of every inbox file and the gaps to process; it is the only page that shows inbox files, which search leaves out. The home page lists situations coming up, texts with an open deadline and the number of captures to process. Dated blocks are hidden by JavaScript when they are out of range, so a site built last week is still right today.

These names are reserved: a source file named `vocabulary.md`, `verbs.md`, `chunks.md`, `grammar.md`, `texts.md`, `conversations.md`, `situations.md`, `skill.md`, `Level.md`, `Topic.md`, `Register.md`, `Genre.md`, `Place.md`, `Pattern.md` (and the others in `logic/theme.py`) is refused. A file whose name starts with a facet name and `_`, such as `Level_` or `Genre_`, gets a `PAGE_NAME_TAKEN` warning. Your own `index.md` replaces the home page.

Article pages: `Article.html` and one page per article, `Article_der.html`, `Article_die.html` and `Article_das.html`, list every noun said with that article. The `die` page shows feminine nouns first, then plural-only nouns. The word cards, the vocabulary table and the Course menu link to them.

## Practice

Each build writes `deutschkurs-data.js`, the data the browser needs to practise. The home page shows how many cards are due and new today. `practice.html` has four sessions: Daily (due cards, the conversation of the day and a few new cards), Short (up to 15 due cards), Weekly (due cards, a conversation and the mistakes you repeat most) and Free (any card, by level, situation, topic or type). A situation page has a Prepare button that opens Free practice for that situation.

Exercises: der, die or das; plural; German to your language; your language to German; Perfekt; separable verbs in a sentence; fill the gap; roleplay of your turns in a conversation; fix a mistake; say a gap in German. Typed answers accept `ae oe ue ss` for `ä ö ü ß`, ignore a capital first letter, extra spaces and final punctuation, and need the exact article. A small typo rates as hard. Speaking exercises have no speech recognition: say the line aloud or type it, then show the answer and rate yourself.

Only entries that are ready give new cards: not `Checked: unchecked`, and for a Word at least one example sentence. `progress.html` lists the others, the words you understand and can say per level, what you can do per situation, your real-life wins from `## Log`, mistake patterns and the days you studied.

Progress lives in the browser (`localStorage`), per course title. Export it as `deutschkurs-progress-YYYY-MM-DD.json` and import it on another device; per card the newer state wins. A private window does not keep progress, and the page says so.

## Privacy

Each build reads every source file and warns with `PRIVACY_SUSPECT doc=<file> reason=<reason> line=<n>` when a line looks like an IBAN, an e-mail address, a phone number or an address. Images under `source/resources/photos/` with GPS data give `PHOTO_GPS`; an image that cannot be opened gives `PHOTO_UNREADABLE`. A Photo whose image is missing or is a web address gives `PHOTO_MISSING`. These checks catch the obvious cases; they do not find names. With `strict`, privacy hits and photos with GPS data stop the build. An entry of `privacy_allow` drops every hit inside that text, so one entry covers a whole address.

## German voice

Listen buttons use the voices of your device. Without a German voice the buttons are hidden and the page says so.

- Android: Settings, System, Languages, Text-to-speech output; install German in the speech engine.
- iOS: Settings, Accessibility, Spoken Content, Voices, German.
- Linux: install a German voice for speech-dispatcher, such as `espeak-ng` with its German data, then restart the browser.
- Windows: Settings, Time and language, Speech, Add voices, German.

## Assistant skill

`skill/deutschkurs/` holds instructions for an AI assistant. Each build copies it to `target/skills/deutschkurs/` and adds `reference/site.md`, the list of your entries. For Claude Code, copy that folder to `~/.claude/skills/deutschkurs/`. Other assistants can read `SKILL.md` and the `reference/` files as instructions.
