@echo off
set "LAUNCH=C:\Windows\Kyra.bat"
if exist "%LAUNCH%" (
    del "%LAUNCH%"
    echo Kyra command uninstalled.
) else (
    echo Kyra command was not found.
)
pause
