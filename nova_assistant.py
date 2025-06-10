import os
import queue
import json
import threading
import pyttsx3
import pyaudio
import webbrowser
from vosk import Model, KaldiRecognizer

# Voice setup

tts_engine = pyttsx3.init()

def speak(text: str) -> None:
    """Speak the provided text out loud and print it."""
    print(f"Assistant: {text}")
    tts_engine.say(text)
    tts_engine.runAndWait()


# Load Vosk STT model
MODEL_PATH = "vosk-model-small-en-us-0.15"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"Vosk model not found at '{MODEL_PATH}'. Download and extract it from https://alphacephei.com/vosk/models"  # noqa: E501
    )

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)

# Queue for microphone data

audio_queue: queue.Queue[bytes] = queue.Queue()


def listen_microphone() -> None:
    """Continuously collect microphone audio and place it into audio_queue."""
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
        audio_queue.put(data)


def execute_command(command: str) -> None:
    """Handle recognized commands."""
    command = command.lower()
    if "open youtube" in command:
        speak("Opening YouTube")
        webbrowser.open_new_tab("https://youtube.com")
    elif "open google" in command:
        speak("Opening Google")
        webbrowser.open_new_tab("https://google.com")
    elif "what time is it" in command:
        from datetime import datetime

        now = datetime.now().strftime("%H:%M")
        speak(f"The time is {now}")
    else:
        speak("Sorry, I didn't understand that command.")


def main() -> None:
    """Main loop that waits for wake word and processes commands."""
    WAKE_WORD = "hey nova"
    threading.Thread(target=listen_microphone, daemon=True).start()

    print("Listening for wake word...")

    while True:
        data = audio_queue.get()
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").lower()
            if text.startswith(WAKE_WORD):
                speak("I'm listening.")
                # Capture the next phrase as a command
                command_text = ""
                while True:
                    cmd_data = audio_queue.get()
                    if recognizer.AcceptWaveform(cmd_data):
                        cmd_result = json.loads(recognizer.Result())
                        command_text = cmd_result.get("text", "")
                        break
                execute_command(command_text)


if __name__ == "__main__":
    main()
