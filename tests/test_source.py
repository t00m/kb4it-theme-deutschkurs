"""Entry pages show their Markdown source and link the editor and the git server (0.6.0, D3)."""

import json
import re
import subprocess

from conftest import KB4IT, BuiltSite, prepare_site


def bar(page):
    return re.search(r'<div class="dk-source-bar[^"]*">.*?</div>', page, re.S).group()


def test_source_dialog_holds_the_markdown(built_site):
    page = built_site.page("termin.html")
    assert 'href="#dk-source" data-uk-toggle' in bar(page)
    dialog = re.search(r'<div id="dk-source"[^>]*data-uk-modal.*?</textarea>', page, re.S).group()
    assert '<textarea id="dk-source-text" class="uk-textarea" readonly' in dialog
    assert "Type: Word" in dialog and "# Termin" in dialog
    assert "termin.md" in dialog


def test_edit_in_the_editor(built_site):
    assert re.search(r'<a class="dk-edit[^"]*" href="add.html" data-kb-edit="termin.md">Edit in the editor</a>',
                     bar(built_site.page("termin.html")))


def test_no_git_link_without_git(built_site):
    assert "dk-edit-git" not in built_site.page("termin.html")


def test_list_pages_have_no_source_bar(built_site):
    for name in ("index.html", "vocabulary.html", "practice.html"):
        assert "dk-source-bar" not in built_site.page(name), name


def test_git_link_when_git_is_set(tmp_path):
    config = prepare_site(tmp_path)
    repo = json.loads(config.read_text(encoding="utf-8"))
    repo.update(git=True, git_server="https://github.com", git_user="someone", git_repo="kurs", git_branch="main",
                git_path="source")
    config.write_text(json.dumps(repo), encoding="utf-8")
    run = subprocess.run([KB4IT, "build", str(config)], capture_output=True, text=True)
    assert run.returncode == 0, run.stdout[-2000:]
    site = BuiltSite(config.parent.parent, config.parent.parent / "target", "")
    assert re.search(r'<a class="dk-edit-git[^"]*" href="https://github.com/someone/kurs/edit/main/source/termin.md"',
                     bar(site.page("termin.html")))
