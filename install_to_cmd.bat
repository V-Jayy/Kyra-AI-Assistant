@echo off
set TARGET=%USERPROFILE%\AppData\Local\Kyra
if not exist "%TARGET%" (
    mkdir "%TARGET%"
)
xcopy /E /I /Y . "%TARGET%"

echo @echo off > Kyra.cmd
echo cd /d "%TARGET%" >> Kyra.cmd
echo python -m app.assistant %%* >> Kyra.cmd

copy /Y Kyra.cmd "%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\Kyra.cmd"
del Kyra.cmd
echo Kyra installed to PATH. You can now use the Kyra command anywhere.
pause
