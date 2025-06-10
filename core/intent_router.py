from __future__ import annotations

import json
from typing import Any, Dict, Tuple

import logging
import time
import requests
from requests.exceptions import RequestException
from pydantic import BaseModel
from jsonschema import ValidationError

import os

from .config import MODEL_NAME, DEBUG
from .tools import _REGISTRY, get_openai_tools, validate_tool_args
import re


class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]


class IntentRouter:
    """LLM-based intent router using OpenAI-compatible function calling."""

    def __init__(self) -> None:
        self.system_prompt = (
            "You are an intent\u2011router for a local voice assistant.\n\n"
            "Respond with **ONLY** a JSON object like one of these \u2014 no prose, no markdown:\n\n"
            "{ \"function\": null }\n\n"
            "or\n\n"
            "{\n  \"function\": {\n    \"name\": \"<one_of_the_function_names_provided>\",\n    \"arguments\": { /* every required parameter */ }\n  }\n}"
        )
        base = [t for t in get_openai_tools() if t.get("function", {}).get("name") != "play_music"]
        base.append(
            {
                "type": "function",
                "function": {
                    "name": "play_music",
                    "description": "Play a song, playlist, or stream in the default browser.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "A direct media URL (YouTube, Spotify, SoundCloud, etc.)",
                            },
                            "query": {
                                "type": "string",
                                "description": "A free-text search term if the user did not supply a URL",
                            },
                        },
                        "required": ["url"],
                    },
                },
            }
        )
        self.tools = base
        self.logger = logging.getLogger(__name__)

    def _post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if DEBUG:
            print("[POST]", payload)

        openai_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("API_BASE_URL") or (
            "https://api.openai.com" if openai_key else "http://localhost:11434"
        )
        endpoint = "/v1/chat/completions"
        url = f"{api_base}{endpoint}"

        headers = {"Content-Type": "application/json"}
        if openai_key:
            headers["Authorization"] = f"Bearer {openai_key}"

        start = time.time()
        resp = requests.post(url, json=payload, timeout=4, headers=headers)
        latency = (time.time() - start) * 1000
        self.logger.info("llm_request", extra={"latency_ms": int(latency)})
        if resp.status_code >= 400:
            raise RuntimeError(f"LLM error {resp.status_code}: {resp.text}")
        return resp.json()

    def route(self, text: str) -> Tuple[str | None, Dict[str, Any], str]:
        if m := re.search(r"(https?://\S+)", text):
            return "open_website", {"url": m.group(1)}, "open_website"

        fallback: Tuple[str, Dict[str, Any]] | None = None
        if text.lower().startswith("play "):
            fallback = ("play_music", {"url": None, "query": text[5:].strip()})

        tools = self.tools

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
        except RequestException as exc:
            self.logger.error("llm_request_failed", extra={"error": str(exc)})
            if fallback:
                name, args = fallback
                return name, args, name
            return None, {"error": str(exc)}, "error"

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
            try:
                validate_tool_args(name or "", args)
            except ValidationError as exc:
                self.logger.warning(
                    "schema_validation_failed",
                    extra={"tool": name, "error": exc.message},
                )
                return None, {"error": exc.message}, "error"
            return name, args, name or "unknown"
        content = msg.get("content", "")
        return None, {"content": content}, "chat"
