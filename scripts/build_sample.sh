#!/usr/bin/env bash
# Build the starter course with the theme of this repository into a temporary folder.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
kb4it="${KB4IT:-$root/.venv/bin/kb4it}"
work="$(mktemp -d)"
cp -r "$root/deutschkurs/apps/default" "$work/site"
mkdir -p "$work/site/target"
python3 - "$work/site/config/repo.json" "$root/deutschkurs" <<'PY'
import json, sys
path, theme = sys.argv[1], sys.argv[2]
repo = json.load(open(path, encoding="utf-8"))
repo["theme_path"] = theme
json.dump(repo, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
PY
"$kb4it" build "$work/site/config/repo.json"
echo "$work/site/target/index.html"
