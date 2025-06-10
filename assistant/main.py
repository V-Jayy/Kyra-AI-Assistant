import argparse
import asyncio
import json
import logging
import os
import yaml

from vosk import KaldiRecognizer, Model

from .stt import speech_chunks
from .router import Router
from tts import PiperTTS

logging.basicConfig(
    filename="assistant.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
)

CONFIG_FILE = "config.yaml"
WAKE_WORD = "hey luna"
VOICE_ID = "en_US-amy-high"
MODEL_PATH = "vosk-model-small-en-us-0.15"


async def load_stt() -> KaldiRecognizer:
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Vosk model not found at {MODEL_PATH}. Download from https://alphacephei.com/vosk/models"
        )
    model = Model(MODEL_PATH)
    return KaldiRecognizer(model, 16000)


async def handle_command(text: str, router: Router, tts: PiperTTS, tts_enabled: bool) -> None:
    """Execute tool for the recognized text and speak the result."""
    tool_fn, kwargs = router.select(text)
    ok, msg = tool_fn(**kwargs)
    if tts_enabled:
        tts.speak(msg)
    else:
        print(f"Assistant: {msg}")
    if not ok:
        logging.error("Action failed: %s", msg)


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--mic_index", type=int, default=None)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--voice", default=None)
    args = parser.parse_args()

    config: dict = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

    voice_id = args.voice or config.get("tts_voice", VOICE_ID)
    wake_word = config.get("wake_word", WAKE_WORD)
    debug = args.debug or config.get("debug", False)

    tts = PiperTTS(voice_id)
    router = Router()
    recognizer = await load_stt()

    gen = speech_chunks(args.mic_index)
    state = "wake"
    command_text = ""
    async for chunk in gen:
        if recognizer.AcceptWaveform(chunk):
            res = json.loads(recognizer.Result())
            text = res.get("text", "").lower()
            if debug and text:
                print("STT:", text)
            if state == "wake" and text.startswith(wake_word):
                if not args.headless:
                    tts.speak("I'm listening")
                else:
                    print("I'm listening")
                state = "command"
            elif state == "command" and text:
                command_text = text
                await handle_command(command_text, router, tts, not args.headless)
                state = "wake"


if __name__ == "__main__":
    asyncio.run(main())
