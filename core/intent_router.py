from __future__ import annotations

import json
from typing import Any, Dict, Tuple

from pydantic import BaseModel

from kyra.local_llm import generate
from .config import MODEL_NAME, DEBUG
from .tools import _REGISTRY


class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]


class IntentRouter:
    """LLM-based intent router using OpenAI-compatible function calling."""

    def __init__(self) -> None:
        self.system_prompt = (
            "You are an intent router. Choose the best function and return JSON only."
        )

    def _post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if DEBUG:
            print("[POST]", payload)
        text = generate(json.dumps(payload))
        try:
            return json.loads(text)
        except Exception:
            return {}

    def route(self, text: str) -> Tuple[str | None, Dict[str, Any], str]:
        tools = [
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": meta["doc"],
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    },
                },
            }
            for name, meta in _REGISTRY.items()
        ]

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": text},
        ]
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "max_tokens": 64,
        }
        try:
            data = self._post(payload)
        except Exception as exc:
            if DEBUG:
                print("[ERROR]", exc)
            return None, {}, "error"

        choice = data.get("choices", [{}])[0]
        finish = choice.get("finish_reason")
        msg = choice.get("message", {})
        if finish == "tool_calls":
            calls = msg.get("tool_calls", [])
            if not calls:
                return None, {}, "unknown"
            call = calls[0]
            name = call.get("function", {}).get("name")
            args_json = call.get("function", {}).get("arguments", "{}")
            try:
                args = json.loads(args_json)
            except json.JSONDecodeError:
                args = {}
            return name, args, name or "unknown"
        content = msg.get("content", "")
        return None, {"content": content}, "chat"
