# Privacy

The learner's material comes from real life: school letters, chats with other parents, letters from offices, invoices. It names real people. The course must not.

## What to replace

Replace before you read the text for language, and before anything goes into a file:

| Data | Placeholder |
|---|---|
| A person's name | `Frau A.`, `Herr B.`, `Kind C.`; keep the gender if the grammar needs it |
| Street, house number, postcode, town of a private address | `[Adresse]` |
| Phone number | `[Telefon]` |
| E-mail address | `[E-Mail]` |
| IBAN, account or card number | `[IBAN]` |
| Date of birth | `[Geburtsdatum]` |
| Number plate | `[Kennzeichen]` |
| Customer, contract, case or tax number | `[Nummer]` |
| Name of the child's school, class or teacher | `die Schule`, `die Klasse 2b` becomes `die Klasse`, `Frau A.` |

Keep what the learner needs to learn: words, grammar, the kind of sender (`die Schule`, `das Bürgeramt`), dates of appointments and deadlines when they matter for the language.

## How

1. Replace the data.
2. Show the learner a short list: what kind of data you found and the placeholder you used. Do not repeat the original values in that list.
3. Continue with the anonymised text only.

When you are not sure whether something is personal, replace it.

## Conversations

- Speakers are roles: `Mutter`, `Lehrerin`, `Arzt`, `Nachbar`. The learner is `ich`.
- People named inside a turn get the same placeholders as in a text: `Frau A.`, `Kind C.`.
- When the learner tells you about a conversation, the account may hold other people's private matters, such as a diagnosis or a family problem. Keep the language the learner needs and leave the matter out, or make it general.
- The title names the moment, not the person: `Frage an die Lehrerin`.

## Photos

Do not describe faces or people in photos. If a photo shows a person, a number plate or a house number, say that the learner should crop or blur it before keeping the image.

Phone cameras store where a photo was taken. Tell the learner to remove that location data before the image goes into `source/resources/photos/`. You never write an image file yourself.

## What the build checks

`kb4it build` reads every file and logs `PRIVACY_SUSPECT doc=<file> reason=<reason> line=<n>` for text that looks like personal data. It is a filter that catches the obvious cases, not a proof that a file is clean: names, for example, are not detected.

| Reason | What it looks for |
|---|---|
| `iban` | Two letters, two digits and blocks of digits, such as a German IBAN with or without spaces |
| `email` | An e-mail address |
| `phone` | A number starting with `+49` or `0` and an area code, such as `030 1234567` |
| `address` | A five-digit postcode before a town name, or a street name ending in `straße`, `weg`, `platz`, `gasse`, `allee`, `ring`, `damm` or `ufer` with a house number |

A postcode followed by a unit such as `Euro` or `Stück`, and words such as `Sitzplatz 45` or `Heimweg 20`, are not reported. A customer or file number that starts with `0` can look like a phone number. A hit is a question, not a verdict: when the text is not personal data, leave it as it is. For text that is not personal, such as the public address of an office the learner needs, the learner adds the exact text to the `privacy_allow` setting, a list of strings. Every hit inside an allowed text is dropped, so one entry for a whole address covers its street and its postcode. Never add a private address there.

For each image under `source/resources/photos/` that holds GPS data, the build logs `PHOTO_GPS doc=<image>`. With `"strict": true`, privacy hits and photos with GPS data stop the build like metadata problems.
