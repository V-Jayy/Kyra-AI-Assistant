import os, sys, types

# Provide stub pyaudio so importing speak doesn't require system deps
sys.modules['pyaudio'] = types.SimpleNamespace(PyAudio=lambda: None, paInt16=0)

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.assistant import speak


def test_speak_empty(monkeypatch):
    monkeypatch.setattr("app.tts.safe_speak", lambda text: None)
    speak("", True)
    speak("   ", True)
