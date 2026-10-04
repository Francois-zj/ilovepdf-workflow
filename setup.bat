@echo off
chcp 65001 >nul
cd /d "%~dp0"
python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul
if not errorlevel 1 (
 set "PYTHON_CMD=python"
 goto install
)
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul
if errorlevel 1 goto fail
set "PYTHON_CMD=py -3"
:install
%PYTHON_CMD% -m venv .venv
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto fail
echo Installation complete. Chrome or Edge must be installed. Double-click start.bat.
pause
exit /b 0
:fail
echo Installation failed. Check the error above. Python 3.10+ with tkinter is required.
echo Enable Add Python to PATH when installing Python.
pause
exit /b 1
