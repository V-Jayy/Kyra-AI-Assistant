import os, sys
import types

sys.modules.setdefault('rapidfuzz', types.SimpleNamespace(fuzz=types.SimpleNamespace(partial_ratio=lambda a,b: 100)))

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.intent_router import fuzzy_match, Action


def test_fuzzy_open():
    act = fuzzy_match("Could you please open google")
    assert isinstance(act, Action)
    assert act.name == "open_website"
    assert "url" in act.args


def test_fuzzy_open_folder():
    act = fuzzy_match("open ~/Downloads")
    assert isinstance(act, Action)
    assert act.name == "open_explorer"
    assert "path" in act.args
