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

This project uses [gTTS](https://gtts.readthedocs.io/) for text-to-speech
output.

Run `python -m app.scenarios` to execute the CSV-driven self test harness.
