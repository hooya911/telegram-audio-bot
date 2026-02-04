# Telegram Audio Converter Bot - Complete Setup Guide

This bot automatically converts your voice memos and audio files to MP3 format, ready for Google Notebook LLM transcription!

## 📋 What You Need

1. A Telegram account
2. A computer (Windows, Mac, or Linux) OR a cloud server
3. 10 minutes for setup

---

## 🚀 Step 1: Create Your Telegram Bot

### 1.1 Talk to BotFather

1. Open Telegram on your phone or computer
2. Search for **@BotFather** (it has a blue checkmark ✓)
3. Start a chat and send: `/newbot`

### 1.2 Name Your Bot

BotFather will ask two questions:

**Question 1:** "Alright, a new bot. How are we going to call it?"
- Answer: `Ali's Audio Converter` (or any name you like)

**Question 2:** "Now let's choose a username for your bot."
- Answer: `ali_audio_mp3_bot` (or similar - must end in 'bot')

### 1.3 Save Your Token

BotFather will give you a **token** that looks like:
```
123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
```

**⚠️ IMPORTANT:** 
- Copy this token and save it somewhere safe
- Don't share it with anyone
- You'll need it in Step 3

---

## 🎯 Step 2: Create Your Private Channel

This is where you'll send your audio files.

### 2.1 Create Channel

1. In Telegram, click the pencil/compose button
2. Select "New Channel"
3. Name it something like: **"My Voice Memos"**
4. Make it **Private** (very important!)
5. Skip adding subscribers (just click Create)

### 2.2 Add Your Bot to the Channel

1. Open your new channel
2. Click the channel name at the top
3. Click "Administrators"
4. Click "Add Administrator"
5. Search for your bot (the username you created, like `@ali_audio_mp3_bot`)
6. Add it and give it these permissions:
   - ✅ Post messages
   - ✅ Delete messages
   - All other permissions can be OFF

Perfect! Your bot can now read and send messages in this channel.

---

## 💻 Step 3: Install and Run the Bot

### Option A: Run on Your Computer (Easiest for Testing)

#### 3.1 Install Python

**On Mac:**
```bash
# Open Terminal and run:
brew install python3
```

**On Windows:**
- Download from: https://www.python.org/downloads/
- Install and check "Add Python to PATH"

#### 3.2 Install ffmpeg (Required for Audio Conversion)

**On Mac:**
```bash
brew install ffmpeg
```

**On Windows:**
- Download from: https://www.gyan.dev/ffmpeg/builds/
- Extract and add to PATH (or use Chocolatey: `choco install ffmpeg`)

**On Linux:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

#### 3.3 Set Up the Bot

Open Terminal (Mac/Linux) or Command Prompt (Windows):

```bash
# Navigate to where you downloaded the bot files
cd Downloads/telegram-audio-bot

# Install dependencies
pip3 install -r requirements.txt

# Set your bot token (replace with your actual token!)
export TELEGRAM_BOT_TOKEN='123456789:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890'

# Run the bot!
python3 audio_bot.py
```

You should see:
```
🤖 Bot is starting...
✅ Ready to convert audio files to MP3!
```

### Option B: Run 24/7 on a Cloud Server (Best for Always-On)

If you want the bot to run even when your computer is off, you can use a free/cheap cloud service.

#### Recommended Services:

1. **Railway.app** (Free tier available)
2. **Render.com** (Free tier available)
3. **DigitalOcean** ($5/month)

#### Quick Railway Setup:

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Upload your bot code
5. Add environment variable: `TELEGRAM_BOT_TOKEN` = your token
6. Deploy!

Detailed railway deployment instructions are in `DEPLOYMENT.md` (optional advanced guide).

---

## 🎉 Step 4: Test It!

### 4.1 Send a Test Audio

1. Open your private channel in Telegram
2. Record a voice message OR send any audio file (m4a, ogg, etc.)
3. Wait a few seconds...
4. The bot will reply with the MP3 file! ✅

### 4.2 Normal Usage Flow

Here's your daily workflow:

1. **Record Meeting:** Use your phone's Voice Memos app during meetings
2. **Share to Telegram:** Open the voice memo → Share → Telegram → Select your private channel
3. **Bot Converts:** The bot automatically converts to MP3
4. **Send to Notebook LLM:** Forward the MP3 to Google Notebook LLM
5. **Get Transcription:** Let Google transcribe it (works great with Farsi!)

---

## 🔧 Troubleshooting

### Bot doesn't respond?

**Check 1:** Is the bot running?
- Look at your Terminal/Command Prompt
- You should see "Ready to convert audio files to MP3!"

**Check 2:** Is the bot an admin in your channel?
- Go to channel → Administrators
- Your bot should be listed

**Check 3:** Is your token correct?
- The token should be one long string with a colon `:` in the middle

### Conversion fails?

**Check:** Is ffmpeg installed?
```bash
# Run this to check:
ffmpeg -version
```

If you see version info, ffmpeg is installed correctly.

### Bot stops when I close Terminal?

This is normal. To keep it running:

**Option 1:** Use `nohup` (Mac/Linux)
```bash
nohup python3 audio_bot.py &
```

**Option 2:** Use a cloud service (Railway, Render, etc.) for 24/7 operation

---

## 💡 Pro Tips

### Tip 1: Auto-Forward from WhatsApp
If you receive voice messages on WhatsApp:
1. Long-press the voice message
2. Forward → Share to Telegram
3. Send to your private channel
4. Bot converts it automatically!

### Tip 2: Organize by Date
Name your channel with date stamps:
- "Voice Memos - Feb 2026"
- Create new channels monthly for organization

### Tip 3: Multiple Bots
Create different bots for different purposes:
- Personal voice memos
- Work meetings
- Language practice

---

## 📞 Need Help?

If something's not working:

1. Check the Terminal output for error messages
2. Make sure your bot token is set correctly
3. Verify ffmpeg is installed: `ffmpeg -version`
4. Check that the bot is an admin in your channel

---

## 🎯 Next Steps (Future Enhancements)

Once this is working, we can add:

✨ **Direct Google Notebook LLM Integration**
- Automatically upload MP3s to Google Notebook LLM
- Get transcriptions sent back to Telegram

✨ **Automatic Transcription**
- Add speech-to-text directly in the bot
- Support for Farsi and English

✨ **Cloud Storage**
- Auto-backup to Google Drive
- Organize by date/topic

Let me know when you're ready for these upgrades!

---

## 📄 Files Included

- `audio_bot.py` - Main bot code
- `requirements.txt` - Python dependencies
- `SETUP.md` - This file
- `DEPLOYMENT.md` - Advanced cloud deployment guide

---

**Enjoy your automated audio conversion! 🎵→📝**
