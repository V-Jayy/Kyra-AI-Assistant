@echo off
set TARGET="C:\Program Files\Kyra"
if not exist %TARGET% (
    mkdir "%TARGET%"
)

xcopy /E /I /Y . "%TARGET%"
cd /d "%TARGET%"

echo @echo off > Kyra.cmd
echo cd /d "%TARGET%" >> Kyra.cmd
echo python -m app.assistant %%* >> Kyra.cmd

copy /Y Kyra.cmd "%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\Kyra.cmd"
echo Kyra installed globally. You can now run it with: Kyra
pause
