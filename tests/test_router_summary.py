import sys
import types

# Stub pyaudio so importing assistant works without system deps
sys.modules["pyaudio"] = types.SimpleNamespace(PyAudio=lambda: None, paInt16=0)

from app.assistant import summarise_router_reply  # noqa: E402


def test_dict_input_old_schema():
    obj = {"function": "launch_app"}
    name, args = summarise_router_reply(obj)
    assert name == "launch_app"
    assert args == {}


def test_open_website_string_new_schema():
    data = (
        '{"function": {"name": "open_website", "arguments": {"url": "google.com"}}}'
    )
    name, args = summarise_router_reply(data)
    assert name == "open_website"
    assert args["url"] == "google.com"


def test_invalid_json():
    name, args = summarise_router_reply('')
    assert name is None
    assert args == {}


def test_noise_wrapped_json():
    text = 'LOG something {"function": {"name": "search_files"}} end'
    name, args = summarise_router_reply(text)
    assert name == "search_files"
    assert args == {}
