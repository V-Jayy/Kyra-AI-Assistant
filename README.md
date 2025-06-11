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
"Close Discord" will terminate `discord.exe` on Windows. On Windows, the
`.exe` extension is added automatically if omitted.

Use `install_cmd` to copy the assistant to a directory on your `%PATH%` so you
can run it via the `Kyra` command. `uninstall_cmd` removes the files again.

On Windows there are helper batch scripts:

- `install_requirements.bat` – install Python packages
- `start_kyra_voice.bat` – launch in voice mode
- `start_kyra_text.bat` – launch in text mode
- `install_to_cmd.bat` – copy `Kyra.cmd` into `WindowsApps`
- `uninstall_from_cmd.bat` – remove the `Kyra` command
