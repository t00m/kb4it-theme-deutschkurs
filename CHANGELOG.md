# Changelog

All notable changes to the deutschkurs theme. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the theme uses [Semantic Versioning](https://semver.org/). Below 1.0.0, a minor release may change the document format; every such change is listed under "Changed" with what to edit in existing files.

## [Unreleased]

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
