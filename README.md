# Aurora Assistant

This project provides an offline voice assistant powered by local models.

## Setup

1. **Download a GGUF model** (e.g. `mistral-7b-instruct-v0.2.Q4_K_M.gguf`)
   ```bash
   wget https://.../mistral.gguf -O models/mistral.gguf
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Download the Vosk model**
   ```bash
   wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
   unzip vosk-model-small-en-us-0.15.zip
   ```
4. **Run the assistant**
   ```bash
   python -m app.assistant --mode voice
   ```
   Use `--mode text` to interact via the console only.

The assistant reads optional settings from `config.json` where you can
customise the wake word, enable debug logging and choose the TTS engine.

This project uses [gTTS](https://gtts.readthedocs.io/) for text-to-speech
output.

Run `python -m app.scenarios` to execute the CSV-driven self test harness.

The `kill_process` tool can force quit applications by process name, e.g.
"Close Discord" will terminate `discord.exe` on Windows.
