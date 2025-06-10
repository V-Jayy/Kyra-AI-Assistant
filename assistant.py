import asyncio
import json
import yaml

from assistant.console import TranscriptConsole
from assistant.stt import speech_chunks
from assistant.tools import match_tool
from assistant.tts import speak, set_voice
from assistant.router import Router
from assistant.main import load_stt

CONFIG_PATH = "config.yaml"


def load_config(path: str = CONFIG_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


async def main() -> None:
    cfg = load_config()
    WAKE_WORD = cfg.get("wake_word", "hey nova").lower()
    console = TranscriptConsole(debug=cfg.get("debug", False))
    set_voice(cfg.get("tts_voice", "en-us-kathleen-low"))
    router = Router()

    recognizer = await load_stt()
    gen = speech_chunks()
    state = "wake"
    async for chunk in gen:
        if recognizer.AcceptWaveform(chunk):
            res = json.loads(recognizer.Result())
            text = res.get("text", "").lower()
            if text:
                console.log(text, user=True)
            if state == "wake" and text.startswith(WAKE_WORD):
                speak("I'm listening", True)
                state = "command"
            elif state == "command" and text:
                tool, params = match_tool(text)
                if tool:
                    console.log(f"[INTENT] {tool.name} {params}", user=False)
                    tool.handler(params)
                else:
                    fn, kwargs = router.select(text)
                    console.log(f"[INTENT] {fn.__name__} {kwargs}", user=False)
                    fn(**kwargs)
                state = "wake"
        else:
            pres = json.loads(recognizer.PartialResult())
            partial = pres.get("partial", "")
            if partial:
                console.log(partial, user=True)


if __name__ == "__main__":
    asyncio.run(main())
