# Entry types

One file per entry, in the course's `source/` folder. Each file has YAML frontmatter, one `#` title, and optional `##` sections. Section headings are in English, exactly as written here. Unknown sections are kept and shown as normal text.

## Common properties

| Property | Values | Rule |
|---|---|---|
| `Type` | `Word`, `Verb`, `Chunk`, `Grammar` | Required |
| `Level` | `A1`, `A2`, `B1`, `B2`, `C1`, `C2` | Required |
| `Translation` | Text in the `native` language | Required for Word, Verb and Chunk |
| `Checked` | `unchecked`, `assistant`, `reference`, `native`, `attested` | Optional, default `unchecked`; see `conventions.md` |
| `Topic` | Free, or one of the `topics` setting | Optional, several allowed |
| `Situation` | Title of a Situation | Do not use yet: Situation entries come in a later version |
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
- `## False friends`: words that look like Spanish or English words but mean something else.
- `## Notes`: anything else, short.

```markdown
---
Article: der
Checked: assistant
Level: A1
PartOfSpeech: noun
Plural: die Termine
Source: Duden
Stress: Ter-MIN
Topic: Schule
Translation: cita
Type: Word
---

# Termin

## Examples

- Ich habe morgen einen Termin beim Arzt. :: Mañana tengo cita con el médico.
- Können wir einen Termin vereinbaren? :: ¿Podemos concertar una cita?

## False friends

*Termin* no es *término*: es una cita con hora fija.
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
Translation: llamar por teléfono
Type: Verb
---

# anrufen

## Examples

- Ich rufe dich morgen an. :: Te llamo mañana.
- Hast du die Schule angerufen? :: ¿Has llamado al colegio?

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
Translation: avisar a alguien
Type: Chunk
---

# Bescheid sagen

## Variants

- Sag mir Bescheid! :: ¡Avísame!
- Sagen Sie mir bitte Bescheid. :: Avíseme, por favor.

## Usage

Cuando prometes informar a alguien más tarde. La persona va en dativo: mir, dir, Ihnen.
```

## Grammar

One grammar point, explained briefly.

| Property | Values | Rule |
|---|---|---|
| `Area` | `Verbs`, `Nouns`, `Cases`, `Word order`, `Sentences`, `Other` | Required |
| `Case` | `Akkusativ`, `Dativ`, `Genitiv`, `Nominativ` | Optional; the page lists verbs whose `Government` is this case |
| `Tense` | `Präsens`, `Perfekt`, `Präteritum`, `Futur` | Optional |
| `Pattern` | A short slug such as `es-tener-haben` | Optional; used by Mistake entries in a later version |
| `Marker` | Words that signal the point, such as `weil, dass` | Optional; used in a later version |

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

El Perfekt es el pasado de la conversación: *haben* o *sein* más el participio al final.
Con *sein* van los verbos de movimiento o cambio de estado: *gehen*, *fahren*, *kommen*.

## Simple German

Das Perfekt ist die Vergangenheit im Gespräch. Bewegung oder Veränderung: mit *sein*. Sonst: mit *haben*.

## Typical mistakes

- Ich habe nach Hause gegangen. :: Ich bin nach Hause gegangen.
```
