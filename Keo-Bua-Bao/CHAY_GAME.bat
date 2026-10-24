@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" goto missing
".venv\Scripts\python.exe" main.py
if errorlevel 1 pause
exit /b
:missing
echo Hay mo CAI_DAT.bat truoc. Chi can cai dat mot lan.
pause
exit /b 1
