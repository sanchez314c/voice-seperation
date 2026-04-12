@echo off
REM Voice Separation - Windows Launcher

echo === Voice Separation - Windows ===
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    echo Install from: https://python.org
    pause
    exit /b 1
)
echo Python found

REM Check FFmpeg
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ERROR: FFmpeg not found
    echo Install from: https://ffmpeg.org/download.html
    echo Add to PATH after installation
    pause
    exit /b 1
)
echo FFmpeg found

REM Get script directory
set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%..

REM Create virtual environment if needed
if not exist "%PROJECT_DIR%\venv" (
    echo Creating virtual environment...
    python -m venv "%PROJECT_DIR%\venv"
)

REM Activate virtual environment
call "%PROJECT_DIR%\venv\Scripts\activate.bat"

REM Install dependencies
echo Installing dependencies...
pip install -q -r "%PROJECT_DIR%\requirements.txt"
pip install -q torch torchaudio demucs

echo.
echo === Starting Voice Separation ===
echo.

cd /d "%PROJECT_DIR%"
python src\voice_isolation.py

pause
