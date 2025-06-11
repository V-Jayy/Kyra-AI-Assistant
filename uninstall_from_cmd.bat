@echo off
set TARGET=%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\Kyra.cmd
if exist "%TARGET%" (
    del "%TARGET%"
    echo Kyra command uninstalled.
) else (
    echo Kyra command was not found.
)
pause
