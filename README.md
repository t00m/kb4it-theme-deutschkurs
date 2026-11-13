# kb4it-theme-deutschkurs

A [KB4IT](https://github.com/t00m/KB4IT) theme for a personal German course. You write what you meet in real life (school letters, chats, conversations at the school gate, street signs) as small Markdown files; KB4IT builds them into an offline website with situations, conversations, texts, linked vocabulary, verbs, phrases and grammar, Listen buttons and your own recordings, and practice with spaced repetition in the browser.

The theme also ships an assistant skill that helps you turn real material into correct course files, after removing personal data.

## Install

You need KB4IT 0.12.x. It is not on PyPI yet, so install it from its git tag:

```bash
pipx install "git+https://github.com/t00m/KB4IT@0.12.0"
```

Download `deutschkurs-X.Y.Z.zip` from the [releases](https://github.com/t00m/kb4it-theme-deutschkurs/releases) and install it:

```bash
kb4it install-theme deutschkurs-0.7.0.zip
kb4it create deutschkurs default ~/deutschkurs
kb4it build ~/deutschkurs/config/repo.json
```

Open `~/deutschkurs/target/index.html` in a browser. The theme reference is in [deutschkurs/README.md](deutschkurs/README.md).

## Develop

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/pytest -q
node --test "tests/js/*.test.js"
scripts/build_sample.sh      # builds the starter course, prints the path of index.html
scripts/pack.sh              # writes dist/deutschkurs-<version>.zip
```

The theme lives in `deutschkurs/`, the folder name the release zip needs.

## Versions

- The theme follows Semantic Versioning; the version is in `deutschkurs/theme.json` and `CHANGELOG.md`.
- Below 1.0.0 a minor release may change the document format. The changelog says what to edit, and the skill learns the conversion.
- Each release is a `vX.Y.Z` tag on `main` and a GitHub release with the zip.
- Each theme version names the KB4IT versions it supports in `theme.json` (0.1.x to 0.6.x: `>=0.12.0, <0.13.0`).

## License

GPL v3, see [LICENSE](LICENSE).
