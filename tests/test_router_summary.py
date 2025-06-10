import sys
import types

# Stub pyaudio so importing assistant works without system deps
sys.modules["pyaudio"] = types.SimpleNamespace(PyAudio=lambda: None, paInt16=0)

from app.assistant import summarise_router_reply  # noqa: E402


def test_open_website():
    data = (
        '{"function":{"name":"open_website"},'
        '"arguments":{"url":"https://www.google.com"}}'
    )
    assert summarise_router_reply(data) == "Opening www.google.com"


def test_launch_app():
    data = (
        '{"function":{"name":"launch_app"},'
        '"arguments":{"app":"notepad"}}'
    )
    assert summarise_router_reply(data) == "Launching notepad"


def test_invalid_json():
    assert summarise_router_reply('') == "I was unable to get that."
