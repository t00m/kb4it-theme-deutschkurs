#!/usr/bin/env bash
# Pack the theme into dist/deutschkurs-<version>.zip with one top folder named deutschkurs/.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
python3 - "$root" <<'PY'
import json, os, sys, zipfile
root = sys.argv[1]
theme = os.path.join(root, "deutschkurs")
version = json.load(open(os.path.join(theme, "theme.json"), encoding="utf-8"))["version"]
os.makedirs(os.path.join(root, "dist"), exist_ok=True)
out = os.path.join(root, "dist", f"deutschkurs-{version}.zip")
skip_dirs = {"__pycache__", "target", "var", ".pytest_cache"}
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
    for folder, dirs, files in os.walk(theme):
        dirs[:] = sorted(d for d in dirs if d not in skip_dirs)
        for name in sorted(files):
            if name.endswith((".pyc", ".pyo")):
                continue
            path = os.path.join(folder, name)
            zf.write(path, os.path.join("deutschkurs", os.path.relpath(path, theme)))
print(out)
PY
