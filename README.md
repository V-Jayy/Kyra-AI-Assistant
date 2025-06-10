# Kyra-AI-Assistant

This project contains a simple offline voice assistant that responds to the wake word **"Hey Nova"** and can execute a few basic spoken commands.

## Requirements

- Python 3.8+
- [Vosk](https://alphacephei.com/vosk/) offline speech recognition model
- `pyttsx3`, `pyaudio`, `vosk`, `keyboard`

Install dependencies with:

```bash
pip install vosk pyttsx3 pyaudio keyboard
```

Download the Vosk model (e.g., `vosk-model-small-en-us-0.15`) and extract it into the project directory.

## Usage

Run the assistant:

```bash
python nova_assistant.py
```

Say **"Hey Nova"** followed by a command such as "open YouTube".
