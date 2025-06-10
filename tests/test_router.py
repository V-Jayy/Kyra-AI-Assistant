import os, sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.scenarios import FakeLLM


def test_router_fake_llm():
    responses = {
        "Hey Aurora, open youtube.com": {
            "choices": [
                {
                    "finish_reason": "tool_calls",
                    "message": {
                        "tool_calls": [
                            {
                                "function": {
                                    "name": "open_website",
                                    "arguments": '{"url": "youtube.com"}',
                                }
                            }
                        ]
                    },
                }
            ]
        }
    }
    router = FakeLLM(responses)
    name, args, _ = router.route("Hey Aurora, open youtube.com")
    assert name == "open_website"
    assert args["url"] == "youtube.com"
