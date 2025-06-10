import json
import os
from typing import Callable, Tuple, Dict, Any

from . import actions
from .nlu import normalize
from .tools import _REGISTRY

try:
    from llama_cpp import Llama
except ImportError:  # pragma: no cover - optional heavy dep
    Llama = None


class Router:
    """Simple tool selection using an optional local Llama model."""

    def __init__(self, capabilities_path: str = "capabilities.json", model_path: str | None = None):
        with open(capabilities_path, "r", encoding="utf-8") as f:
            self.capabilities = json.load(f)
        if model_path and os.path.exists(model_path) and Llama is not None:
            self.llm = Llama(model_path=model_path, n_gpu_layers=32)
        else:
            self.llm = None

    def _llm_select(self, text: str) -> Tuple[str, Dict[str, Any]]:
        tools_json = json.dumps(self.capabilities, indent=2)
        prompt = (
            "SYSTEM:\nYou are CommandRouter v2. Decide which tool (from TOOLS) best fulfils\n"
            "the USER request. Respond only with valid JSON:\n"
            "{\"tool\": \"<tool_name>\", \"args\": {<arg>: <value>}}\n\n"
            f"TOOLS:\n{tools_json}\n\nUSER: \"{text}\"\n"
        )
        output = self.llm(prompt, stop=["\n"])["choices"][0]["text"].strip()
        try:
            data = json.loads(output)
            return data.get("tool"), data.get("args", {})
        except Exception:
            return "", {}

    def _heuristic_select(self, text: str) -> Tuple[str, Dict[str, Any]]:
        text = text.lower()
        if "download" in text:
            return "reveal_folder", {"path": os.path.expandvars("%USERPROFILE%/Downloads")}
        if "youtube" in text:
            return "open_website", {"url": "youtube.com"}
        if "open" in text and "website" in text:
            return "open_website", {"url": text.split()[-1]}
        return "", {}

    def select(self, text: str) -> Tuple[Callable[..., Tuple[bool, str]], Dict[str, Any]]:
        text = normalize(text)
        if self.llm:
            tool_name, args = self._llm_select(text)
        else:
            tool_name, args = self._heuristic_select(text)
        fn = _REGISTRY.get(tool_name, {}).get("callable")
        if fn is None:
            return actions.open_website, {"url": text}
        return fn, args
