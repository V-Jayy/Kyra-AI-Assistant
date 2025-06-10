import os, sys, types

# Stub pyaudio so importing assistant works without system deps
sys.modules['pyaudio'] = types.SimpleNamespace(PyAudio=lambda: None, paInt16=0)

from app.assistant import summarise_router_reply


def test_open_website():
    assert summarise_router_reply(
        '{"function":{"name":"open_website"},"arguments":{"url":"https://www.google.com"}}'
    ) == "Opening www.google.com"


def test_invalid_json():
    assert summarise_router_reply('') == "I was unable to get that."

