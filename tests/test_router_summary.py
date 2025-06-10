import sys
import types

# Stub pyaudio so importing assistant works without system deps
sys.modules["pyaudio"] = types.SimpleNamespace(PyAudio=lambda: None, paInt16=0)

from app.assistant import summarise_router_reply  # noqa: E402


def test_dict_input_old_schema():
    obj = {"function": "launch_app"}
    assert summarise_router_reply(obj) == "launch_app"


def test_open_website_string_new_schema():
    data = (
        '{"function": {"name": "open_website", "arguments": {"url": "google.com"}}}'
    )
    assert summarise_router_reply(data) == "open_website"


def test_invalid_json():
    assert summarise_router_reply('') is None


def test_noise_wrapped_json():
    text = 'LOG something {"function": {"name": "search_files"}} end'
    assert summarise_router_reply(text) == "search_files"
