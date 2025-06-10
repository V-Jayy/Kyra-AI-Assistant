import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core.tools import sanitize_domain


def test_sanitize():
    assert sanitize_domain('https://WWW.Google.com/search') == 'google.com'
    assert sanitize_domain('play this song') == ''
