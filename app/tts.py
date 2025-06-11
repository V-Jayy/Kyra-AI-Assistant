from __future__ import annotations

import asyncio
import hashlib
import logging
from pathlib import Path

from edge_tts import Communicate
import simpleaudio

from .config import VOICE_NAME, VOICE_RATE, AUDIO_CACHE

logger = logging.getLogger(__name__)

_CACHE = Path(AUDIO_CACHE)
_CACHE.mkdir(exist_ok=True)


async def speak(text: str) -> None:
    """Synthesize *text* with Edge TTS and play it back."""
    text = (text or "").strip()
    if not text:
        return
    h = hashlib.sha1(text.encode("utf-8")).hexdigest()
    path = _CACHE / f"{h}.wav"
    if not path.exists():
        logger.info("TTS synth %s", path)
        comm = Communicate(text, VOICE_NAME, rate=VOICE_RATE)
        await comm.save(str(path))
    logger.info("TTS play %s", path)
    wave = simpleaudio.WaveObject.from_wave_file(str(path))
    play = wave.play()
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, play.wait_done)
