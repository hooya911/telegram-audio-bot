#!/bin/bash

# Simple startup script for the Telegram Audio Converter Bot

echo "🤖 Starting Telegram Audio Converter Bot..."
echo ""

# Check if token is set
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ ERROR: TELEGRAM_BOT_TOKEN not set!"
    echo ""
    echo "Please set your bot token first:"
    echo "  export TELEGRAM_BOT_TOKEN='your-token-from-botfather'"
    echo ""
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed"
    echo "Please install Python 3 first"
    exit 1
fi

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  WARNING: ffmpeg is not installed"
    echo "Audio conversion will not work without ffmpeg"
    echo ""
    echo "Install ffmpeg:"
    echo "  Mac:     brew install ffmpeg"
    echo "  Ubuntu:  sudo apt-get install ffmpeg"
    echo "  Windows: Download from https://ffmpeg.org/"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if dependencies are installed
echo "📦 Checking Python dependencies..."
pip3 install -q -r requirements.txt

echo ""
echo "✅ All checks passed!"
echo "🚀 Starting bot..."
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run the bot
python3 audio_bot.py
