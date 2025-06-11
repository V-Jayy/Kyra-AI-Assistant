@echo off
set "TARGET=C:\Program Files\Kyra"
set "LAUNCH=C:\Windows\Kyra.bat"
rd /s /q "%TARGET%"
if exist "%LAUNCH%" del "%LAUNCH%"
echo Kyra has been fully uninstalled.
pause
