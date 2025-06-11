import os, sys, types

sys.modules['pyaudio'] = types.SimpleNamespace(PyAudio=lambda: None, paInt16=0)

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.assistant import play_music

class FakeResp:
    def __init__(self, text):
        self.text = text

def test_play_music_fetch(monkeypatch):
    opened = {}
    def fake_open(url):
        opened['url'] = url
        return True
    def fake_get(url, timeout=5):
        return FakeResp('<a href="/watch?v=abc123def45">')
    monkeypatch.setattr('webbrowser.open', fake_open)
    monkeypatch.setattr('requests.get', fake_get)
    ok, msg = play_music(query='test song')
    assert ok
    assert opened['url'] == 'https://www.youtube.com/watch?v=abc123def45'
