"""Wrapper around Piper TTS with simple queuing."""

import subprocess
import threading
import queue

_voice = "en-us-kathleen-low"
_queue: queue.Queue[str] = queue.Queue()


def set_voice(name: str) -> None:
    """Select a different Piper voice model."""
    global _voice
    _voice = name


def _worker() -> None:
    while True:
        text = _queue.get()
        if text is None:
            break
        print(f"Assistant: {text}")
        subprocess.run([
            "piper",
            "--model",
            _voice,
            "--text",
            text,
        ], check=False)
        _queue.task_done()


_thread = threading.Thread(target=_worker, daemon=True)
_thread.start()


def speak(text: str, enable: bool = True) -> None:
    """Enqueue text to be spoken."""
    if not enable:
        print(f"Assistant: {text}")
        return
    _queue.put(text)
