import argparse
import asyncio
import json
import logging
import os

from vosk import KaldiRecognizer, Model

from .stt import speech_chunks
from .router import Router
from .tts import speak, set_voice

logging.basicConfig(
    filename="assistant.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
)

WAKE_WORD = "hey luna"
MODEL_PATH = "vosk-model-small-en-us-0.15"


async def load_stt() -> KaldiRecognizer:
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Vosk model not found at {MODEL_PATH}. Download from https://alphacephei.com/vosk/models"
        )
    model = Model(MODEL_PATH)
    return KaldiRecognizer(model, 16000)


async def handle_command(text: str, router: Router, tts_enabled: bool) -> None:
    tool_fn, kwargs = router.select(text)
    ok, msg = tool_fn(**kwargs)
    speak(msg, tts_enabled)
    if not ok:
        logging.error("Action failed: %s", msg)


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--mic_index", type=int, default=None)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--voice", default="en-us-kathleen-low")
    args = parser.parse_args()

    set_voice(args.voice)
    router = Router()
    recognizer = await load_stt()

    gen = speech_chunks(args.mic_index)
    state = "wake"
    command_text = ""
    async for chunk in gen:
        if recognizer.AcceptWaveform(chunk):
            res = json.loads(recognizer.Result())
            text = res.get("text", "").lower()
            if args.debug and text:
                print("\rSTT:", text, flush=True)
            if state == "wake" and text.startswith(WAKE_WORD):
                speak("I'm listening", not args.headless)
                state = "command"
            elif state == "command" and text:
                command_text = text
                await handle_command(command_text, router, not args.headless)
                state = "wake"
        elif args.debug:
            pres = json.loads(recognizer.PartialResult())
            partial = pres.get("partial", "")
            if partial:
                print("\rSTT (partial):", partial, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
