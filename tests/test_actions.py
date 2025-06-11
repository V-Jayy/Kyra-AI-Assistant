import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core.tools import open_website


def test_open_website():
    success, msg = open_website("example.com")
    assert success
    assert msg == "Opening example.com"
