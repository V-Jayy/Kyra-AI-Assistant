from __future__ import annotations

import argparse
import asyncio
import json
import os
from typing import AsyncGenerator

import pyttsx3
import pyaudio
from vosk import Model, KaldiRecognizer

from core.config import DEBUG, WAKE_WORD
from core.intent_router import IntentRouter
from core.transcript import Transcript
from core.tools import _REGISTRY


async def microphone_chunks() -> AsyncGenerator[bytes, None]:
    q = asyncio.Queue()

    def _worker() -> None:
        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=8000,
        )
        stream.start_stream()
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            asyncio.run_coroutine_threadsafe(q.put(data), asyncio.get_event_loop())

    import threading

    threading.Thread(target=_worker, daemon=True).start()
    while True:
        data = await q.get()
        yield data


def speak(text: str, engine: pyttsx3.Engine, enable: bool) -> None:
    if enable:
        engine.say(text)
        engine.runAndWait()
    else:
        print(f"Assistant: {text}")


async def voice_loop(
    router: IntentRouter, model_path: str, tts: bool, transcript: Transcript
) -> None:
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Vosk model missing at {model_path}")
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)
    engine = pyttsx3.init()

    transcript.log("BOT", "Ready")
    async for chunk in microphone_chunks():
        if recognizer.AcceptWaveform(chunk):
            res = json.loads(recognizer.Result())
            text = res.get("text", "")
            if not text:
                continue
            transcript.log("USER", text)
            if text.lower().startswith(WAKE_WORD.lower()):
                speak("I'm listening", engine, tts)
                continue
            name, args, _ = router.route(text)
            if name and name in _REGISTRY:
                ok, msg = _REGISTRY[name]["callable"](**args)
                transcript.log("BOT", msg)
                speak(msg, engine, tts)
            else:
                reply = args.get("content", "I didn't understand")
                transcript.log("BOT", reply)
                speak(reply, engine, tts)


async def console_loop(router: IntentRouter, transcript: Transcript) -> None:
    engine = pyttsx3.init()
    while True:
        text = input("You: ")
        if not text:
            continue
        transcript.log("USER", text)
        name, args, _ = router.route(text)
        if name and name in _REGISTRY:
            ok, msg = _REGISTRY[name]["callable"](**args)
            transcript.log("BOT", msg)
            speak(msg, engine, False)
        else:
            reply = args.get("content", "I didn't understand")
            transcript.log("BOT", reply)
            speak(reply, engine, False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["voice", "console"], default="voice")
    parser.add_argument("--model-path", default="vosk-model-small-en-us-0.15")
    args = parser.parse_args()

    transcript = Transcript(DEBUG)
    router = IntentRouter()

    if args.mode == "voice":
        asyncio.run(voice_loop(router, args.model_path, True, transcript))
    else:
        asyncio.run(console_loop(router, transcript))


if __name__ == "__main__":
    main()
