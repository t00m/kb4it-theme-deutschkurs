# Conventions

## File names

- Lower case, words joined by hyphens, ending in `.md`: `termin.md`, `bescheid-sagen.md`, `perfekt-haben-sein.md`.
- Umlauts and ß spelled out: `ä` as `ae`, `ö` as `oe`, `ü` as `ue`, `ß` as `ss` (`maedchen.md`, `strasse.md`).
- These names are taken by the theme's own pages and are refused: `vocabulary`, `verbs`, `chunks`, `grammar`, `texts`, `conversations`, `situations`, `photos`, `mistakes`, `inbox`, `practice`, `progress`, `skill`, `search`, `404`, and `add` while the editor is on.

## Frontmatter

- Every file starts with `---`, the properties, and `---`. A file without frontmatter is refused by KB4IT.
- One property per line: `Key: value`. Keep keys in alphabetical order; it makes files easy to compare.
- KB4IT splits every value on commas. `Topic: Schule, Familie` gives two topics. Never put a sentence or an explanation with a comma in a property: write it in the body.
- Quote a value with double quotes when it contains `: ` or starts with `[`, `{`, `#`, `&`, `*`, `!`, `|`, `>`, `%`, `@` or `-`.
- A word with no plural is `Plural: none`, never `Plural: -` (a bare dash breaks YAML).

## Body

- One `#` title, right after the frontmatter and a blank line.
- `##` sections with the names in `entry-types.md`, in that order.
- Translation pairs are list items: `- German :: translation`. The German comes first. A Listen button is added to each.
- One sentence per list item.

## Checked: how sure a fact is

| Value | Meaning | Who sets it |
|---|---|---|
| `unchecked` | Nobody checked it yet | Default; converted files |
| `assistant` | An AI assistant wrote or checked it | You |
| `reference` | Checked against a named dictionary or grammar, named in `Source` | You or the learner |
| `native` | A native speaker confirmed it | Only the learner |
| `attested` | Seen or heard in real life | Only the learner |

The site underlines `unchecked` and `assistant` facts with dots, so the learner knows what to trust less.

## Sources

Good references for German: Duden (duden.de) and DWDS (dwds.de) for words, articles, plurals and verb forms. Name them in `Source` when you used them, and then you may set `Checked: reference`.
