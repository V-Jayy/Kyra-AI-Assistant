import sys
import types

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


def test_invalid_json():
    msg = summarise_router_reply('')
    assert msg == ""


def test_noise_wrapped_json():
    text = 'LOG something {"function": {"name": "search_files"}} end'
    msg = summarise_router_reply(text)
    assert "search_files" in msg
