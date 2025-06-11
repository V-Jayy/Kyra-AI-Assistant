from __future__ import annotations

import asyncio
import logging
import os
from tempfile import NamedTemporaryFile

from edge_tts import Communicate

try:  # pragma: no cover - optional dep
    from piper import PiperVoice  # type: ignore
    import sounddevice as sd  # type: ignore
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover - environment may lack engines
    PiperVoice = None
    sd = None
    np = None

try:  # pragma: no cover - optional
    import comtypes.client as cc
except Exception:
    cc = None


from .constants import VOICE, TTS_FALLBACK, DEBUG, PIPER_MODEL_PATH

logger = logging.getLogger(__name__)


async def _edge_play(text: str, voice: str) -> None:
    communicate = Communicate(text, voice)
    with NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        await communicate.save(f.name)
        path = f.name
    if not os.path.exists(path):
        logger.error("TTS output missing: %s", path)
        return
    if os.name == "nt":
        os.startfile(path)  # type: ignore[attr-defined]
    elif os.system(f"which xdg-open > /dev/null 2>&1") == 0:
        asyncio.create_subprocess_exec("xdg-open", path)
    elif os.system(f"which afplay > /dev/null 2>&1") == 0:
        await asyncio.create_subprocess_exec("afplay", path)
    else:
        logger.warning("No audio player available to play %s", path)
    await asyncio.sleep(0)  # let playback start


async def _sapi_play(text: str) -> None:
    if cc is None:  # pragma: no cover - optional
        raise RuntimeError("comtypes unavailable")
    speaker = cc.CreateObject("SAPI.SpVoice")
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, speaker.Speak, text)


async def _piper_play(text: str, model_path: str) -> None:
    if PiperVoice is None or sd is None or np is None:  # pragma: no cover - optional
        raise RuntimeError("piper-tts unavailable")
    loop = asyncio.get_running_loop()
    try:
        voice = await loop.run_in_executor(None, PiperVoice.load, model_path)
    except Exception as exc:
        raise RuntimeError(f"model load failed: {exc}")
    audio = await loop.run_in_executor(None, voice.speak, text)
    await loop.run_in_executor(None, sd.play, np.array(audio), voice.config.sample_rate)
    await loop.run_in_executor(None, sd.wait)


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
        if os.name == "nt":
            try:
                await _sapi_play(text)
                return
            except Exception as exc:  # pragma: no cover - windows only
                logger.error("sapi failed: %s", exc)
        if PiperVoice and sd and np:
            try:
                await _piper_play(text, PIPER_MODEL_PATH)
                return
            except Exception as exc:  # pragma: no cover
                logger.error("piper playback failed: %s", exc)

    asyncio.create_task(_run())
