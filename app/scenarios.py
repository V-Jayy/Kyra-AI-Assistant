from __future__ import annotations

import csv
import argparse

from core.intent_router import IntentRouter
from core.transcript import Transcript
from core.tools import _REGISTRY


class FakeLLM(IntentRouter):
    def __init__(self, responses: dict[str, dict]):
        super().__init__()
        self.responses = responses

    def _post(self, payload):  # type: ignore[override]
        text = payload["messages"][-1]["content"]
        return self.responses[text]


def run_file(path: str) -> None:
    responses = {}
    with open("tests/intents.csv", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for utterance, tool in reader:
            responses[utterance] = {
                "choices": [
                    {
                        "finish_reason": "tool_calls",
                        "message": {
                            "tool_calls": [
                                {
                                    "function": {
                                        "name": tool,
                                        "arguments": "{}",
                                    }
                                }
                            ]
                        },
                    }
                ]
            }

    router = FakeLLM(responses)
    transcript = Transcript(True)
    for utterance in responses:
        transcript.log("USER", utterance)
        name, args, _ = router.route(utterance)
        fn = _REGISTRY[name]["callable"]
        ok, msg = fn(**args)
        transcript.log("BOT", msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="tests/intents.csv")
    args = parser.parse_args()
    run_file(args.path)
