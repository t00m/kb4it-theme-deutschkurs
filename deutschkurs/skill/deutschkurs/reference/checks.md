# Checks

`kb4it build` and `kb4it verify` report problems in the entries. Fix every one; with `"strict": true` in the `deutschkurs` settings, any problem stops the build.

## Metadata problems

Each line looks like `META_INVALID doc=<file> key=<key> reason=<reason>`.

| Reason | Cause | Fix |
|---|---|---|
| `type_missing` | No `Type` property | Add `Type: Word`, `Verb`, `Chunk` or `Grammar` |
| `type_unknown` | `Type` is not one of the four | Correct it; Text and other types come in later versions |
| `level_missing` | No `Level` | Add `Level: A1` to `C2` |
| `level_invalid` | `Level` is not `A1` to `C2` | Correct it |
| `translation_missing` | Word, Verb or Chunk without `Translation` | Add the translation in the `native` language |
| `article_missing` | Noun without `der`, `die` or `das` | Add `Article`, or `PluralOnly: yes` for plural-only nouns |
| `part_of_speech_invalid` | `PartOfSpeech` missing or not an allowed value | Use one of the values in `entry-types.md`, lower case |
| `participle_missing` | Verb without `Participle` | Add it, such as `Participle: gegangen` |
| `auxiliary_missing` | Verb without `Auxiliary`, or a value other than `haben` and `sein` | Add `Auxiliary: haben` or `sein` |
| `prefix_missing` | `Separable: yes` without `Prefix` | Add `Prefix: an` |
| `register_invalid` | `Register` not `du`, `Sie`, `neutral` or `colloquial` | Correct it |
| `checked_invalid` | `Checked` not one of the five values | Use a value from `conventions.md` |
| `area_invalid` | Grammar without `Area`, or not an allowed value | Use one of the values in `entry-types.md` |
| `date_invalid` | `Date` not `YYYY-MM-DD` | Write it as `2026-11-09` |
| `topic_unknown` | `Topic` not in the `topics` setting | Use an allowed topic, or ask the learner to add it to the setting |
| `explanation_missing` | Grammar without a `## Explanation` section | Add it |

## KB4IT messages

| Message | Cause | Fix |
|---|---|---|
| `DOC_INVALID reason=missing_frontmatter` | The file does not start with `---` | Add the frontmatter |
| `DOC_INVALID reason=yaml_error` | The frontmatter is not valid YAML; the message gives line and column | Quote the value, or fix `Plural: -` to `Plural: none` |
| `DOC_NAME_RESERVED` | The file name is one of the theme's own pages | Rename the file |
| `LABEL_UNKNOWN key=<key>` | A `labels` override names a label that does not exist | Remove or correct that key in the `labels` setting |
| `THEME_SETTING_UNKNOWN` | An unknown key in the `deutschkurs` block of `repo.json` | Remove or correct it |
