# Entry types

One file per entry, in the course's `source/` folder. Each file has YAML frontmatter, one `#` title, and optional `##` sections. Section headings are in English, exactly as written here. Unknown sections are kept and shown. In any section, a list item written `German :: translation` gets a Listen button.

## Common properties

| Property | Values | Rule |
|---|---|---|
| `Type` | `Word`, `Verb`, `Chunk`, `Grammar`, `Text`, `Conversation`, `Situation` | Required |
| `Level` | `A1`, `A2`, `B1`, `B2`, `C1`, `C2` | Required, except for a Situation |
| `Translation` | Text in the `native` language | Required for Word, Verb and Chunk |
| `Checked` | `unchecked`, `assistant`, `reference`, `native`, `attested` | Optional, default `unchecked`; see `conventions.md` |
| `Topic` | Free, or one of the `topics` setting | Optional, several allowed |
| `Situation` | The `#` title of a Situation entry, exactly as written | Optional, several allowed; the entry is then listed on the page of that situation |
| `Source` | Free text | Optional; where the entry comes from |
| `Date` | `YYYY-MM-DD` | Optional; the day the entry was added |
| `Tag` | Free | Optional |

## Word

Nouns, adjectives, adverbs and other single words. The `#` title is the word without article.

| Property | Values | Rule |
|---|---|---|
| `PartOfSpeech` | `noun`, `adjective`, `adverb`, `preposition`, `conjunction`, `pronoun`, `particle`, `other` | Required |
| `Article` | `der`, `die`, `das` | Required for nouns, except plural-only nouns |
| `Plural` | `die Termine`, or `none` | Optional; with the article; `none` when there is no plural |
| `PluralOnly` | `yes` | Optional; for nouns that only exist in the plural, such as *Eltern* |
| `Forms` | Other forms | Optional; such as `Termins, Terminen`, so links find them |
| `Stress` | `Ter-MIN` | Optional; the stressed syllable in capitals |
| `Regional` | Other words for the same thing | Optional; such as `Brotbox, Brotbüchse` |
| `Family` | Related words | Optional; such as `der Terminkalender`; linked when an entry exists |

Sections, all optional, in this order:

- `## Examples`: list items `German sentence :: translation`.
- `## Pronunciation`: what is hard to say for the learner.
- `## False friends`: words that look like words of the learner's language but mean something else.
- `## Notes`: anything else, short.

```markdown
---
Article: der
Checked: assistant
Level: A1
PartOfSpeech: noun
Plural: die Termine
Stress: Ter-MIN
Topic: Schule
Translation: appointment
Type: Word
---

# Termin

## Examples

- Ich habe morgen einen Termin beim Arzt. :: Tomorrow I have a doctor's appointment.
- Können wir einen Termin vereinbaren? :: Can we make an appointment?

## False friends

*Termin* is not a *term*: it is an appointment with a fixed time.
```

## Verb

The `#` title is the infinitive.

| Property | Values | Rule |
|---|---|---|
| `Participle` | `angerufen` | Required |
| `Auxiliary` | `haben`, `sein` | Required; both when the verb takes both |
| `Present` | `ich rufe an, du rufst an, er ruft an` | Optional; always with the pronoun, because KB4IT drops repeated values |
| `Preterite` | `ich rief an` | Optional; with the pronoun |
| `Irregular` | `yes` | Optional |
| `Separable` | `yes` | Optional; needs `Prefix` |
| `Prefix` | `an` | Required when `Separable: yes` |
| `Reflexive` | `yes` | Optional |
| `Government` | `Akkusativ`, `Dativ`, `Präposition` | Optional; the case or preposition the verb takes |
| `Preposition` | `auf + Akk` | Optional; when `Government: Präposition` |
| `KonjunktivII` | `würde anrufen` | Optional |
| `Stress` | `AN-ru-fen` | Optional; for separable verbs the page stresses the prefix when this is missing |

Sections, all optional:

- `## Examples`: list items `German sentence :: translation`.
- `## Typical mistakes`: list items `wrong :: right`.
- `## Notes`.

```markdown
---
Auxiliary: haben
Checked: assistant
Government: Akkusativ
Irregular: yes
Level: A1
Participle: angerufen
Prefix: an
Present: ich rufe an, du rufst an, er ruft an, wir rufen an, ihr ruft an, sie rufen an
Preterite: ich rief an
Separable: yes
Translation: to phone
Type: Verb
---

# anrufen

## Examples

- Ich rufe dich morgen an. :: I will call you tomorrow.
- Hast du die Schule angerufen? :: Have you called the school?

## Typical mistakes

- Ich anrufe dich. :: Ich rufe dich an.
```

## Chunk

A fixed phrase used as one block. The `#` title is the phrase.

| Property | Values | Rule |
|---|---|---|
| `Register` | `du`, `Sie`, `neutral`, `colloquial` | Optional; who you can say it to |

Sections, all optional:

- `## Variants`: list items `German variant :: translation`.
- `## Usage`: when to say it, in a few lines.

```markdown
---
Checked: assistant
Level: A2
Register: neutral
Translation: to let someone know
Type: Chunk
---

# Bescheid sagen

## Variants

- Sag mir Bescheid! :: Let me know!
- Sagen Sie mir bitte Bescheid. :: Please let me know. (formal)

## Usage

When you promise to tell someone later. The person is in the dative: mir, dir, Ihnen.
```

## Grammar

One grammar point, explained briefly.

| Property | Values | Rule |
|---|---|---|
| `Area` | `Verbs`, `Nouns`, `Cases`, `Word order`, `Sentences`, `Other` | Required |
| `Case` | `Akkusativ`, `Dativ`, `Genitiv`, `Nominativ` | Optional; the page lists verbs whose `Government` is this case |
| `Tense` | `Präsens`, `Perfekt`, `Präteritum`, `Futur` | Optional |
| `Pattern` | A short slug such as `es-tener-haben` | Optional; used by Mistake entries in a later version |
| `Marker` | Words that signal the point, such as `weil, dass` | Optional; the page lists the sentences of texts and conversations that contain one of them, as candidates |

Sections:

- `## Explanation`: required; in the `native` language, a few lines and an example.
- `## Simple German`: optional; the same in simple German. From `german_from` on it is shown first.
- `## Typical mistakes`: optional; list items `wrong :: right`.

```markdown
---
Area: Verbs
Checked: assistant
Level: A2
Tense: Perfekt
Type: Grammar
---

# Perfekt mit haben oder sein

## Explanation

The Perfekt is the past tense of conversation: *haben* or *sein* plus the participle at the end.
Verbs of movement or change of state take *sein*: *gehen*, *fahren*, *kommen*.

## Simple German

Das Perfekt ist die Vergangenheit im Gespräch. Bewegung oder Veränderung: mit *sein*. Sonst: mit *haben*.

## Typical mistakes

- Ich habe nach Hause gegangen. :: Ich bin nach Hause gegangen.
```

## Text

Something the learner read: a letter, a notice, a chat, an e-mail. The `#` title says what it is, without names.

| Property | Values | Rule |
|---|---|---|
| `Genre` | `Letter`, `School letter`, `Official letter`, `Notice`, `Contract`, `Chat`, `Email`, `Article`, `Other` | Optional |
| `Received` | `YYYY-MM-DD` | Optional; the day it arrived |
| `Deadline` | `YYYY-MM-DD` | Optional; the day an answer or a payment is due; the page shows a banner until that day has passed |
| `Reply` | `yes` | Optional; the text needs an answer |

Body, before any `##` heading: the German text, one short paragraph after the other. A blockquote right after a paragraph is its translation; the page folds it. Each paragraph is one sentence unit, numbered in order (`#s1`, `#s2`...). Lists, tables, images and code are shown but are not units.

Sections, all optional:

- `## Notes`: what was hard, what to do next.

```markdown
---
Checked: attested
Deadline: 2026-11-20
Genre: School letter
Level: A2
Received: 2026-11-09
Reply: yes
Situation: Elternbrief
Source: Elternbrief der Schule
Topic: Schule
Type: Text
---

# Elternbrief zum Ausflug

Liebe Eltern,

> Dear parents,

am Freitag machen wir einen Ausflug in den Zoo. Bitte geben Sie Ihrem Kind eine Brotdose mit.

> On Friday we are going on a trip to the zoo. Please give your child a lunch box.

Bitte geben Sie den Zettel bis zum 20. November bei Frau A. ab.

> Please hand in the slip to Ms A. by 20 November.

## Notes

*abgeben* is separable: Sie geben den Zettel ab.
```

## Conversation

A dialogue from the learner's life. The `#` title names the moment.

| Property | Values | Rule |
|---|---|---|
| `Kind` | `real`, `reconstructed`, `model` | Required; see below |
| `Me` | The speaker name that is the learner | Optional; default `ich` |
| `Register` | `du`, `Sie`, `neutral`, `colloquial` | Optional |

`Kind` says where the dialogue comes from, and the page shows it as a badge:

- `real`: written down or recorded as it was said.
- `reconstructed`: the learner remembers it; the wording may differ.
- `model`: written to practise. Everything an assistant invents is `model`.

Body, before any `##` heading: one list, one item per turn, written `**Speaker:** German :: translation`. The translation is optional. The turns are numbered by position (`#t1`, `#t2`...), so do not put other lists above the turns. Speaker names follow `privacy.md`: a role such as `Mutter`, `Lehrerin`, `Arzt`, never a real name.

Sections, all optional:

- `## Variations`: other ways a turn could go. Each item starts with the number of the turn it replaces: `3 **Mutter:** German :: translation`.
- `## Notes`.

```markdown
---
Checked: assistant
Date: 2026-11-05
Kind: model
Level: A1
Me: ich
Register: colloquial
Situation: Am Schultor
Type: Conversation
---

# Gruß am Schultor

- **Mutter:** Hallo! Na, wie geht's? :: Hello! How are you?
- **ich:** Hallo! Gut, danke. Und dir? :: Hello! Fine, thanks. And you?
- **Mutter:** Auch gut. Kommst du morgen zum Elternabend? :: Fine too. Are you coming to the parents' evening tomorrow?
- **ich:** Ja, ich komme. Bis morgen! :: Yes, I am coming. See you tomorrow!

## Variations

- 4 **ich:** Leider nicht, ich muss arbeiten. :: Sadly not, I have to work.

## Notes

*Na?* opens a chat between people who know each other.
```

## Situation

A moment of the learner's life that comes back: the school gate, the parents' evening, the doctor. The `#` title is the name other entries use in their `Situation` property. A Situation needs no `Level`.

| Property | Values | Rule |
|---|---|---|
| `NextTime` | `YYYY-MM-DD` | Optional; the next time it happens; the home page lists the situation in the days before |

Sections, all optional:

- `## I can`: a task list of what the learner wants to be able to do: `- [ ] Ich kann ... :: translation`. The learner ticks an item (`- [x]`) when it worked in real life. Never tick one yourself.
- `## Log`: dated items of what happened: `- 2026-11-10 What went well, what was missing.`

The page lists by itself every conversation, text, chunk, word, verb and grammar point whose `Situation` is this title.

```markdown
---
NextTime: 2026-11-10
Topic: Schule
Type: Situation
---

# Elternabend

## I can

- [x] Ich kann sagen, ob ich zum Elternabend komme. :: I can say whether I am coming to the parents' evening.
- [ ] Ich kann eine Frage zum Ausflug stellen. :: I can ask a question about the trip.

## Log

- 2026-11-10 Ich habe eine Frage gestellt und alles verstanden.
```
