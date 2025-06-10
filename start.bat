@echo off
setlocal

if not exist .venv (
    python -m venv .venv
)
call .\.venv\Scripts\activate.bat

python -m pip install -qq --upgrade pip
python -m pip install -r requirements.txt llama-cpp-python

echo Starting Kyra...
python -m kyra.main %*
endlocal

