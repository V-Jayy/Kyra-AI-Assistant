from __future__ import annotations

import os
from typing import Any, Dict

import yaml

_DEFAULT = {
    "wake_word": "kyra",
    "voice": "en-US-AriaNeural",
    "tts_fallback": True,
    "debug": True,
    "vosk_model_path": "vosk-model-small-en-us-0.15",
}

_DEFAULT_HOME = os.path.join(os.path.expanduser("~"), ".kyra")
_CONFIG_PATH = os.path.expanduser(
    os.getenv("KYRA_CONFIG", os.path.join(_DEFAULT_HOME, "config.yaml"))
)


def _load_config() -> Dict[str, Any]:
    if not os.path.exists(_CONFIG_PATH):
        os.makedirs(os.path.dirname(_CONFIG_PATH), exist_ok=True)
        with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump(_DEFAULT, f)
        return _DEFAULT.copy()
    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f) or {}
        except Exception:
            data = {}
    cfg = {**_DEFAULT, **data}
    return cfg


_CFG = _load_config()

WAKE_WORD: str = _CFG.get("wake_word", _DEFAULT["wake_word"])
VOICE: str = _CFG.get("voice", _DEFAULT["voice"])
TTS_FALLBACK: bool = bool(_CFG.get("tts_fallback", _DEFAULT["tts_fallback"]))
DEBUG: bool = bool(_CFG.get("debug", _DEFAULT["debug"]))
VOSK_MODEL_PATH: str = _CFG.get("vosk_model_path", _DEFAULT["vosk_model_path"])

__all__ = [
    "WAKE_WORD",
    "VOICE",
    "TTS_FALLBACK",
    "DEBUG",
    "VOSK_MODEL_PATH",
]
