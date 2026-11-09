---
name: deutschkurs
description: Use when working on a deutschkurs German course (a KB4IT site built with the deutschkurs theme), such as turning a real letter, chat, photo or note into course entries, correcting the learner's German, fixing problems reported by kb4it build or kb4it verify, or converting lingua files.
---

# deutschkurs

A deutschkurs course is a folder of Markdown files, one entry per file, built into an offline website by KB4IT with the deutschkurs theme. The learner lives in Germany and learns from real life. Your job is to help them turn that real life into correct, honest course files.

This skill matches theme version 0.1.0. It knows four entry types: Word, Verb, Chunk and Grammar. Texts, conversations, situations, photos, mistakes, gaps and the inbox come in later versions. Do not create files of those types yet.

## Before you start

1. Find the course: a folder with `config/repo.json` whose `"theme"` is `"deutschkurs"`. Entries live in its `source/` folder.
2. Read the `"deutschkurs"` block of `config/repo.json`. The keys you need:
   - `native`: language of translations and explanations (default `es`, Spanish).
   - `learner_level`: the learner's level (default `A2`).
   - `german_from`: from this level, explanations are written in simple German (default `B1`).
   - `topics`: when set, the only allowed `Topic` values.
3. Read `reference/site.md` when it exists. A built site has it at `target/skills/deutschkurs/reference/site.md`. It lists every entry id and title, and the topics and levels in use. Reuse those names; never invent a second name for something that exists.
4. Read `reference/entry-types.md` before you write any file.

## Rules

1. **Privacy first.** Before you read a text for language, replace personal data with placeholders: names, addresses, phone numbers, e-mail addresses, account numbers and IBANs, dates of birth, number plates, customer and contract numbers. Show the learner the list of what you replaced. Never write the original data into a file. Details in `reference/privacy.md`.
2. **Honest trust levels.** Every fact you produce gets `Checked: assistant`. Only the learner sets `native` (a native speaker confirmed it) or `attested` (it was seen or heard in real life). Use `reference` only when you name the dictionary or grammar in `Source`. Never raise a value the learner set.
3. **Valid files.** Every file follows `reference/entry-types.md` and `reference/conventions.md`. After writing, run `kb4it verify <course>/config/repo.json` when you can, then `kb4it build`, and fix every line they report.
4. **Small explanations.** Explanations are a few lines and an example, in the `native` language while `learner_level` is below `german_from`, in simple German from it. No grammar lectures.
5. **No duplicates.** Before adding an entry, look for it: same file name, same H1 title, or the word as a form of another entry (a plural, a conjugated verb). Extend the existing file instead.
6. **Few new entries.** From one piece of material, propose at most five new entries. The learner chooses which ones to keep. Prefer words and chunks the learner will need again in their own life.
7. **Talk like the learner.** Answer in the language the learner writes to you in. Keep German examples natural and from the learner's world: school, family, work, shopping, neighbours, offices.

## Workflows

### Capture

Input: a letter, a chat, a photo of a sign, a note of something heard.

1. Apply rule 1. Show the replacements.
2. Transcribe the German. For a photo, say what you can and cannot read.
3. Give a short translation into the `native` language.
4. List the words, verbs and chunks the learner does not have yet (check `reference/site.md`). Mark which ones are worth learning and why.
5. Propose at most five entries. Wait for the learner to choose.
6. Write the chosen files. Use sentences from the material as examples, after anonymisation. Set `Source` to where the material came from, in general terms (`Elternbrief der Schule`, not the school's name).
7. Run `kb4it verify` and fix what it reports.

In this version the material itself is not stored as a file. Say so, and suggest the learner keeps the original in a private place.

### Correct my German

Input: a sentence or text the learner wrote or said.

1. Apply rule 1.
2. Give the corrected version first, then each change with a one-line reason.
3. Say what was already good. Keep it short.
4. When a mistake comes from Spanish or English habits, say so: that helps the learner spot it again.
5. Offer to add a chunk or a word entry for the correct form when it is reusable. A Mistake entry type comes in a later version; until then, put the wrong and right form under `## Typical mistakes` of the Verb or Grammar entry it belongs to, as `wrong :: right`.

### Fix problems

Input: the output of `kb4it build` or `kb4it verify`.

1. Read `reference/checks.md`.
2. For each `META_INVALID doc=<file> key=<key> reason=<reason>` line, open the file and apply the fix for that reason.
3. For KB4IT's own messages (`DOC_INVALID`, `DOC_NAME_RESERVED`), apply the fixes in the same file.
4. Run `kb4it verify` again until it reports no problems. `verify` reads properties only; run `kb4it build` too, which also checks sections such as `## Explanation`.

### Convert lingua files

Input: a folder of files written for the older lingua theme.

1. Read `reference/lingua.md`.
2. Convert one file, show the result, and wait for the learner to agree before converting the rest.
3. Keep the learner's translations as they are, even when they are in English, and set `Checked: unchecked` on those files. Translate them only when the learner asks.
4. Files with `Type: Text` cannot be converted yet; list them and leave them untouched.
5. Run `kb4it verify` on the result.

## Reference files

- `reference/entry-types.md`: every type, property, allowed value and body section, with a full example per type.
- `reference/conventions.md`: file names, translation pairs, commas in values, trust levels, YAML quoting.
- `reference/privacy.md`: what to replace and with which placeholders.
- `reference/checks.md`: every problem the build reports and how to fix it.
- `reference/lingua.md`: how lingua files map to deutschkurs files.
- `reference/site.md`: the learner's own course, written by each build (only in a built site).
