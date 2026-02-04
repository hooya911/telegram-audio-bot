#!/bin/bash

# Try python3 first, then python
if command -v python3 &> /dev/null; then
    python3 audio_bot.py
elif command -v python &> /dev/null; then
    python audio_bot.py
else
    echo "Error: Python not found"
    exit 1
fi
