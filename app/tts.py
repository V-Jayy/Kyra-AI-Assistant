from __future__ import annotations

import asyncio
import hashlib
import logging
from pathlib import Path

from edge_tts import Communicate
import miniaudio
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
    mp3 = _CACHE / f"{h}.mp3"
    if not mp3.exists():
        logger.info("TTS synth %s", mp3)
        comm = Communicate(text, VOICE_NAME, rate=VOICE_RATE)
        await comm.save(str(mp3))
    logger.info("TTS play %s", mp3)
    data = miniaudio.decode_file(str(mp3))
    samples = data.samples.tobytes() if hasattr(data.samples, "tobytes") else data.samples
    play = simpleaudio.play_buffer(
        samples, data.nchannels, data.sample_width, data.sample_rate
    )
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, play.wait_done)
