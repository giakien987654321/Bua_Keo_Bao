@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Dang cai dat...
if exist ".venv\Scripts\python.exe" goto install
where py >nul 2>&1
if errorlevel 1 goto use_python
py -m venv .venv
if errorlevel 1 goto failed
goto install
:use_python
python -m venv .venv
if errorlevel 1 goto failed
:install
".venv\Scripts\python.exe" --version
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo.
echo Cai dat xong. Mo CHAY_GAME.bat de chay.
pause
exit /b 0
:failed
echo.
echo Cai dat that bai.
pause
exit /b 1
