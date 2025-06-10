# Aurora Assistant

This project provides an offline voice assistant powered by local models.

## Quick Start

```shell
git clone ...
cd Kyra-AI-Assistant
start.bat          # Windows
# or
pip install -e .   # any OS
Kyra help
```

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
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Download the Vosk model**
   ```bash
   wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
   unzip vosk-model-small-en-us-0.15.zip
   ```
5. **Run the assistant**
   ```bash
   python -m kyra.main --mode voice
   ```

Run `python -m app.scenarios` to execute the CSV-driven self test harness.
