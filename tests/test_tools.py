import os, sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core import tools


def test_open_website():
    success, msg = tools.open_website("example.com")
    assert success
    assert "Opening" in msg


def test_derive_glob_from_phrase():
    pattern = tools.derive_glob_from_phrase("pdf file")
    assert pattern == "*.pdf"
    pattern2 = tools.derive_glob_from_phrase("my notes")
    assert pattern2 == "*my*notes*"


def test_open_explorer(monkeypatch, tmp_path):
    opened = []
    monkeypatch.setattr(tools.webbrowser, "open", lambda url: opened.append(url) or True)
    ok, msg = tools.open_explorer(str(tmp_path))
    assert ok
    assert opened


def test_create_note(tmp_path):
    ok, msg = tools.create_note("buy milk", directory=str(tmp_path))
    assert ok
    files = list(tmp_path.glob("note_*.txt"))
    assert files
    assert files[0].read_text().strip() == "buy milk"
