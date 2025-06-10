import pyttsx3
from typing import Optional


def speak(text: str, enable: bool = True) -> None:
    """Speak text using pyttsx3 if enabled."""
    print(f"Assistant: {text}")
    if not enable:
        return
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
