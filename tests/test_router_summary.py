import sys
import types

# Stub pyaudio so importing assistant works without system deps
sys.modules["pyaudio"] = types.SimpleNamespace(PyAudio=lambda: None, paInt16=0)

from app.assistant import summarise_router_reply  # noqa: E402


def test_dict_input_old_schema():
    obj = {"function": "launch_app"}
    msg = summarise_router_reply(obj)
    assert msg == "launch_app"


def test_open_website_string_new_schema():
    data = (
        '{"function": {"name": "open_website", "arguments": {"url": "google.com"}}}'
    )
    msg = summarise_router_reply(data)
    assert "Opening" in msg
    assert "google.com" in msg


def test_open_website_full_url():
    data = (
        '{"function": {"name": "open_website", "arguments": {"url": "https://youtube.com/watch?v=abc"}}}'
    )
    msg = summarise_router_reply(data)
    assert msg == "Opening youtube.com"


def test_invalid_json():
    msg = summarise_router_reply('')
    assert msg == ""


def test_noise_wrapped_json():
    text = 'LOG something {"function": {"name": "search_files"}} end'
    msg = summarise_router_reply(text)
    assert "search_files" in msg
