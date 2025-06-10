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


class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]


class IntentRouter:
    """LLM-based intent router using OpenAI-compatible function calling."""

    def __init__(self) -> None:
        self.system_prompt = (
            "You are an intent router. Choose the best function and return JSON only."
        )
        self.tools = get_openai_tools()
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
