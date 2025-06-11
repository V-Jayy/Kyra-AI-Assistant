@echo off
echo Creating Kyra.cmd...
echo @echo off > Kyra.cmd
echo python -m app.assistant %%* >> Kyra.cmd

set TARGET=%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\Kyra.cmd
copy /Y Kyra.cmd "%TARGET%"
echo Kyra installed to PATH. You can now use the `Kyra` command anywhere.
pause
