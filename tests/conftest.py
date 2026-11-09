"""Shared helpers: build the starter course with the theme from this repository."""

import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import pytest

ROOT = Path(__file__).resolve().parent.parent
THEME = ROOT / "deutschkurs"
STARTER = THEME / "apps" / "default"


def _kb4it() -> str:
    """The kb4it command next to this Python, on Linux, macOS and Windows."""
    bin_dir = Path(sys.executable).parent
    for candidate in (bin_dir / "kb4it", bin_dir / "kb4it.exe", bin_dir / "Scripts" / "kb4it.exe"):
        if candidate.is_file():
            return str(candidate)
    return shutil.which("kb4it") or "kb4it"


KB4IT = _kb4it()
LEVEL = re.compile(r"^\S+ \S+ \|\s+(WARNING|ERROR|CRITICAL) \|")


@dataclass
class BuiltSite:
    root: Path
    target: Path
    log: str

    def page(self, name: str) -> str:
        return (self.target / name).read_text(encoding="utf-8")


def warnings(log: str) -> list[str]:
    """Log lines at WARNING level or above."""
    return [line for line in log.splitlines() if LEVEL.match(line)]


def prepare_site(tmp: Path, extra: Mapping[str, str] = {}, settings: Mapping[str, Any] = {},
                 starter: bool = True) -> Path:
    """Copy the starter course into tmp, point it at this theme and return the repo.json path."""
    site = tmp / "site"
    shutil.copytree(STARTER, site)
    if not starter:
        for path in (site / "source").glob("*.md"):
            path.unlink()
    (site / "target").mkdir(exist_ok=True)
    for name, text in extra.items():
        (site / "source" / name).write_text(text, encoding="utf-8")
    config = site / "config" / "repo.json"
    repo = json.loads(config.read_text(encoding="utf-8"))
    repo["theme_path"] = str(THEME)
    repo.setdefault("deutschkurs", {}).update(settings)
    config.write_text(json.dumps(repo, indent=2, ensure_ascii=False), encoding="utf-8")
    return config


def build_site(tmp: Path, extra: Mapping[str, str] = {}, settings: Mapping[str, Any] = {},
               starter: bool = True) -> BuiltSite:
    """Build the starter course (or only the extra files) with the given theme settings."""
    config = prepare_site(tmp, extra, settings, starter)
    site = config.parent.parent
    run = subprocess.run([KB4IT, "build", str(config)], capture_output=True, text=True)
    assert run.returncode == 0, run.stdout[-3000:] + run.stderr[-3000:]
    log = (site / "var" / "log" / "kb4it.log").read_text(encoding="utf-8")
    return BuiltSite(site, site / "target", log)


@pytest.fixture(scope="session")
def built_site(tmp_path_factory) -> BuiltSite:
    return build_site(tmp_path_factory.mktemp("starter"))
