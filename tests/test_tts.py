import asyncio
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.tts import speak


def test_speak_runs():
    asyncio.run(speak("This is only a test."))
