import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core import tools


def test_open_website():
    success, msg = tools.open_website("example.com")
    assert success
    assert msg == "Opening example.com"


def test_derive_glob_from_phrase():
    pattern = tools.derive_glob_from_phrase("pdf file")
    assert pattern == "*.pdf"
    pattern2 = tools.derive_glob_from_phrase("my notes")
    assert pattern2 == "*my*notes*"
