# Aurora Assistant

This project provides an offline voice assistant powered by local models.

## Setup

1. **Build `llama.cpp`**
   ```bash
   git clone https://github.com/ggerganov/llama.cpp
   cd llama.cpp && make
   ```
2. **Download a GGUF model** (e.g. `mistral-7b-instruct-v0.2.Q4_K_M.gguf`)
   ```bash
   wget https://.../mistral.gguf -O models/mistral.gguf
   ```
3. **Start the local LLM server**
   ```bash
   ./main -m models/mistral.gguf --port 11434 --api
   ```
   Or with Ollama:
   ```bash
   ollama run mistral:latest
   ```
4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
5. **Download the Vosk model**
   ```bash
   wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
   unzip vosk-model-small-en-us-0.15.zip
   ```
6. **Run the assistant**
   ```bash
   python -m app.assistant --mode voice
   ```

Run `python -m app.scenarios` to execute the CSV-driven self test harness.
