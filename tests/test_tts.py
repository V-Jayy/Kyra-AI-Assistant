import os, sys, types
import pytest

# Stub piper and edge_tts so safe_speak imports without deps
edge_mock = types.SimpleNamespace(Communicate=lambda text, voice: types.SimpleNamespace(save=lambda f: None))
sys.modules.setdefault('edge_tts', edge_mock)
voice_stub = types.SimpleNamespace(config=types.SimpleNamespace(sample_rate=22050), speak=lambda t: [0])
sys.modules.setdefault('piper', types.SimpleNamespace(PiperVoice=types.SimpleNamespace(load=lambda *a, **k: voice_stub)))
sys.modules.setdefault('sounddevice', types.SimpleNamespace(play=lambda *a, **k: None, wait=lambda: None))
sys.modules.setdefault('numpy', types.SimpleNamespace(array=lambda a: a))

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.tts import safe_speak

def test_safe_speak_empty():
    import asyncio
    with pytest.raises(ValueError):
        asyncio.run(safe_speak(""))

def test_safe_speak_runs():
    import asyncio
    asyncio.run(safe_speak("hi"))
