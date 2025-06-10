import argparse
import asyncio
import json
import logging
import os
from typing import Dict

from vosk import KaldiRecognizer, Model

from .stt import speech_chunks
from .nlu import load_commands, NLU
from .actions import dispatch
from .tts import speak

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


async def handle_command(text: str, nlu: NLU, tts_enabled: bool) -> None:
    intent, slots, _conf = nlu.predict(text)
    if not intent:
        speak("Sorry, I didn't understand.", tts_enabled)
        return
    cmd = next(c for c in nlu.commands if c.id == intent)
    args: Dict[str, str] = {}
    for k, v in cmd.args.items():
        if isinstance(v, dict):
            slot_val = slots.get(k)
            if slot_val:
                mapped = v.get(slot_val)
                if mapped:
                    args[k] = os.path.expandvars(mapped)
        else:
            args[k] = os.path.expandvars(v.format(**slots))
    ok, msg = dispatch(cmd.action, **args)
    speak(msg, tts_enabled)
    if not ok:
        logging.error("Action failed: %s", msg)


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--mic_index", type=int, default=None)
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    commands = load_commands(os.path.join(os.path.dirname(__file__), "commands.yml"))
    nlu = NLU(commands)
    recognizer = await load_stt()

    gen = speech_chunks(args.mic_index)
    state = "wake"
    command_text = ""
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
                command_text = text
                await handle_command(command_text, nlu, not args.headless)
                state = "wake"


if __name__ == "__main__":
    asyncio.run(main())
