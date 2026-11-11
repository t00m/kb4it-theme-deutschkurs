# Conventions

## File names

- Lower case, words joined by hyphens, ending in `.md`: `termin.md`, `bescheid-sagen.md`, `perfekt-haben-sein.md`.
- Umlauts and ß spelled out: `ä` as `ae`, `ö` as `oe`, `ü` as `ue`, `ß` as `ss` (`maedchen.md`, `strasse.md`).
- A Situation that has the name of a word gets the prefix `situation-`: `elternabend.md` is the Word, `situation-elternabend.md` the Situation. Both keep the title `Elternabend`.
- These names are taken by the theme's own pages and are refused: `vocabulary`, `verbs`, `chunks`, `grammar`, `texts`, `conversations`, `situations`, `photos`, `mistakes`, `inbox`, `practice`, `progress`, `skill`, `search`, `404`, `Level`, `Topic`, `Register`, `ConversationKind`, `Genre`, `Place`, `Pattern`, `Article` (and names starting with `Article_`), and `add` while the editor is on.
- Names that start with `Level_`, `Topic_`, `Register_`, `ConversationKind_`, `Genre_`, `Place_` or `Pattern_`, in any case, clash with the theme's facet pages: the build warns, and the file must be renamed.
- `index.md`, when present, replaces the theme's home page.

## Frontmatter

- Every file starts with `---`, the properties, and `---`. A file without frontmatter is refused by KB4IT.
- One property per line: `Key: value`. Keep keys in alphabetical order; it makes files easy to compare.
- KB4IT splits every value on commas. `Topic: Schule, Familie` gives two topics. Never put a sentence or an explanation with a comma in a property: write it in the body.
- Quote a value with double quotes when it contains `: ` or starts with `[`, `{`, `#`, `&`, `*`, `!`, `|`, `>`, `%`, `@` or `-`.
- A word with no plural is `Plural: none`, never `Plural: -` (a bare dash breaks YAML).
- Yes-or-no properties (`PluralOnly`, `Irregular`, `Separable`, `Reflexive`, `Reply`) take only `yes`, in lower case. Leave them out for no.
- `Situation` holds the exact `#` title of a Situation entry. Several situations are separated by commas, so a Situation title never contains a comma.

## Body

- One `#` title, right after the frontmatter and a blank line.
- `##` sections with the names in `entry-types.md`, in that order.
- Translation pairs are list items: `- German :: translation`. The German comes first. A Listen button is added to each.
- One sentence per list item.

## Sentence units

The turns of a Conversation and the paragraphs of a Text are sentence units. Each one gets a Listen button, and the pages of the words, verbs and chunks in it link to it under "Where it appears".

- A turn is a list item written `**Speaker:** German :: translation`. Turns are numbered by position: `#t1`, `#t2`...
- A variation is an item of `## Variations` written `2 **Speaker:** German :: translation`, where `2` is the turn it replaces: `#v1`, `#v2`...
- A paragraph of a Text is followed by a blockquote with its translation: `#s1`, `#s2`...
- Keep a unit to one or two sentences. Split a long paragraph of a letter.
- The numbers are positions. Adding a unit in the middle moves every later one, which is fine: the build writes all links again.
- Write plain German in a unit: no links and no tables. The theme links the words it knows by itself.
- Speakers are roles (`Mutter`, `Lehrerin`, `Arzt`), never names.

## Checked: how sure a fact is

| Value | Meaning | Who sets it |
|---|---|---|
| `unchecked` | Nobody checked it yet | Default; converted files |
| `assistant` | An AI assistant wrote or checked it | You |
| `reference` | Checked against a named dictionary or grammar, named in `Source` | You or the learner |
| `native` | A native speaker confirmed it | Only the learner |
| `attested` | Seen or heard in real life | Only the learner |

Each entry page shows the value as a badge; `unchecked` and `assistant` badges are underlined with dots, so the learner knows what to trust less.

## Sources

Good references for German: Duden (duden.de) and DWDS (dwds.de) for words, articles, plurals and verb forms. Name them in `Source` when you used them, and then you may set `Checked: reference`.
