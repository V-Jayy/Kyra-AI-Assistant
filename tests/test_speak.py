import os, sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.assistant import speak


def test_speak_empty(monkeypatch):
    monkeypatch.setattr("app.tts.speak", lambda text: None)
    speak("", True)
    speak("   ", True)
