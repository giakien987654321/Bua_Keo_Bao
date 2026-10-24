@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Tao moi truong rieng trong thu muc Keo-Bua-Bao...
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
echo Cai dat xong. Mo CHAY_GAME.bat de choi.
pause
exit /b 0
:failed
echo.
echo Cai dat chua thanh cong. Hay chup lai thong bao loi phia tren.
echo Khong can xoa hoac sua thu muc du an cu.
pause
exit /b 1
