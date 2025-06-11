@echo off
set TARGET="C:\Program Files\Kyra"
rd /s /q %TARGET%
del "%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\Kyra.cmd"
echo Kyra has been fully uninstalled.
pause
