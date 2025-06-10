import argparse
import asyncio
import json
import logging
import os
from typing import Any

from vosk import KaldiRecognizer, Model

from .stt import speech_chunks
from .router import Router
from .tts import speak, set_voice
from .nlu import normalize

logging.basicConfig(
    filename="assistant.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
)


class Logger:
    def __init__(self, debug: bool = False):
        self.debug = debug
        try:
            from colorama import Fore, Style

            self.colors = {
                "USER": Fore.CYAN,
                "NORM": Fore.MAGENTA,
                "NLU": Fore.YELLOW,
                "CALL": Fore.GREEN,
                "RESP": Fore.BLUE,
                "ERR": Fore.RED,
            }
            self.reset = Style.RESET_ALL
        except Exception:  # pragma: no cover - colorama optional
            self.colors = {t: "" for t in ["USER", "NORM", "NLU", "CALL", "RESP", "ERR"]}
            self.reset = ""

    def log(self, tag: str, message: str) -> None:
        if not self.debug:
            return
        color = self.colors.get(tag, "")
        print(f"[{tag:4}] {color}{message}{self.reset}")


WAKE_WORD = "hey luna"
MODEL_PATH = "vosk-model-small-en-us-0.15"


async def load_stt() -> KaldiRecognizer:
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Vosk model not found at {MODEL_PATH}. Download from https://alphacephei.com/vosk/models"
        )
    model = Model(MODEL_PATH)
    return KaldiRecognizer(model, 16000)


async def handle_command(text: str, router: Router, tts_enabled: bool, logger: Logger) -> None:
    norm = normalize(text)
    fn, args, intent, conf = router.select(text)
    logger.log("NORM", f'"{norm}"')
    logger.log("NLU", f"intent={intent}, args={args}, conf={conf:.2f}")
    if fn:
        ok, msg = fn(**args)
        status = "\u2713" if ok else "x"
        logger.log("CALL", f"actions.{fn.__name__}({args}) -> {status} {msg}")
        speak(msg, tts_enabled)
        if not ok:
            logger.log("ERR", msg)
    else:
        resp = "I'm sorry, I didn't understand."  # placeholder response
        logger.log("RESP", resp)
        speak(resp, tts_enabled)


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--mic_index", type=int, default=None)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--voice", default="en-us-kathleen-low")
    args = parser.parse_args()

    logger = Logger(debug=args.debug)
    set_voice(args.voice)
    router = Router()
    recognizer = await load_stt()

    gen = speech_chunks(args.mic_index)
    state = "wake"
    async for chunk in gen:
        if recognizer.AcceptWaveform(chunk):
            res = json.loads(recognizer.Result())
            text = res.get("text", "").lower()
            if args.debug and text:
                print("STT:", text)
            if state == "wake" and text.startswith(WAKE_WORD):
                speak("I'm listening", not args.headless)
                state = "command"
            elif state == "command" and text:
                logger.log("USER", text)
                await handle_command(text, router, not args.headless, logger)
                state = "wake"


if __name__ == "__main__":
    asyncio.run(main())
