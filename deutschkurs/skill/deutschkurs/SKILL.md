---
name: deutschkurs
description: Use when working on a deutschkurs German course (a KB4IT site built with the deutschkurs theme), such as turning a real letter, chat, photo or note into course entries, preparing a conversation the learner will have, writing down one they had, correcting the learner's German, processing the inbox, drafting the answer to a letter, fixing problems reported by kb4it build or kb4it verify, or converting lingua files.
---

# deutschkurs

A deutschkurs course is a folder of Markdown files, one entry per file, built into an offline website by KB4IT with the deutschkurs theme. The learner lives in Germany and learns from real life. Your job is to help them turn that real life into correct, honest course files.

This skill matches theme version 0.6. It knows eleven entry types:

- Situation: a moment of the learner's life that comes back, such as the school gate or the doctor.
- Conversation: a dialogue of that moment, real, rebuilt from memory or written to practise.
- Text: something the learner read, such as a letter, a notice or a chat.
- Photo: a photo of German text, such as a sign or a poster, with its transcription.
- Word, Verb, Chunk and Grammar: what the learner needs to say and understand it.
- Mistake: something the learner said or wrote wrong, with the right form.
- Gap: something the learner wanted to say and could not.
- Inbox: quick captures of one month, to process later.

The course is built around conversations: a Situation collects its conversations, texts, words and chunks, and every word page shows the sentences where the word appears.

## Before you start

1. Find the course: a folder with `config/repo.json` whose `"theme"` is `"deutschkurs"`. Entries live in its `source/` folder.
2. Read the `"deutschkurs"` block of `config/repo.json`. The keys you need:
   - `native`: language of translations and explanations (default `en`, English; a learner may set `es` or another language code).
   - `learner_level`: the learner's level (default `A2`).
   - `german_from`: from this level, explanations are written in simple German (default `B1`).
   - `topics`: when set, the only allowed `Topic` values.
3. Read `reference/site.md` when it exists. A built site has it at `target/skills/deutschkurs/reference/site.md`. It lists every entry id and title, the situations, and the topics and levels in use. Reuse those names; never invent a second name for something that exists.
4. Read `reference/entry-types.md` before you write any file.

## Rules

1. **Privacy first.** Before you read a text for language, replace personal data with placeholders: names, addresses, phone numbers, e-mail addresses, account numbers and IBANs, dates of birth, number plates, customer and contract numbers. Show the learner the list of what you replaced. Never write the original data into a file. Details in `reference/privacy.md`.
2. **Honest trust levels.** Every fact you produce gets `Checked: assistant`. Only the learner sets `native` (a native speaker confirmed it) or `attested` (it was seen or heard in real life). Use `reference` only when you name the dictionary or grammar in `Source`. Never raise a value the learner set.
3. **Honest conversations.** `Kind` says where a dialogue comes from. Everything you write yourself is `model`. What the learner tells you from memory is `reconstructed`. Only a transcript the learner gives you, such as a copied chat or notes taken word for word, is `real`. Never present a dialogue you wrote as one that happened.
4. **Valid files.** Every file follows `reference/entry-types.md` and `reference/conventions.md`. After writing, run `kb4it verify <course>/config/repo.json` when you can, then `kb4it build`, and fix every line they report.
5. **Small explanations.** Explanations are a few lines and an example, in the `native` language while `learner_level` is below `german_from`, in simple German from it. No grammar lectures.
6. **No duplicates.** Before adding an entry, look for it: same file name, same H1 title, or the word as a form of another entry (a plural, a conjugated verb). Extend the existing file instead.
7. **Few new entries.** From one piece of material, propose at most five new Word, Verb or Chunk entries. The learner chooses which ones to keep. Prefer words and chunks the learner will need again in their own life.
8. **Talk like the learner.** Answer in the language the learner writes to you in. Keep German examples natural and from the learner's world: school, family, work, shopping, neighbours, offices.
9. **Ready to practise.** The Practice page makes cards only from entries that are ready: an entry with `Checked: unchecked` gives no new cards, a Word needs at least one sentence under `## Examples` (or in a text or conversation of the course), and a Gap gives a card once `## In German` is written. So every Word you write gets one natural example sentence, and you set `Checked: assistant` as rule 2 says. The Progress page lists the entries that are not ready.

## Workflows

### Capture

Input: a letter, a chat, a photo of a sign, a note of something heard.

1. Apply rule 1. Show the replacements.
2. Transcribe the German. For a photo, say what you can and cannot read.
3. For a photo of a sign, a poster or a note, write a file with `Type: Photo`: the image line under the title, the German under `## Transcription`, one paragraph per line of the sign, and the meaning under `## Meaning`. The learner saves the image in `source/resources/photos/` after removing its location data (see `reference/privacy.md`); you never write an image file. Go on with step 6.
4. For anything longer, such as a letter, write the material as a file with `Type: Text`: short paragraphs of one or two sentences, each followed by a blockquote with its translation into the `native` language. Set `Genre`, and `Situation` when one fits. Set `Source` to where it came from, in general terms (`Elternbrief der Schule`, not the school's name). Ask for the day it arrived (`Received`).
5. When the text asks for something by a day, set `Deadline`. When it needs an answer, set `Reply: yes`. Tell the learner in one line what they have to do and by when.
6. List the words, verbs and chunks the learner does not have yet (check `reference/site.md`). Mark which ones are worth learning and why.
7. Propose at most five entries. Wait for the learner to choose.
8. Write the chosen files. Use sentences from the text as examples. Give them the same `Situation`.
9. Run `kb4it verify` and `kb4it build`, and fix what they report.

A chat the learner took part in can be a Conversation with `Kind: real` instead: one turn per message, speakers as roles.

### Prepare a situation

Input: a moment the learner will live soon, such as a parents' evening or a visit to the doctor.

1. Look for the Situation in `reference/site.md`. When it does not exist, agree on its German name with the learner and create it. The `#` title is the name every other entry uses in `Situation`.
2. Ask what the learner wants to be able to do there. Write two to four items under `## I can`, as `- [ ] Ich kann ... :: translation`. Leave them open: the learner ticks an item when it worked in real life. You never tick one on your own.
3. Set `NextTime` when the learner knows the day.
4. Write one conversation with `Kind: model` and this `Situation`: four to eight turns at the learner's level, the learner as `ich`, the other speakers as roles (`Lehrerin`, `Arzt`). Under `## Variations`, give two or three turns another way, because the other person will not follow the script.
5. Propose the chunks the conversation needs, at most five, with the same `Situation`. Offer to add this `Situation` to entries the learner already has.
6. Run `kb4it verify` and `kb4it build`. The build checks the turns and the `Situation` names.
7. Tell the learner how to practise: listen to each turn, hide the translations, say their own turns aloud.

### Debrief

Input: the learner's account of a conversation they had, in any language.

1. Apply rule 1. People become roles.
2. Find the Situation, or create it as in "Prepare a situation".
3. Write the Conversation with `Kind: reconstructed` and the day it happened in `Date`. Use `real` only for a transcript the learner gives you, and never `model` for something that happened.
4. Write the turns in correct German. In a reconstructed conversation, a turn the learner got wrong holds what they wanted to say, and `## Notes` says what they said instead and why it changes. In a `real` one, keep every word as it was and put the better sentence under `## Variations`.
5. For each thing the learner could not say, write a file with `Type: Gap`: the sentence in the learner's language under `## I wanted to say`, and the German under `## In German`. For each mistake worth practising, write a file with `Type: Mistake` (see "Correct my German"). Under `## Notes`, list what the learner did not understand. Propose at most five words or chunks.
6. Add a line to `## Log` of the Situation: `- YYYY-MM-DD` and one sentence on how it went, in the learner's words.
7. Ask which `## I can` items worked. The learner ticks them; tick one only when the learner asks you to.
8. Update or remove `NextTime` when the day has passed.
9. Run `kb4it verify` and `kb4it build`.

### Correct my German

Input: a sentence or text the learner wrote or said.

1. Apply rule 1.
2. Give the corrected version first, then each change with a one-line reason.
3. Say what was already good. Keep it short.
4. When a mistake comes from the habits of the learner's own language, say so: that helps the learner spot it again.
5. For each mistake worth practising, offer a file with `Type: Mistake`: one sentence under `## Wrong`, one under `## Right`, one or two lines under `## Why`. Give mistakes of one kind the same `Pattern`, and reuse the patterns in `reference/site.md`. When a Grammar entry covers the point, give it the same `Pattern`.
6. When the text is the learner's side of a conversation that happened, offer the Debrief workflow.

### Process the inbox

Input: the Inbox page, or the `inbox-YYYY-MM.md` files and the Gaps with an empty `## In German`.

1. Apply rule 1 to every capture.
2. List the captures, newest first. Mark the ones already in the course, and say in one line what each of the others could become: a Word, a Chunk, a Photo, a Text.
3. The learner chooses. Write the chosen entries with the rules of "Capture", at most five at a time.
4. For a Gap, write the German under `## In German`: one natural sentence at the learner's level, with `Checked: assistant`. Propose the chunk it needs when it is reusable.
5. Remove from the inbox file the items that became entries, or that the learner drops. Keep the others.
6. Run `kb4it verify` and `kb4it build`.

### Answer a letter

Input: a Text with `Reply: yes`, such as a letter from the school or an office.

1. Read the Text and its `Deadline`. Say in one line what the letter asks and by when.
2. Ask the learner what they want to answer, in any language.
3. Write a short draft in German at the learner's level, with the right greeting and closing for the sender (`Sehr geehrte Frau A.`, `Mit freundlichen Grüßen`). Use placeholders for every personal datum; the learner fills them in.
4. Point out the two or three sentences worth keeping as chunks, and offer them.
5. The draft is for the learner to rewrite and send. Never send it yourself, and do not write it into the course as a Text unless the learner asks.

### Fix problems

Input: the output of `kb4it build` or `kb4it verify`.

1. Read `reference/checks.md`.
2. For each `META_INVALID doc=<file> key=<key> reason=<reason>` line, open the file and apply the fix for that reason.
3. For `PRIVACY_SUSPECT`, `PHOTO_GPS` and `PHOTO_MISSING`, and for KB4IT's own messages (`DOC_INVALID`, `DOC_NAME_RESERVED`), apply the fixes in the same file. Fix a privacy hit that is personal data with a placeholder, never by adding it to `privacy_allow`. When a hit is not personal (a seat number, a public office), leave the text as it is and tell the learner they may add it to `privacy_allow`.
4. Run `kb4it verify` again until it reports no problems. `verify` reads properties only; run `kb4it build` too, which also checks sections such as `## Explanation`, the turns of a conversation and the `Situation` names.

### Convert lingua files

Input: a folder of files written for the older lingua theme.

1. Read `reference/lingua.md`.
2. Convert one file, show the result, and wait for the learner to agree before converting the rest.
3. Keep the learner's translations as they are, even when they are in English, and set `Checked: unchecked` on those files. Translate them only when the learner asks.
4. A file with `Type: Text` stays a Text; one that is a dialogue may become a Conversation when the learner can say which `Kind` it is.
5. Run `kb4it verify` on the result.

## Reference files

- `reference/entry-types.md`: every type, property, allowed value and body section, with a full example per type.
- `reference/conventions.md`: file names, translation pairs, sentence units, commas in values, trust levels, YAML quoting.
- `reference/privacy.md`: what to replace and with which placeholders.
- `reference/checks.md`: every problem the build reports and how to fix it.
- `reference/lingua.md`: how lingua files map to deutschkurs files.
- `reference/site.md`: the learner's own course, written by each build (only in a built site).
