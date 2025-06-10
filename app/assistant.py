from __future__ import annotations

import argparse
import asyncio
import json
import os
from typing import AsyncGenerator, Optional, Dict, Any

from gtts import gTTS
from tempfile import NamedTemporaryFile
import pyaudio
from playsound import playsound
from vosk import Model, KaldiRecognizer
import logging
import re
import urllib.parse
import webbrowser
import requests

from core.config import DEBUG, WAKE_WORD, TTS_ENGINE
from core.intent_router import IntentRouter
from core.transcript import Transcript

from core.tools import _REGISTRY, tool, _TOOL_SCHEMA_MAP
from core.dispatcher import match_intent

ROUTER_PROMPT = """
You are an intent‑router for a local voice assistant.

Respond with **ONLY** a JSON object like one of these — no prose, no markdown:

{ "function": null }

or

{
  "function": {
    "name": "<one_of_the_function_names_provided>",
    "arguments": { /* every required parameter */ }
  }
}
"""


logger = logging.getLogger(__name__)


@tool
def play_music(url: str | None = None, query: str | None = None) -> tuple[bool, str]:
    """Play a song, playlist or stream in the default browser."""
    if not url and query:
        q = urllib.parse.quote_plus(query)
        search_url = f"https://www.youtube.com/results?search_query={q}"
        try:
            resp = requests.get(search_url, timeout=5)
            m = re.search(r"/watch\?v=([\w-]{11})", resp.text)
            if m:
                url = f"https://www.youtube.com/watch?v={m.group(1)}"
            else:
                url = search_url
        except Exception:
            url = search_url
    if url:
        try:
            webbrowser.open(url)
            return True, f"Playing {query or url}"
        except Exception as exc:  # pragma: no cover - platform dependent
            return False, str(exc)
    return False, "No URL provided"

_TOOL_SCHEMA_MAP["play_music"] = {
    "type": "object",
    "properties": {
        "url": {
            "type": "string",
            "description": "A direct media URL (YouTube, Spotify, SoundCloud, etc.)",
        },
        "query": {
            "type": "string",
            "description": "A free-text search term if the user did not supply a URL",
        },
    },
    "required": ["url"],
}


def _safe_json_load(raw: str) -> Dict[str, Any] | None:
    """
    Try to extract and load the first JSON object found in *raw*.
    Returns None on failure.
    """
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.S)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                return None
    return None


def summarise_router_reply(reply: str | Dict[str, Any]) -> tuple[str | None, Dict[str, Any]]:
    """Return (function_name, arguments) from *reply* without raising."""
    if isinstance(reply, dict):
        obj = reply
    else:
        obj = _safe_json_load(reply) or {}

    name: str | None = None
    args: Dict[str, Any] = {}

    func = obj.get("function")

    if isinstance(func, dict):
        name = func.get("name")
        raw_args = func.get("arguments", {})
        if isinstance(raw_args, str):
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                args = {}
        elif isinstance(raw_args, dict):
            args = raw_args
    elif isinstance(func, str):
        name = func
        raw_args = obj.get("arguments", {})
        if isinstance(raw_args, dict):
            args = raw_args
    return name, args


async def microphone_chunks() -> AsyncGenerator[bytes, None]:
    q: asyncio.Queue[bytes] = asyncio.Queue()
    loop = asyncio.get_running_loop()

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
            asyncio.run_coroutine_threadsafe(q.put(data), loop)

    import threading

    threading.Thread(target=_worker, daemon=True).start()
    while True:
        data = await q.get()
        yield data


def speak(text: str, enable: bool) -> None:
    text = (text or "").strip()
    if not text:
        logger.info("Empty reply – nothing to speak.")
        return

    if enable:
        try:
            tts_obj = gTTS(text)
        except AssertionError as e:
            logger.error(
                "TTS failed: %s",
                e,
                exc_info=logger.isEnabledFor(logging.DEBUG),
            )
            return
        with NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            tts_obj.save(f.name)
        playsound(f.name)
        os.remove(f.name)
    else:
        print(f"Assistant: {text}")


def handle_text(text: str, router: IntentRouter, tts: bool, transcript: Transcript) -> None:
    """Map *text* to a tool either via local rules or the LLM."""
    name, args = match_intent(text)
    if name and name in _REGISTRY:
        if DEBUG:
            logger.info("Mapped input '%s' to '%s' with %s", text, name, args)
        ok, msg = _REGISTRY[name]["callable"](**args)
        transcript.log("BOT", msg)
        speak(msg, tts)
        return

    name, args_route, _ = router.route(text)
    if name and name in _REGISTRY:
        ok, msg = _REGISTRY[name]["callable"](**args_route)
        transcript.log("BOT", msg)
        speak(msg, tts)
    else:
        reply = args_route.get("content", "I didn't understand")
        transcript.log("BOT", reply)
        speak(reply, tts)


async def voice_loop(
    router: IntentRouter, model_path: str, tts: bool, transcript: Transcript
) -> None:
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Vosk model missing at {model_path}")
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)
    transcript.log("BOT", "Ready")
    async for chunk in microphone_chunks():
        if recognizer.AcceptWaveform(chunk):
            res = json.loads(recognizer.Result())
            text = res.get("text", "")
            if not text:
                continue
            transcript.log("USER", text)
            if text.lower().startswith(WAKE_WORD.lower()):
                speak("I'm listening", tts)
                continue
            handle_text(text, router, tts, transcript)


async def console_loop(router: IntentRouter, transcript: Transcript) -> None:
    while True:
        text = input("You: ")
        if not text:
            continue
        transcript.log("USER", text)
        handle_text(text, router, False, transcript)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["voice", "text"],
        default="voice",
    )
    parser.add_argument("--model-path", default="vosk-model-small-en-us-0.15")
    parser.add_argument("text", nargs="*", help="Optional one-shot command")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)

    transcript = Transcript(DEBUG)
    router = IntentRouter()
    router.system_prompt = ROUTER_PROMPT

    if args.text:
        query = " ".join(args.text)
        name, params, _ = router.route(query)
        if name and name in _REGISTRY:
            ok, msg = _REGISTRY[name]["callable"](**params)
            transcript.log("BOT", msg)
            speak(msg, False)
        else:
            reply = params.get("content", "I didn't understand")
            transcript.log("BOT", reply)
            speak(reply, False)
        return

    if args.mode == "voice":
        asyncio.run(voice_loop(router, args.model_path, True, transcript))
    else:
        asyncio.run(console_loop(router, transcript))


if __name__ == "__main__":
    main()
