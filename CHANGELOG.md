# Changelog

All notable changes to the deutschkurs theme. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the theme uses [Semantic Versioning](https://semver.org/). Below 1.0.0, a minor release may change the document format; every such change is listed under "Changed" with what to edit in existing files.

## [Unreleased]

## [0.6.1] - 2026-11-11

### Added

- A paragraph of a Text can end with `[audio](resources/audio/x.m4a)`, like a turn.
- `AUDIO_MISSING reason=type` when `Audio` or an audio link names a file that is no recording.
- When the course title changed, the Practice page finds the progress saved under the old title and offers to use it.

### Fixed

- Import and stored progress drop broken card states, which could keep a card from ever coming due.
- The Practice page says when the browser storage fills up during a session.
- The import message says why cards were skipped.
- Speech: `1.2.3` is no longer read as a date; `12.30 Uhr` and street names such as `Hauptstr.` are read out; an abbreviation at the end of a sentence keeps its full stop.
- Listen, Play all and the page players stop each other instead of sounding together.
- The verb bracket takes the nearest auxiliary: in *Wir haben Zeit und haben gekocht* the second *haben*.
- In *Er hat ein Auto gehabt*, *hat* keeps its fill-the-gap card for *haben*.
- A web address written in capitals (`HTTPS://`) is reported `remote`, for photos and recordings.

## [0.6.0] - 2026-11-11

### Added

- Entry pages: View source shows the Markdown in a dialog; Edit in the editor opens it in `add.html`; Edit on the git server links the file when `repo.json` sets `git`, `git_server`, `git_user`, `git_repo` and `git_branch`.
- Part of speech facet: `PartOfSpeech.html` and one page per value.
- The Level and Part of speech cells of the vocabulary table, and the Level cells of the verb and chunk tables, link their facet pages.
- Filters: Situations by topic; Conversations by topic, level and kind. A situation group with no matching conversation is hidden.

### Changed

- The top bar and the phone menu have no Home link; the logo opens the home page.
- Mistakes and Inbox left the Real life menu. The pages stay: the home page links Mistakes and shows the Inbox alert.
- `PartOfSpeech.md` is now a reserved source file name, and names starting with `PartOfSpeech_` get `PAGE_NAME_TAKEN`. Rename such a file if your course has one.

## [0.5.0] - 2026-11-11

### Added

- Slow button next to every Listen button, at `slow_rate` (default 0.75). A `slow_rate` that is not above 0 and at most 2 logs `SETTING_INVALID key=slow_rate` and uses 0.75.
- Play all on conversations and texts: every turn or sentence in order.
- Two voices on pages: Listen buttons of your own turns use `voice_me`.
- Recordings: the property `Audio` on Word, Verb and Chunk, and `[audio](resources/audio/x.m4a)` at the end of a turn. The page shows a player and the badge `real`; roleplay plays the recording. `AUDIO_MISSING doc=<file> reason=missing|remote` when the file does not exist or is a web address.
- Speech normalisation before speaking: times (`8:30 Uhr`), prices (`5,50 €`, `5 EUR`, `€ 5`), dates (`3.11.`, `3.11.2026`, `3. November`) and the abbreviations `z. B.`, `d. h.`, `usw.`, `bzw.`, `ca.`, `Nr.`, `Str.`, `Tel.`.
- Verb bracket for haben or sein with the participle of a verb in the course, in the same clause; the auxiliary must match the verb's `Auxiliary`.
- The gender cue `m`, `f`, `n`, `pl` on word cards, article badges, the vocabulary and article tables and the article buttons of practice; plural forms in the plural colour.
- Skill: `Audio` and recorded turns in `entry-types.md`, `AUDIO_MISSING` in `checks.md`, a Recordings section in `privacy.md`.

### Fixed

- Roleplay speaks every turn of the other speaker when there are two or more in a row; before, only the last one was heard.

## [0.4.0] - 2026-11-11

### Added

- Article pages: `Article.html` and `Article_der.html`, `Article_die.html`, `Article_das.html` list every noun said with that article. The `die` page has feminine nouns first, then plural-only nouns. Word cards, the vocabulary table and the Course menu link to them.
- Practice in the browser. Each build writes `deutschkurs-data.js`; `practice.html` has the sessions Daily, Short, Weekly and Free, with ten exercises: der/die/das, plural, German to your language, your language to German, Perfekt, separable verbs, fill the gap, roleplay, fix a mistake and say a gap in German.
- Typing rules: `ae oe ue ss` count as `ä ö ü ß`; a capital first letter, extra spaces and final punctuation are ignored; the article must be exact; a lowercase noun or a small typo rates as hard; a wrong answer shows which letters differ.
- A simplified SM-2 scheduler; mistakes stay at one day until three good answers in a row.
- Progress in `localStorage`, per course title, with export to `deutschkurs-progress-YYYY-MM-DD.json` and import that keeps the newer state of each card.
- `progress.html`: words you understand and can say per level, can-do per situation, real-life wins from `## Log`, mistake patterns, study days and the entries not ready to practise.
- The home page shows the cards due and new today. Situation pages have a Prepare button that opens Free practice for that situation.
- The settings `daily_reviews`, `daily_new`, `weekly_new` and `voice_me` are now used.
- Starter course: a processed gap, so every exercise has a card.
- Skill rule "Ready to practise".

### Changed

- `Article.md` is now a reserved source file name, and names starting with `Article_` get `PAGE_NAME_TAKEN`. Rename such a file if your course has one.
- The Course menu has Articles (after Vocabulary) and Progress (at the end).
- Only entries that are ready give practice cards: not `Checked: unchecked`, and a Word needs one example sentence.

## [0.3.2] - 2026-11-11

### Changed

- The pages use UIkit, as the techdoc theme does. KB4IT ships the library and the build copies it into the site, so the course still works offline. Your source files need no change.
- The top bar is a UIkit navbar: Home, the menus "Real life" (situations, conversations, texts, photos, mistakes, inbox) and "Course" (vocabulary, verbs, chunks, grammar), and the Assistant skill. On a phone the links open in a side menu.
- Search opens in a dialog from the search icon, `/` or Ctrl+K.
- Page content, entry cards, home tiles, situations and photos are UIkit cards; lists, tables, filters, buttons and banners use UIkit components. The Add page shows one UIkit card per entry type.
- New labels `menu_life`, `menu_course` and `menu`.

## [0.3.1] - 2026-11-11

### Fixed

- An image written `![...](<resources/photos/mein foto.webp>)`, with spaces inside `<...>`, is found; before, the Photo got `PHOTO_MISSING reason=none` and was left out of the gallery.
- An image path written with backslashes (`resources\photos\a.jpg`) is found.
- A web image in an inbox capture is no longer loaded by the Inbox page, and the build reports `PHOTO_MISSING reason=remote` for that inbox file.
- A five-digit number before a counted noun (`50000 Einwohner`, `10000 Dollar`, `30000 Kilometern`, `12345 Personen`) is no longer reported as an address.
- An image under `resources/photos/` that cannot be opened gives `PHOTO_UNREADABLE` instead of being skipped without a word.
- An inbox capture with an impossible date (`2026-13-45`) shows that date on the Inbox page, so the typo can be seen and fixed.
- The privacy reference says that customer and file numbers starting with `0` can be reported as phone numbers; that warning stays, because such numbers are often personal.

## [0.3.0] - 2026-11-11

### Added

- Entry types Photo, Mistake, Gap and Inbox. A Photo has an image under `source/resources/photos/`, a `## Transcription` and a `## Meaning`. A Mistake has `## Wrong`, `## Right` and `## Why`, grouped by `Pattern`. A Gap holds what you wanted to say and, once processed, the German. An Inbox file `inbox-YYYY-MM.md` collects quick captures of one month.
- Problems `place_invalid` and `mistake_incomplete`.
- Privacy check on every build: `PRIVACY_SUSPECT` for text that looks like an IBAN, an e-mail address, a phone number or an address; `PHOTO_GPS` for images with location data; `PHOTO_MISSING` for a Photo whose image is missing or is a web address. The setting `privacy_allow` is now used; with `strict`, privacy hits stop the build.
- Pages Photos (a gallery with filters by place and situation), Mistakes (by pattern, newest first) and Inbox (captures and gaps to process, newest first; captures whose first word is in the course are marked). The home page shows how many captures wait.
- Facet pages by `Place` and `Pattern`, and three new links in the top bar.
- Photo transcriptions show in "Where it appears" on word pages, after texts and before conversations.
- A Mistake page links the Grammar entries with the same `Pattern`.
- Facts with `Checked: unchecked` or `assistant` get a dotted underline on their page and in lists.
- Starter course: a photo of a building site sign (drawn by `scripts/make_starter_photo.py`), a mistake, a gap and an inbox file. Add page skeletons for the four new types.
- Skill: workflows "Process the inbox" and "Answer a letter"; Capture writes a Photo, Debrief writes Gaps and Mistakes, Correct my German writes Mistakes; the privacy reference explains the new checks; the site appendix lists photos, mistakes, gaps and patterns.

### Changed

- `Place.md` and `Pattern.md` are now reserved source file names, and names starting with `Place_` or `Pattern_` get `PAGE_NAME_TAKEN`. Rename such a file if your course has one.
- A Gap needs no `Level`; Photo and Inbox need none either.
- A Grammar `Pattern` now links the grammar point to the mistakes with that pattern.

## [0.2.0] - 2026-11-10

### Added

- Entry types Text, Conversation and Situation. A Conversation is a list of turns `**Speaker:** German :: translation` with a `Kind` badge (`real`, `reconstructed`, `model`). A Text is German paragraphs with folded blockquote translations. A Situation has a `## I can` task list and a `## Log`, and lists every entry whose `Situation` names it.
- Common property `Situation`. A value that names no Situation gives `situation_unknown` during the build.
- "Where it appears" on word, verb and chunk pages: up to 10 sentences from texts and conversations, each linked to its sentence anchor (`#t3`, `#s2`).
- Coverage on text and conversation pages: the share of words the course already knows. The new setting `known_words` adds words without an entry.
- Grammar property `Marker`: the page lists sentences that contain one of the markers.
- Deadline banner on texts and a "coming up" block for situations. The new setting `prepare_days` (default 7) sets how many days before `NextTime` a situation shows as coming up. Dated blocks are hidden by JavaScript when out of range.
- Pages Situations, Conversations and Texts, facet pages by `Kind` (`ConversationKind.html`) and `Genre`, and three new links in the top bar.
- Starter course: situations "Am Schultor", "Elternbrief" and "Elternabend", the conversation "Gruß am Schultor" and the text "Elternbrief zum Ausflug".
- Add page skeletons for the three new types.
- Skill: the rule "honest conversations", workflows "Prepare a situation" and "Debrief", Capture writes a Text, lingua texts convert to Text files, and the site appendix lists situations, conversations and texts.

### Changed

- `texts.md`, `conversations.md`, `situations.md`, `Genre.md` and `ConversationKind.md` are now reserved source file names. Rename such a file if your course has one.

## [0.1.1] - 2026-11-09

### Changed

- Translations default to English: `native` is now `en`. A course with Spanish translations sets `"native": "es"` in the `deutschkurs` block of `repo.json`.
- The starter course and the skill examples are in English.
- The top bar is one compact row, as in the techdoc theme: logo, links and a small search box. On phones the links scroll sideways.
- `PluralOnly`, `Irregular`, `Separable` and `Reflexive` accept only `yes`; other values give `flag_invalid`. Impossible dates such as `2026-13-45` give `date_invalid`.

### Fixed

- Glossary linking: attributes containing `>`, closing tags without an opening tag, and separable verbs that share a stem (`anrufen`, `zurückrufen`).
- Invalid colours in `accent` or `gender_colors` are replaced by the default with a `COLOR_INVALID` warning.
- The 404 page, footer, skill page and facet headings take their text from the labels, so `labels` overrides reach them.
- CI uses the Node 24 versions of the GitHub actions.

## [0.1.0] - 2026-11-09

### Added

- Theme for KB4IT 0.12.x on the `BaseTheme` API, with the built-in features search, 404 page and Add page.
- Entry types Word, Verb, Chunk and Grammar, with their properties, body sections and a card on each entry page.
- Glossary linking in every page: nouns with their gender colour, plurals, verb forms, split separable verbs and chunks.
- Example lines `German :: translation` with a Listen button; typical mistakes shown as wrong and right form.
- Listen buttons with the browser's German voice, hidden with a note when the device has none.
- Pages: home, vocabulary, verbs, chunks, grammar, and facet pages by Level, Topic and Register, with table filters.
- Grammar pages show the explanation or the simple German version first, by the learner's level.
- Metadata checks during the build and in `kb4it verify`, with a `strict` setting.
- Assistant skill v1 (`skill/deutschkurs/`): privacy first, honest trust levels, workflows to capture material, correct German, fix problems and convert lingua files; published in the site with a list of the learner's entries.
- Add page skeletons for the four types.
- Starter course: 10 words, 5 verbs, 4 chunks and 2 grammar points from school and family life, in Spanish.
