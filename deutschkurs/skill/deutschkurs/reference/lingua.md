# Converting lingua files

lingua was an earlier KB4IT theme for language courses. Its files are close to deutschkurs files, but not the same. Convert them one by one, show the first result, and wait for the learner's agreement.

## Properties

| lingua | deutschkurs |
|---|---|
| `Type: Word`, `Verb`, `Grammar` | Same |
| `Type: Text` | Same; see "Texts" below |
| `PartOfSpeech: Noun`, `Adjective`... (capitalised) | Lower case: `noun`, `adjective`... |
| `PartOfSpeech: Expression` | `Type: Chunk`, remove `PartOfSpeech` |
| `Plural: Häuser` (without article) | `Plural: die Häuser` |
| `Plural: -` | `Plural: none` |
| `PluralOnly: yes` with `Article: die` | Keep `PluralOnly: yes`; `Article` may stay |
| `Preterite: rief` (without pronoun) | `Preterite: ich rief an` (with pronoun, and prefix for separable verbs) |
| `Translation` in English | Keep it; add `Checked: unchecked` |
| Everything else (`Level`, `Topic`, `Date`, `Forms`, `Auxiliary`, `Participle`, `Separable`, `Prefix`, `Government`, `Case`, `Area`) | Same |

## Body

| lingua | deutschkurs |
|---|---|
| `## Examples` with `German :: translation` | Same |
| Free text right after the title (Word, Verb) | Move it under `## Notes` |
| Grammar: free text and tables after the title | Move them under `## Explanation` |
| Grammar: `## Examples` | Keep it after `## Explanation`; its `German :: translation` items get Listen buttons |

## Example

lingua:

```text
---
Type: Word
Article: das
Plural: Häuser
PartOfSpeech: Noun
Level: A1
Translation: house
---

# Haus
```

deutschkurs:

```markdown
---
Article: das
Checked: unchecked
Level: A1
PartOfSpeech: noun
Plural: die Häuser
Translation: house
Type: Word
---

# Haus
```

## Texts

A lingua Text has the same body: short paragraphs, each followed by a blockquote with its translation. Keep the body as it is. Change the properties:

| lingua | deutschkurs |
|---|---|
| `Genre: Letter`, `School letter`, `Article` | Same |
| `Genre: Message` | `Genre: Chat` |
| `Genre: Invoice`, `Story` or any other value | `Genre: Other` |
| `Genre: Conversation` | Ask the learner; see below |
| `Source: Grundschule, 2020-09-01` (place and day) | `Source: Grundschule` and `Received: 2020-09-01` |
| No `Level` | `Level` is required: estimate it and tell the learner |
| A `Source` that names a person or a school | Replace it as `privacy.md` says |

A Text with `Genre: Conversation` is a dialogue. Ask the learner where it comes from: it happened and was written down word for word (`real`), it is remembered (`reconstructed`), or it was written to practise (`model`). Then write it as `Type: Conversation` with that `Kind`, one turn per paragraph, speakers as roles. When the learner does not know, keep it a Text with `Genre: Other`.

lingua:

```text
---
Type: Text
Genre: Message
Topic: Schule
Source: Elternchat, 2026-10-30
Date: 2026-11-02
---

# Kein Sport am Montag

Am Montag ist kein Sport.

> There is no PE on Monday.
```

deutschkurs:

```markdown
---
Checked: unchecked
Date: 2026-11-02
Genre: Chat
Level: A1
Received: 2026-10-30
Source: Elternchat
Topic: Schule
Type: Text
---

# Kein Sport am Montag

Am Montag ist kein Sport.

> There is no PE on Monday.
```
