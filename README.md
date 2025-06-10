# Kyra-AI-Assistant

This project contains a simple offline voice assistant and a more modular
prototype. The original script `nova_assistant.py` listens for **"Hey Nova"**
and executes a few basic commands. The new `assistant/` package provides a
more extensible assistant called **Luna** using a wake phrase "Hey Luna".

## Requirements

- Python 3.10+
- [Vosk](https://alphacephei.com/vosk/) offline speech recognition model
- Additional Python packages listed in `assistant/requirements.txt`

Install dependencies with:

```bash
pip install -r assistant/requirements.txt
```

Download the Vosk model (e.g. `vosk-model-small-en-us-0.15`) and extract it into
the project directory.

## Usage

Run the assistant:

```bash
python -m assistant.main --debug --voice en-us-kathleen-low
```

Say **"Hey Luna"** followed by a polite request. Luna introspects its tools
from `capabilities.json` and chooses the right action.
