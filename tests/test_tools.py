import os, sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core import tools


def test_open_website():
    success, msg = tools.open_website("example.com")
    assert success
    assert "Opening" in msg
