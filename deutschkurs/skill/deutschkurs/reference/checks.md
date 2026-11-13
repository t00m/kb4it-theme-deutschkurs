# Checks

`kb4it build` and `kb4it verify` report problems in the entries. Fix every one; with `"strict": true` in the `deutschkurs` settings, any problem stops the build.

## Metadata problems

Each line looks like `META_INVALID doc=<file> key=<key> reason=<reason>`. Some end with ` line=<number>`: the line of the file to fix.

| Reason | Cause | Fix |
|---|---|---|
| `type_missing` | No `Type` property | Add `Type: Word`, `Verb`, `Chunk`, `Grammar`, `Text`, `Conversation`, `Situation`, `Photo`, `Mistake`, `Gap` or `Inbox` |
| `type_unknown` | `Type` is not one of the eleven | Correct it |
| `level_missing` | No `Level`, on any type but Situation, Photo, Gap and Inbox | Add `Level: A1` to `C2` |
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
| `date_invalid` | `Date`, `NextTime`, `Received` or `Deadline` not `YYYY-MM-DD`, or not a real day such as `2026-13-45` | Write it as `2026-11-09` |
| `flag_invalid` | `PluralOnly`, `Irregular`, `Separable`, `Reflexive` or `Reply` with a value other than `yes` (such as `Yes` or `true`) | Write `yes` in lower case, or remove the property |
| `topic_unknown` | `Topic` not in the `topics` setting | Use an allowed topic, or ask the learner to add it to the setting |
| `explanation_missing` | Grammar without a `## Explanation` section | Add it. Only `kb4it build` reports this one: `kb4it verify` reads properties, not sections |
| `kind_missing` | Conversation without `Kind` | Add `Kind: real`, `reconstructed` or `model`; ask the learner when you do not know |
| `kind_invalid` | `Kind` not `real`, `reconstructed` or `model` | Correct it, lower case |
| `genre_invalid` | `Genre` of a Text not an allowed value | Use one of the values in `entry-types.md`, or `Other` |
| `turn_invalid` | An item of the turn list, or of `## Variations`, is not written `**Speaker:** German`; a variation also needs the turn number first | Fix the line the message names. Only `kb4it build` reports this one |
| `place_invalid` | `Place` of a Photo not an allowed value | Use one of the values in `entry-types.md`, or `Other` |
| `mistake_incomplete` | A Mistake without text under `## Wrong` or `## Right` | Write one sentence in each. Only `kb4it build` reports this one |
| `situation_unknown` | A `Situation` value is not the title of a Situation entry | Correct the spelling, or create the Situation entry. Only `kb4it build` reports this one |

## Other theme messages

| Message | Cause | Fix |
|---|---|---|
| `LABEL_UNKNOWN key=<key>` | A `labels` override names a label that does not exist | Remove or correct that key in the `labels` setting |
| `COLOR_INVALID key=<key>` | `accent` or a `gender_colors` value is not a CSS colour; the default is used | Use a hex colour such as `#c0392b`, a colour name, or `rgb()` |
| `PAGE_NAME_TAKEN doc=<file>` | The file name is the name of a facet page, in any case: `Level`, `Topic`, `Register`, `ConversationKind`, `Genre`, `Place` or `Pattern`, alone or followed by `_` | Rename the file, for example `genre.md` to `das-genre.md` |

## Privacy and photo messages

Only `kb4it build` reports these: they read the text of the files and the images. Details in `privacy.md`.

| Message | Cause | Fix |
|---|---|---|
| `PRIVACY_SUSPECT doc=<file> reason=<reason> line=<n>` | That line looks like personal data: an IBAN, an e-mail address, a phone number or an address | Replace it with a placeholder from `privacy.md`. When it is not personal (a seat number, the address of a public office), leave the text and let the learner add it to `privacy_allow` |
| `PHOTO_GPS doc=<image>` | The image under `resources/photos/` holds GPS data: where it was taken. With `strict`, it stops the build | Remove the location data: save the image again without metadata, or turn off location in the camera app |
| `PHOTO_MISSING doc=<file> reason=missing` | The Photo names an image file that does not exist | Correct the path, or add the image under `source/resources/photos/` |
| `PHOTO_MISSING doc=<file> reason=none` | The Photo has no image before its first section | Add `![what it shows](resources/photos/<file>)` under the title |
| `PHOTO_UNREADABLE doc=<image>` | An image under `resources/photos/` cannot be opened, so it was not checked for GPS data | Save the image again as JPEG or WebP, or remove the broken file |
| `PHOTO_MISSING doc=<file> reason=remote` | The image of a Photo, or of an inbox capture, is a web address; the Inbox page leaves such an image out | Save the image under `source/resources/photos/`; pages never load anything from the internet |
| `AUDIO_MISSING doc=<file> reason=missing` | An `Audio` property or an `[audio](...)` link of a turn names a file that does not exist; a `?query` or `#fragment` after the extension is ignored for this check | Correct the path, or add the recording under `source/resources/audio/` |
| `AUDIO_MISSING doc=<file> reason=remote` | A recording is a web address; the page does not load it and uses the device voice | Save the recording under `source/resources/audio/` |
| `AUDIO_MISSING doc=<file> reason=type` | `Audio` names a file that is not `.m4a`, `.mp3`, `.ogg`, `.oga`, `.opus`, `.wav` or `.webm`; the page uses the device voice | Point to the recording, not to another file |

## KB4IT messages

| Message | Cause | Fix |
|---|---|---|
| `DOC_INVALID reason=missing_frontmatter` | The file does not start with `---` | Add the frontmatter |
| `DOC_INVALID reason=yaml_error` | The frontmatter is not valid YAML; the message gives line and column | Quote the value, or fix `Plural: -` to `Plural: none` |
| `DOC_NAME_RESERVED` | The file name is one of the theme's own pages | Rename the file |
| `THEME_SETTING_UNKNOWN` | An unknown key in the `deutschkurs` block of `repo.json` | Remove or correct it |
