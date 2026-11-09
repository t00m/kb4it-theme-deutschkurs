import json
import os
import re
import subprocess
import zipfile
from pathlib import Path

import pytest

from conftest import KB4IT

ROOT = Path(__file__).resolve().parent.parent
VERSION = json.loads((ROOT / "deutschkurs" / "theme.json").read_text(encoding="utf-8"))["version"]


@pytest.fixture(scope="module")
def zip_path():
    run = subprocess.run(["bash", str(ROOT / "scripts" / "pack.sh")], capture_output=True, text=True, cwd=ROOT)
    assert run.returncode == 0, run.stderr
    path = ROOT / "dist" / f"deutschkurs-{VERSION}.zip"
    assert path.is_file()
    return path


def test_version_matches_changelog():
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    released = re.search(r"^## \[(\d+\.\d+\.\d+)\]", changelog, re.M)
    assert released and released.group(1) == VERSION
    assert "## [Unreleased]" in changelog


def test_zip_layout(zip_path):
    names = zipfile.ZipFile(zip_path).namelist()
    assert all(name.startswith("deutschkurs/") for name in names)
    assert "deutschkurs/theme.json" in names
    assert "deutschkurs/skill/deutschkurs/SKILL.md" in names
    assert "deutschkurs/apps/default/config/repo.json" in names
    for bad in ("__pycache__", ".pyc", "/target/", "/var/"):
        assert not any(bad in name for name in names), bad


def test_zip_installs(zip_path, tmp_path):
    env = dict(os.environ, HOME=str(tmp_path), XDG_DATA_HOME=str(tmp_path / "data"),
               XDG_CONFIG_HOME=str(tmp_path / "config"))
    run = subprocess.run([KB4IT, "install-theme", str(zip_path)], capture_output=True, text=True, env=env)
    assert run.returncode == 0, run.stdout + run.stderr


def test_theme_info():
    run = subprocess.run([KB4IT, "theme-info", str(ROOT / "deutschkurs")], capture_output=True, text=True)
    assert run.returncode == 0
    assert re.search(r"^api\s+BaseTheme", run.stdout, re.M)
    assert "unused" not in run.stdout.lower()


def test_no_em_dash_in_docs():
    for name in ("README.md", "deutschkurs/README.md", "CHANGELOG.md"):
        assert "\u2014" not in (ROOT / name).read_text(encoding="utf-8"), name


def test_ci_workflow_present():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "KB4IT@0.12.0" in ci or "requirements-dev.txt" in ci
    assert 'node --test "tests/js/*.test.js"' in ci
