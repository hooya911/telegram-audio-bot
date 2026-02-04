#!/usr/bin/env bash
# Build script for Render.com

set -o errexit

# Install ffmpeg
apt-get update
apt-get install -y ffmpeg

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
