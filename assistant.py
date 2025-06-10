from __future__ import annotations

import json
import re
import time
from collections import deque
from typing import Dict, Tuple

import config
from tools import ALL_TOOLS
from transcript_console import get_console, TranscriptConsole

try:
    from vosk import Model, KaldiRecognizer
    from assistant.stt import speech_chunks  # reuse existing module
    from assistant.tts import speak, set_voice
except Exception:  # pragma: no cover - optional heavy deps
    Model = KaldiRecognizer = None  # type: ignore
    def speech_chunks(_=None):
        yield b""
    def speak(text: str, enable: bool = True):
        print("Assistant:", text)
    def set_voice(_name: str) -> None:
        pass


# ----- Intent Parsing ----------------------------------------------------
_PATTERNS = [
    (re.compile(r"(?:open|go to) (\S+\.[a-z]{2,})", re.I), "open_website", "url"),
    (re.compile(r"(?:launch|start) (.+)", re.I), "launch_program", "path"),
    (re.compile(r"(?:search|find) (.+)", re.I), "search_files", "query"),
    (re.compile(r"(?:open|show) (.+folder|[a-zA-Z]:\\\\.+)", re.I), "open_explorer", "path"),
    (re.compile(r"lock (?:pc|computer|screen)", re.I), "lock_pc", None),
    (re.compile(r"volume up", re.I), "volume_up", None),
    (re.compile(r"volume down", re.I), "volume_down", None),
]


def detect_wake_word(text: str) -> bool:
    return text.lower().startswith(config.WAKE_WORD.lower())


def parse_intent(text: str) -> Tuple[str, Dict[str, str]]:
    for pattern, tool, arg in _PATTERNS:
        m = pattern.search(text)
        if m:
            if arg:
                return tool, {arg: m.group(1)}
            return tool, {}
    if re.search(r"\w+\.\w+", text):
        return "open_website", {"url": text}
    return "", {}


# ----- Execution ---------------------------------------------------------
_recent: deque[Tuple[int, float]] = deque(maxlen=5)


def execute_command(text: str, console: TranscriptConsole) -> str:
    h = hash(text)
    now = time.time()
    if any(h == old and now - t < 2 for old, t in _recent):
        return ""  # debounce duplicate speech
    _recent.append((h, now))

    tool, args = parse_intent(text)
    fn = ALL_TOOLS.get(tool)
    if not fn:
        console.log("ERROR", "no_tool")
        return "Sorry, I couldn't understand."
    try:
        result = fn(**args)
        console.log("BOT", result)
        return result
    except Exception as exc:
        console.log("ERROR", str(exc))
        return f"Sorry, I couldn't {tool.replace('_', ' ')}."


# ----- Main Loop --------------------------------------------------------

def main() -> None:
    console = get_console()
    set_voice(config.VOICE)
    if Model is None:
        print("Vosk not available")
        return
    model = Model(config.OPTIONS.get("model_path", "vosk-model-small-en-us-0.15"))
    recognizer = KaldiRecognizer(model, 16000)
    gen = speech_chunks(config.OPTIONS.get("mic_device"))
    state = "wake"
    command_text = ""
    start = 0.0
    for chunk in gen:
        if recognizer.AcceptWaveform(chunk):
            res = json.loads(recognizer.Result())
            text = res.get("text", "")
            if not text:
                continue
            if state == "wake" and detect_wake_word(text):
                console.log("USER", text)
                speak("I'm listening", True)
                state = "command"
                start = time.time()
            elif state == "command":
                command_text += " " + text
                if time.time() - start > config.OPTIONS["speech_timeout"]:
                    console.log("USER", command_text.strip())
                    reply = execute_command(command_text.strip(), console)
                    if reply:
                        speak(reply, True)
                    command_text = ""
                    state = "wake"


if __name__ == "__main__":
    main()
