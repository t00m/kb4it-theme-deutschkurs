# Changelog

All notable changes to the deutschkurs theme. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the theme uses [Semantic Versioning](https://semver.org/). Below 1.0.0, a minor release may change the document format; every such change is listed under "Changed" with what to edit in existing files.

## [Unreleased]

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
