import os, sys, types

sys.modules['pyaudio'] = types.SimpleNamespace(PyAudio=lambda: None, paInt16=0)

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.assistant import play_music

def test_play_music_fetch(monkeypatch):
    opened = {}
    def fake_open(url):
        opened['url'] = url
        return True
    monkeypatch.setattr('webbrowser.open', fake_open)
    ok, msg = play_music(query='test song')
    assert ok
    assert opened['url'].startswith('https://www.youtube.com/results?search_query=')
