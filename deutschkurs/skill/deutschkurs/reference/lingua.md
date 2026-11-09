# Converting lingua files

lingua was an earlier KB4IT theme for language courses. Its files are close to deutschkurs files, but not the same. Convert them one by one, show the first result, and wait for the learner's agreement.

## Properties

| lingua | deutschkurs |
|---|---|
| `Type: Word`, `Verb`, `Grammar` | Same |
| `Type: Text` | Not supported yet: leave the file untouched and list it |
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

```text
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
