from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import time
from typing import AsyncGenerator, Optional, Dict, Any

from app.tts import speak as tts_speak
from vosk import Model, KaldiRecognizer
import logging
import re
import urllib.parse
import webbrowser
import requests

from app.constants import (
    DEBUG,
    CONVERSATIONAL_MODE,
    WAKE_WORD,
    WAKE_WORD_ALIASES,
    VOSK_MODEL_PATH,
)

if not DEBUG:
    os.environ.setdefault("VOSK_LOG_LEVEL", "-1")
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("gtts").setLevel(logging.WARNING)
from core.intent_router import IntentRouter
from core.transcript import Transcript
from app.config import VOICE_NAME, VOICE_RATE

from core.tools import _REGISTRY, tool, _TOOL_SCHEMA_MAP
from app.intent_router import fuzzy_match, Action

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
    if url is None and query:
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
    "required": [],
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


def summarise_router_reply(reply: str | Dict[str, Any]) -> str:
    """Return a short spoken confirmation for a router reply."""
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

    if not name:
        return ""
    if name == "open_website" and "url" in args:
        return f"Opening {args['url']}"
    if name == "launch_app" and "app" in args:
        return f"Launching {args['app']}"
    if name == "play_music":
        q = args.get("query") or args.get("url", "")
        return f"Playing {q}".strip()
    if name == "download_app" and "package" in args:
        return f"Downloading {args['package']}"
    if name == "kill_process" and "name" in args:
        return f"Killing {args['name']}"
    if name == "open_explorer" and "path" in args:
        return f"Opening {args['path']}"
    if name == "create_note" and "content" in args:
        return "Saved note"
    return name


def _fix_wake_word(text: str) -> str:
    """Normalize common mis-hearings of the wake word."""
    aliases = "|".join(re.escape(w) for w in WAKE_WORD_ALIASES)
    pattern = rf"\b(?:{aliases})\b"
    return re.sub(pattern, WAKE_WORD, text, flags=re.I)


_STOP_WORDS = re.compile(
    r"^(?:the|a|an|process|explorer(?: to)?|explore(?: to)?)\s+", re.I
)


def _clean_arg(arg: str) -> str:
    return _STOP_WORDS.sub("", arg.strip())


_SMALL_TALK = [
    (re.compile(r"\b(?:are you there\??|can we talk\??|just chat with me)\b", re.I), [
        "Sure, I'm here.",
        "Yes, I'm listening!",
    ]),
]

_CASUAL_FALLBACKS = [
    "Sure, I'm here.",
    "Yes, I'm listening!",
    "Let's just chat.",
    "I'm here if you need me.",
]


async def microphone_chunks() -> AsyncGenerator[bytes, None]:
    q: asyncio.Queue[bytes] = asyncio.Queue()
    loop = asyncio.get_running_loop()

    def _worker() -> None:
        import pyaudio
        pa = pyaudio.PyAudio()
        try:
            stream = pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=8000,
            )
        except Exception as e:
            print(f"Microphone error: {e}")
            return
        stream.start_stream()
        while True:
            try:
                data = stream.read(4000, exception_on_overflow=False)
            except OSError as exc:
                logger.error(
                    "Mic read failed: %s. Check device index or reinitialise audio input.",
                    exc,
                )
                try:
                    stream.stop_stream()
                    stream.close()
                    stream = pa.open(
                        format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        frames_per_buffer=8000,
                    )
                    stream.start_stream()
                except Exception as exc2:
                    logger.error("Reopening mic failed: %s", exc2)
                    time.sleep(1)
                    continue
                continue
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
        asyncio.create_task(tts_speak(text))
    else:
        print(f"Assistant: {text}")


def handle_text(text: str, router: IntentRouter, tts: bool, transcript: Transcript) -> None:
    """Map *text* to a tool either via fuzzy rules or the LLM."""
    for pattern, replies in _SMALL_TALK:
        if pattern.search(text):
            resp = random.choice(replies)
            transcript.log("BOT", resp)
            speak(resp, tts)
            return
    act = fuzzy_match(text)
    if act:
        if act.name == "repeat":
            resp = random.choice(_CASUAL_FALLBACKS)
            transcript.log("BOT", resp)
            speak(resp, tts)
            return
        if act.name in _REGISTRY:
            if act.name == "kill_process":
                act.args["name"] = _clean_arg(act.args.get("name", ""))
            if act.name == "open_website":
                act.args["url"] = _clean_arg(act.args.get("url", ""))
            if act.name == "open_explorer":
                act.args["path"] = _clean_arg(act.args.get("path", ""))
            if DEBUG:
                transcript.log("FUNC", f"{act.name} {act.args} | raw='{text}'")
            ok, msg = _REGISTRY[act.name]["callable"](**act.args)
            transcript.log("BOT", msg)
            speak(msg, tts)
            return

    name, args_route, intent = router.route(text)
    if DEBUG:
        transcript.log("INTENT", intent)
    if name and name in _REGISTRY:
        if name == "kill_process":
            args_route["name"] = _clean_arg(args_route.get("name", ""))
        if name == "open_website":
            args_route["url"] = _clean_arg(args_route.get("url", ""))
            if not args_route["url"]:
                name = None
        if name == "open_explorer":
            args_route["path"] = _clean_arg(args_route.get("path", ""))
        if name and DEBUG:
            transcript.log("FUNC", f"{name} {args_route} | raw='{text}'")
        if name:
            ok, msg = _REGISTRY[name]["callable"](**args_route)
            transcript.log("BOT", msg)
            speak(msg, tts)
            return
    else:
        reply = args_route.get("content")
        if not reply and CONVERSATIONAL_MODE:
            reply = random.choice(_CASUAL_FALLBACKS)
        elif not reply:
            reply = "I didn't understand"
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
    last_voice = time.monotonic()
    awaiting = False
    buffer = ""
    last_part = ""
    async for chunk in microphone_chunks():
        if recognizer.AcceptWaveform(chunk):
            res = json.loads(recognizer.Result())
            text = res.get("text", "").strip()
            if DEBUG and text:
                transcript.log("RAW", text)
                if last_part:
                    transcript.log("PART", "")
            awaiting = False
            buffer = ""
            last_part = ""
            text = _fix_wake_word(text)
            if not text:
                continue
            if not text.lower().startswith(WAKE_WORD.lower()):
                continue
            cmd = text[len(WAKE_WORD):].strip()
            transcript.log("USER", cmd)
            handle_text(cmd, router, tts, transcript)
        else:
            part = json.loads(recognizer.PartialResult()).get("partial", "")
            now = time.monotonic()
            if part:
                buffer = part
                awaiting = WAKE_WORD.lower() in part.lower() or awaiting
                last_voice = now
                last_part = part
                if DEBUG:
                    transcript.log("PART", part)
            elif awaiting and now - last_voice > 0.3:
                res = json.loads(recognizer.FinalResult())
                text = (buffer + " " + res.get("text", "")).strip()
                if DEBUG:
                    transcript.log("RAW", text)
                    if last_part:
                        transcript.log("PART", "")
                awaiting = False
                buffer = ""
                last_part = ""
                text = _fix_wake_word(text)
                if not text:
                    continue
                if not text.lower().startswith(WAKE_WORD.lower()):
                    continue
                cmd = text[len(WAKE_WORD):].strip()
                transcript.log("USER", cmd)
                handle_text(cmd, router, tts, transcript)


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
        choices=["voice", "console"],
        default="voice",
    )
    parser.add_argument("--model-path", default=VOSK_MODEL_PATH)
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
        print(f"TTS backend: Edge | Voice: {VOICE_NAME} | Rate: {VOICE_RATE}")
        asyncio.run(voice_loop(router, args.model_path, True, transcript))
    else:
        asyncio.run(console_loop(router, transcript))


if __name__ == "__main__":
    main()
