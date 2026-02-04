# Windows Setup Guide - Telegram Audio Converter Bot

## Quick Start for Windows

### Step 1: Install Python

1. Go to https://www.python.org/downloads/
2. Download Python 3.11 or newer
3. **IMPORTANT:** Check "Add Python to PATH" during installation
4. Install

### Step 2: Install ffmpeg

**Option A - Easy Way (Recommended):**
1. Install Chocolatey package manager:
   - Open PowerShell as Administrator
   - Run: `Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))`
2. Install ffmpeg: `choco install ffmpeg`

**Option B - Manual Way:**
1. Download from: https://www.gyan.dev/ffmpeg/builds/
2. Download the "ffmpeg-release-essentials.zip"
3. Extract to `C:\ffmpeg`
4. Add to PATH:
   - Search "Environment Variables" in Windows
   - Edit "Path" variable
   - Add: `C:\ffmpeg\bin`

### Step 3: Get Your Bot Token

1. Open Telegram
2. Search for @BotFather
3. Send: `/newbot`
4. Follow instructions
5. Copy your token (looks like: `123456789:ABCdef...`)

### Step 4: Edit the Batch File

1. Open `start_bot.bat` in Notepad
2. Find this line:
   ```
   set TELEGRAM_BOT_TOKEN=YOUR_TOKEN_HERE
   ```
3. Replace `YOUR_TOKEN_HERE` with your actual token
4. Save the file

### Step 5: Run the Bot

**Double-click `start_bot.bat`**

That's it! The bot will start automatically.

## Alternative: Run from Command Prompt

If you prefer Command Prompt:

```cmd
cd Downloads\telegram-audio-bot
set TELEGRAM_BOT_TOKEN=8408466591:AAEIt_W0L63c1wgy9Q_nE4N4KjQV2kVkc
pip install -r requirements.txt
python audio_bot.py
```

## Troubleshooting

### "python is not recognized"
- Python not installed or not in PATH
- Reinstall Python and check "Add to PATH"

### "ffmpeg is not recognized"
- ffmpeg not installed or not in PATH
- Follow Step 2 above

### Bot doesn't respond in Telegram
1. Make sure bot is running (window should say "Ready to convert")
2. Add bot as admin to your private channel
3. Give it "Post messages" permission

## Keeping Bot Running

The bot runs as long as the Command Prompt window is open.

**To run 24/7:**
- Use Railway.app (free, easiest)
- Or leave your PC on with the bot running

See DEPLOYMENT.md for cloud hosting options.

---

**You're all set! Send an audio file to your Telegram channel and watch it convert!**
