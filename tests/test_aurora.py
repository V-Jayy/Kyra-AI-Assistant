import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    return mod

assistant = load_module("assistant_module", "assistant.py")
config = load_module("config_module", "config.py")
console_mod = load_module("console_module", "transcript_console.py")


def test_intent_parser():
    tool, args = assistant.parse_intent("open github.com")
    assert tool == "open_website"
    assert args["url"] == "github.com"


def test_wake_word(monkeypatch):
    monkeypatch.setattr(assistant.config, "WAKE_WORD", "Hey Test")
    monkeypatch.setattr(config, "WAKE_WORD", "Hey Test")
    assert assistant.detect_wake_word("Hey Test open")
    assert not assistant.detect_wake_word("Hello there")


def test_console_toggle(monkeypatch):
    monkeypatch.setattr(assistant.config, "DEBUG", True)
    monkeypatch.setattr(config, "DEBUG", True)
    console = console_mod.get_console()
    assert getattr(console, "enabled", False)
    monkeypatch.setattr(assistant.config, "DEBUG", False)
    monkeypatch.setattr(config, "DEBUG", False)
    console = console_mod.get_console()
    assert not getattr(console, "enabled", False)
