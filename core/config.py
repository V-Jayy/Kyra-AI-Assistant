"""Basic runtime configuration loaded from ``config.json`` if present."""

import json
import os

LLM_BASE_URL = "http://localhost:11434/v1/chat"
MODEL_NAME = "mistral:7b-instruct"

_DEFAULT = {
    "wake_word": "Hey Aurora",
    "debug": True,
    "tts_engine": "piper",
    "conversational_mode": True,
}

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.json")

try:  # pragma: no cover - file may not exist in tests
    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        _USER = json.load(f)
except Exception:
    _USER = {}

_CONFIG = {**_DEFAULT, **_USER}

WAKE_WORD: str = _CONFIG.get("wake_word", _DEFAULT["wake_word"])
DEBUG: bool = bool(_CONFIG.get("debug", _DEFAULT["debug"]))
TTS_ENGINE: str = _CONFIG.get("tts_engine", _DEFAULT["tts_engine"])
CONVERSATIONAL_MODE: bool = bool(
    _CONFIG.get("conversational_mode", _DEFAULT["conversational_mode"])
)

__all__ = [
    "LLM_BASE_URL",
    "MODEL_NAME",
    "WAKE_WORD",
    "DEBUG",
    "TTS_ENGINE",
    "CONVERSATIONAL_MODE",
]
