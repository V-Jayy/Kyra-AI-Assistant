# Kyra-AI-Assistant

This project now provides a lightweight voice assistant called **Aurora**.
Configuration lives in `config.py` where you can change the wake word,
default TTS voice and other options.  Tools are pure functions in
`tools.py` and the main event loop is implemented in `assistant.py`.

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
python assistant.py
```

Say the wake phrase (default **"Hey Aurora"**) and then a command such as
"open youtube.com".  When `DEBUG` is enabled a transcript window will
appear.  To add new tools simply create a function in `tools.py` and
register it in the `ALL_TOOLS` dictionary.
