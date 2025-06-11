from __future__ import annotations

import asyncio
import logging
import os
from tempfile import NamedTemporaryFile

from edge_tts import Communicate

try:  # pragma: no cover - optional dep
    import pyttsx3
except Exception:  # pragma: no cover - environment may lack engines
    pyttsx3 = None

from .constants import VOICE, TTS_FALLBACK, DEBUG

logger = logging.getLogger(__name__)


async def _edge_play(text: str, voice: str) -> None:
    communicate = Communicate(text, voice)
    with NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        await communicate.save(f.name)
        path = f.name
    if os.name == "nt":
        os.startfile(path)  # type: ignore[attr-defined]
    elif os.system(f"which xdg-open > /dev/null 2>&1") == 0:
        asyncio.create_subprocess_exec("xdg-open", path)
    elif os.system(f"which afplay > /dev/null 2>&1") == 0:
        await asyncio.create_subprocess_exec("afplay", path)
    else:
        logger.warning("No audio player available to play %s", path)
    await asyncio.sleep(0)  # let playback start


async def _pyttsx3_play(text: str) -> None:
    if pyttsx3 is None:  # pragma: no cover - optional
        raise RuntimeError("pyttsx3 unavailable")
    engine = pyttsx3.init()
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, engine.say, text)
    await loop.run_in_executor(None, engine.runAndWait)


async def safe_speak(text: str) -> None:
    text = (text or "").strip()
    if text == "":
        raise ValueError("empty utterance")

    async def _run() -> None:
        if DEBUG:
            logger.debug("TTS: %s", text)
        try:
            await _edge_play(text, VOICE)
            return
        except Exception as exc:
            logger.warning("edge-tts failed: %s", exc)
            if not TTS_FALLBACK:
                return
        if pyttsx3:
            try:
                await _pyttsx3_play(text)
            except Exception as exc:  # pragma: no cover
                logger.error("pyttsx3 failed: %s", exc)

    asyncio.create_task(_run())
