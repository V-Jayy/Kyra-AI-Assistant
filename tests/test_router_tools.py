import os, sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.scenarios import FakeLLM


def test_router_returns_tools():
    responses = {
        "close discord": {
            "choices": [
                {
                    "finish_reason": "tool_calls",
                    "message": {
                        "tool_calls": [
                            {"function": {"name": "kill_process", "arguments": '{"name": "discord"}'}}
                        ]
                    },
                }
            ]
        },
        "search song": {
            "choices": [
                {
                    "finish_reason": "tool_calls",
                    "message": {
                        "tool_calls": [
                            {"function": {"name": "play_music", "arguments": '{"url": "https://youtu.be/123"}'}}
                        ]
                    },
                }
            ]
        },
        "open example.com": {
            "choices": [
                {
                    "finish_reason": "tool_calls",
                    "message": {
                        "tool_calls": [
                            {"function": {"name": "open_website", "arguments": '{"url": "example.com"}'}}
                        ]
                    },
                }
            ]
        },
        "find file": {
            "choices": [
                {
                    "finish_reason": "tool_calls",
                    "message": {
                        "tool_calls": [
                            {"function": {"name": "search_files", "arguments": '{"directory": ".", "pattern": "*.txt"}'}}
                        ]
                    },
                }
            ]
        },
        "how are you": {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"content": "I'm fine"},
                }
            ]
        },
    }
    router = FakeLLM(responses)

    name, args, _ = router.route("close discord")
    assert name == "kill_process"
    assert args["name"] == "discord"

    name, args, _ = router.route("search song")
    assert name == "play_music"
    assert args["url"].startswith("http")

    name, args, _ = router.route("open example.com")
    assert name == "open_website"
    assert args["url"] == "example.com"

    name, args, _ = router.route("find file")
    assert name == "search_files"
    assert args["pattern"] == "*.txt"

    name, args, _ = router.route("how are you")
    assert name is None
    assert args["content"] == "I'm fine"
