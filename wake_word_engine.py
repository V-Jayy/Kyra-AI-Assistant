"""Simple pvporcupine wake word detector."""

from __future__ import annotations

import pvporcupine


class WakeWordEngine:
    """Detect a wake word in audio frames."""

    def __init__(self, wake_word: str = "nova") -> None:
        self._porcupine = pvporcupine.create(keywords=[wake_word])

    def detect(self, frame: bytes) -> bool:
        """Return True if the wake word is detected."""
        pcm = memoryview(frame).cast("h")
        return self._porcupine.process(pcm) >= 0
