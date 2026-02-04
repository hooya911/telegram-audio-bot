@echo off
REM Windows Startup Script for Telegram Audio Converter Bot

echo.
echo ================================
echo Telegram Audio Converter Bot
echo ================================
echo.

REM Set your bot token here
set TELEGRAM_BOT_TOKEN=8400464691:AAETt_M0L63C3Lwgy9O_nE04NdKjOV2Xvkc

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if ffmpeg is installed
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo WARNING: ffmpeg is not installed
    echo.
    echo Audio conversion will not work without ffmpeg.
    echo.
    echo Install ffmpeg:
    echo 1. Download from: https://www.gyan.dev/ffmpeg/builds/
    echo 2. Extract and add to PATH
    echo    OR
    echo 3. Use Chocolatey: choco install ffmpeg
    echo.
    pause
)

echo Installing Python dependencies...
pip install -q -r requirements.txt

echo.
echo Starting bot...
echo.
echo Press Ctrl+C to stop
echo.

REM Run the bot
python audio_bot.py

pause
