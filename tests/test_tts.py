import os
import sys
import types
import pytest

# Stub pyttsx3 and edge_tts so safe_speak imports without deps
sys.modules.setdefault('pyttsx3', types.SimpleNamespace(init=lambda: types.SimpleNamespace(say=lambda t: None, runAndWait=lambda: None)))
edge_mock = types.SimpleNamespace(Communicate=lambda text, voice: types.SimpleNamespace(save=lambda f: None))
sys.modules.setdefault('edge_tts', edge_mock)

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.tts import safe_speak  # noqa: E402

def test_safe_speak_empty():
    import asyncio
    with pytest.raises(ValueError):
        asyncio.run(safe_speak(""))

def test_safe_speak_runs():
    import asyncio
    asyncio.run(safe_speak("hi"))
