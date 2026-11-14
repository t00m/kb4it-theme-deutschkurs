# deutschkurs theme

A KB4IT theme that turns your own Markdown files into an offline German course built around real life. Version 0.7.0, for KB4IT 0.12.x.

## Entries

One file per entry in `source/`, with YAML frontmatter, one `#` title and optional `##` sections. The full reference, with an example per type, is in `skill/deutschkurs/reference/entry-types.md`.

| Type | What | Required properties |
|---|---|---|
| Word | A noun, article, adjective, adverb, pronoun, preposition, conjunction, numeral, interjection or particle | `Level`, `Translation`, `PartOfSpeech`; `Article` for nouns |
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
| `voice_me` | none | Voice of your own turns in conversations and roleplay |
| `slow_rate` | `0.75` | Speed of the Slow button; a number above 0 and at most 2 |
| `accent` | `#c0392b` | Accent colour |
| `gender_colors` | `{"m": "#1f6feb", "f": "#cf222e", "n": "#1a7f37", "pl": "#d4760a"}` | Colours of der, die, das and plural |
| `topics` | none | When set, the only allowed `Topic` values |
| `prepare_days` | `7` | Days before a situation's `NextTime` that the home page and the situation page show it as coming up |
| `known_words` | `[]` | Words you know without an entry; coverage counts them as known |
| `privacy_allow` | `[]` | Exact texts the privacy check accepts, such as the public address of an office |

`daily_reviews` (40), `daily_new` (5) and `weekly_new` (10) set the size of practice sessions.

## Pages

The pages use UIkit, the same library as the techdoc theme. KB4IT ships it and each build copies it to `target/resources/vendor/uikit/`, so the site needs no Internet connection. The top bar has the logo (it opens the home page), two menus (Real life: Situations, Conversations, Texts, Photos; Course) and the Assistant skill; on a phone the links are in a side menu. The search icon, `/` or Ctrl+K open the search box. The labels `menu_life`, `menu_course` and `menu` rename the menus.

Home, Situations, Conversations, Texts, Photos, Mistakes, Inbox, Vocabulary, Verbs, Chunks, Grammar, Assistant skill, search, and facet pages `Level.html`, `Topic.html`, `Register.html`, `ConversationKind.html`, `Genre.html`, `Place.html`, `Pattern.html`, `PartOfSpeech.html` with one page per value. The Level and Part of speech cells of the vocabulary, verb and chunk tables link these pages. Situations can be filtered by topic, Conversations by topic, level and kind. Photos is a gallery with filters by place and situation. Mistakes groups mistakes by `Pattern`, newest first; the home page links it. Inbox lists the captures of every inbox file and the gaps to process; it is the only page that shows inbox files, which search leaves out. The home page lists situations coming up, texts with an open deadline and the number of captures to process. Every entry page has View source (the Markdown in a dialog), Edit in the editor (when the editor is on) and Edit on the git server (when `repo.json` sets the git keys). Dated blocks are hidden by JavaScript when they are out of range, so a site built last week is still right today.

These names are reserved: a source file named `vocabulary.md`, `verbs.md`, `chunks.md`, `grammar.md`, `texts.md`, `conversations.md`, `situations.md`, `skill.md`, `Level.md`, `Topic.md`, `Register.md`, `Genre.md`, `Place.md`, `Pattern.md`, `PartOfSpeech.md` (and the others in `logic/theme.py`) is refused. A file whose name starts with a facet name and `_`, such as `Level_` or `Genre_`, gets a `PAGE_NAME_TAKEN` warning. Your own `index.md` replaces the home page.

Article pages: `Article.html` and one page per article, `Article_der.html`, `Article_die.html` and `Article_das.html`, list every noun said with that article. The `die` page shows feminine nouns first, then plural-only nouns. The word cards, the vocabulary table and the Course menu link to them.

Part of speech pages: `PartOfSpeech.html` counts the words of each part of speech, and one page per value, such as `PartOfSpeech_preposition.html`, lists them. The Course menu, the vocabulary table and the "Part of speech" line of every word page link to them.

## Practice

Each build writes `deutschkurs-data.js`, the data the browser needs to practise. The home page shows how many cards are due and new today. `practice.html` has four sessions: Daily (due cards, the conversation of the day and a few new cards), Short (up to 15 due cards), Weekly (due cards, a conversation and the mistakes you repeat most) and Free (any card, by level, situation, topic or type). A situation page has a Prepare button that opens Free practice for that situation.

Exercises: der, die or das; plural; the case of a preposition; where the verb goes after a conjunction; comparison (*gut, besser, am besten*); the Akkusativ or Dativ of a pronoun; German to your language; your language to German; Perfekt; separable verbs in a sentence; fill the gap; roleplay of your turns in a conversation; fix a mistake; say a gap in German. Typed answers accept `ae oe ue ss` for `ä ö ü ß`, ignore a capital first letter, extra spaces and final punctuation, and need the exact article. A small typo rates as hard. Speaking exercises have no speech recognition: say the line aloud or type it, then show the answer and rate yourself.

Only entries that are ready give new cards: not `Checked: unchecked`, and for a Word at least one example sentence. `progress.html` lists the others, the words you understand and can say per level, what you can do per situation, your real-life wins from `## Log`, mistake patterns and the days you studied.

Progress lives in the browser (`localStorage`), per course title. Export it as `deutschkurs-progress-YYYY-MM-DD.json` and import it on another device; per card the newer state wins. An import skips cards of entries this course does not have and broken card data, and says how many. A private window does not keep progress, and the page says so; when the storage fills up during a session, the page says that too. If you rename the course, the Practice page finds the progress saved under the old title and offers to use it.

## Privacy

Each build reads every source file and warns with `PRIVACY_SUSPECT doc=<file> reason=<reason> line=<n>` when a line looks like an IBAN, an e-mail address, a phone number or an address. Images under `source/resources/photos/` with GPS data give `PHOTO_GPS`; an image that cannot be opened gives `PHOTO_UNREADABLE`. A Photo whose image is missing or is a web address gives `PHOTO_MISSING`, and a recording that is missing or a web address gives `AUDIO_MISSING`. These checks catch the obvious cases; they do not find names. With `strict`, privacy hits and photos with GPS data stop the build. An entry of `privacy_allow` drops every hit inside that text, so one entry covers a whole address.

## Seeing and hearing

Nouns have the colour of their gender, and a small `m`, `f`, `n` or `pl` after them for readers who do not see colours: in linked text, on word cards, in the vocabulary and article tables and in practice. Plural forms have the plural colour.

A verb in two parts is underlined twice in both parts: a split separable verb (*Ich **rufe** dich morgen **an***) and haben or sein with the participle of a verb in the course (*Ich **habe** dich gestern **angerufen***). The auxiliary must be the one the verb's `Auxiliary` names.

Every Listen button has a Slow button next to it (`slow_rate`). Conversations and texts have a Play all button that reads every turn or sentence in order; your own turns use `voice_me` when it is set. Before speaking, times, prices, dates and a few abbreviations are written out: `8:30 Uhr` is read as *acht Uhr dreißig*, `5,50 €` as *fünf Euro fünfzig*, `am 3.11.` as *am dritten November*, `z. B.` as *zum Beispiel*.

### Recordings

A real recording replaces the device voice. Put the file under `source/resources/audio/` (`.m4a`, `.mp3`, `.ogg`, `.oga`, `.opus`, `.wav` or `.webm`) and point to it:

- Word, Verb or Chunk: the property `Audio: resources/audio/termin.m4a`.
- A turn of a conversation: a link at the end, `- **Lehrerin:** Guten Morgen! :: Good morning! [audio](resources/audio/guten-morgen.m4a)`.
- A paragraph of a text: the same link at the end of the paragraph.

The path may end with a query or a fragment: `resources/audio/dialog.m4a#t=12` starts the recording at second 12, so one long recording can serve several turns.

The page shows a player and the badge `real`; Play all and roleplay play the recording. A file that does not exist, a web address or an `Audio` file that is no recording gives `AUDIO_MISSING`; a web address is never loaded. Listen buttons and page players stop each other, so two sounds never overlap. Record only your own voice or a person who agreed to it.

### German voice

Listen buttons use the voices of your device. Without a German voice the Listen, Slow and Play all buttons are hidden and the page says so; recordings still play.

- Android: Settings, System, Languages, Text-to-speech output; install German in the speech engine.
- iOS: Settings, Accessibility, Spoken Content, Voices, German.
- Linux: install a German voice for speech-dispatcher, such as `espeak-ng` with its German data, then restart the browser.
- Windows: Settings, Time and language, Speech, Add voices, German.

## Assistant skill

`skill/deutschkurs/` holds instructions for an AI assistant. Each build copies it to `target/skills/deutschkurs/` and adds `reference/site.md`, the list of your entries. For Claude Code, copy that folder to `~/.claude/skills/deutschkurs/`. Other assistants can read `SKILL.md` and the `reference/` files as instructions.
