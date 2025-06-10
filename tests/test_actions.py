import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from assistant.actions import open_website


def test_open_website():
    success, msg = open_website('example.com')
    assert success
    assert 'Opening' in msg
