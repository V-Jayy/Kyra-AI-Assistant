"""Piper TTS wrapper for Kyra assistant."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

try:
    from piper.tts import PiperVoice, Piper
    import sounddevice as sd
    import numpy as np
except Exception:  # pragma: no cover - optional heavy deps
    PiperVoice = None
    Piper = None
    sd = None
    np = None

VOICE_CACHE = Path(os.path.expanduser("~/.cache/kyra/voices"))
VOICE_CACHE.mkdir(parents=True, exist_ok=True)


class PiperTTS:
    """Small wrapper around the piper-tts library."""

    def __init__(self, voice_id: str) -> None:
        self.voice_id = voice_id
        self.voice: Optional[PiperVoice] = None
        if PiperVoice is not None:
            self.voice = self._load_voice()
        else:
            logging.warning("piper-tts not installed; TTS disabled")

    def _load_voice(self) -> Optional[PiperVoice]:
        if PiperVoice is None:
            return None
        model_path = VOICE_CACHE / f"{self.voice_id}.onnx"
        if not model_path.exists():
            url = (
                "https://huggingface.co/rhasspy/piper-voices/resolve/main/" +
                f"en/en_US/{self.voice_id}.onnx"
            )
            try:
                import requests
                resp = requests.get(url, timeout=30)
                resp.raise_for_status()
                model_path.write_bytes(resp.content)
            except Exception as exc:  # pragma: no cover - network failure
                logging.error("Failed to download voice %s: %s", self.voice_id, exc)
                return None
        return PiperVoice.load(model_path)

    def speak(self, text: str) -> None:
        """Speak text synchronously."""
        if self.voice is None or Piper is None or sd is None:
            logging.info("TTS disabled: %s", text)
            return
        tts = Piper(self.voice)
        data = tts.synthesize(text)
        audio = np.frombuffer(data, dtype=np.int16)
        sd.play(audio, 24000)
        sd.wait()

