import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core.dispatcher import match_intent


def test_match_play():
    name, args = match_intent("please play Bohemian Rhapsody on youtube")
    assert name == "play_music"
    assert args["query"] == "bohemian rhapsody"


def test_match_search():
    name, args = match_intent("Search for openai")
    assert name == "open_website"
    assert "openai" in args["url"]


def test_match_open():
    name, args = match_intent("Can you open google.com")
    assert name == "open_website"
    assert args["url"] == "google.com"
