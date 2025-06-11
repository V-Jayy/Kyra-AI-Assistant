from __future__ import annotations

import os
from tempfile import NamedTemporaryFile

try:
    import pyttsx3
except ImportError:  # pragma: no cover
    pyttsx3 = None

try:
    from gtts import gTTS
    from playsound import playsound
except Exception:  # pragma: no cover
    gTTS = None
    playsound = None


def speak(text: str) -> None:
    """Speak *text* using gTTS or pyttsx3 as fallback."""
    text = (text or "").strip()
    if not text:
        return

    if gTTS and playsound:
        try:
            tts_obj = gTTS(text)
            with NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                tts_obj.save(f.name)
            try:
                playsound(f.name)
            finally:
                os.remove(f.name)
            return
        except Exception as e:
            print(f"TTS failed: {e}")

    if pyttsx3:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
