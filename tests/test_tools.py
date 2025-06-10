import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core import tools  # noqa: E402


def test_open_website():
    success, msg = tools.open_website("example.com")
    assert success
    assert "Opening" in msg


def test_launch_app(monkeypatch):
    monkeypatch.setattr(tools.subprocess, "Popen", lambda *_: None)
    success, msg = tools.launch_app("dummy")
    assert success
    assert msg == "Launching dummy"


def test_derive_glob_from_phrase():
    pattern = tools.derive_glob_from_phrase("pdf file")
    assert pattern == "*.pdf"
    pattern2 = tools.derive_glob_from_phrase("my notes")
    assert pattern2 == "*my*notes*"
