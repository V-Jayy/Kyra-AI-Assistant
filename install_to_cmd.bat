@echo off
set "TARGET=C:\Program Files\Kyra"
set "LAUNCH=C:\Windows\Kyra.bat"

if not exist "%TARGET%" (
    mkdir "%TARGET%"
)

xcopy /E /I /Y . "%TARGET%"

if not exist "%TARGET%\venv\Scripts\python.exe" (
    python -m venv "%TARGET%\venv"
    "%TARGET%\venv\Scripts\pip.exe" install -r "%TARGET%\requirements.txt"
)

echo @echo off>"%LAUNCH%"
echo cd /d "%TARGET%" >>"%LAUNCH%"
echo "%TARGET%\venv\Scripts\python.exe" -m app.assistant %%* >>"%LAUNCH%"

echo Kyra installed to PATH. You can now use the Kyra command anywhere.
pause
