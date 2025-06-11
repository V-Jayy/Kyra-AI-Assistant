import os
import sys
import types

# Provide stub pyaudio so importing speak doesn't require system deps
sys.modules['pyaudio'] = types.SimpleNamespace(PyAudio=lambda: None, paInt16=0)

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.assistant import speak  # noqa: E402


def test_speak_no_tts():
    speak("test", False)
