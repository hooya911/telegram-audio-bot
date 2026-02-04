# 🎵 Telegram Audio Converter Bot

**Automatically convert voice memos and audio files to MP3 for Google Notebook LLM transcription**

Perfect for:
- Converting meeting recordings to MP3
- Preparing audio for transcription in Google Notebook LLM
- Processing voice messages from WhatsApp, Telegram, etc.
- Handling multilingual content (English, Farsi, etc.)

---

## ⚡️ Quick Start (5 Minutes)

### 1. Create Your Bot

1. Open Telegram and talk to **@BotFather**
2. Send: `/newbot`
3. Follow the prompts to name your bot
4. Copy the token BotFather gives you (looks like: `123456:ABCdef...`)

### 2. Create Private Channel

1. Create a new Private Channel in Telegram
2. Add your bot as an administrator
3. Give it permission to "Post messages"

### 3. Run the Bot

```bash
# Set your token
export TELEGRAM_BOT_TOKEN='your-token-here'

# Install dependencies (one time only)
pip3 install -r requirements.txt

# Make sure ffmpeg is installed
# Mac: brew install ffmpeg
# Linux: sudo apt-get install ffmpeg

# Start the bot!
./start_bot.sh
```

### 4. Test It!

1. Send a voice message to your private channel
2. Wait a few seconds
3. Bot sends back the MP3! ✅

---

## 📁 What's Included

- **audio_bot.py** - Main bot code
- **requirements.txt** - Python dependencies  
- **start_bot.sh** - Easy startup script
- **SETUP.md** - Detailed setup instructions
- **DEPLOYMENT.md** - 24/7 cloud hosting guide

---

## 🎯 How It Works

```
Your Phone                Telegram Channel              Bot                   Google Notebook LLM
    |                            |                       |                            |
    |--Voice Memo (m4a)--------->|                       |                            |
    |                            |-----Audio File------->|                            |
    |                            |                       |--Convert to MP3-->         |
    |                            |<----MP3 File----------|                            |
    |<--Forward MP3--------------|                       |                            |
    |-------------------------MP3 File------------------------------------->          |
    |                            |                       |                            |
    |<--Transcription (works great with Farsi!)----------------------------|
```

---

## 🌟 Features

✅ Converts all audio formats to MP3:
- M4A (iPhone voice memos)
- OGG (Telegram voice messages)
- OPUS (WhatsApp voice messages)
- WAV, AAC, FLAC, WMA, and more

✅ Automatic processing - just send and forget

✅ Shows conversion progress and file details

✅ Perfect quality for speech transcription

✅ Works with Google Notebook LLM for Farsi transcription

---

## 💡 Usage Tips

### Daily Workflow

1. **Record**: Use your phone's voice recorder during meetings
2. **Share**: Send to your private Telegram channel
3. **Convert**: Bot automatically converts to MP3
4. **Transcribe**: Forward MP3 to Google Notebook LLM
5. **Done**: Get accurate transcription (works great in Farsi!)

### WhatsApp Voice Messages

1. Long-press voice message in WhatsApp
2. Forward → Share to another app → Telegram
3. Select your private channel
4. Bot converts it automatically

### Batch Processing

Send multiple audio files at once - the bot processes each one individually.

---

## 🚀 Run 24/7 (Optional)

Want the bot running even when your computer is off?

**Free Options:**
- Railway.app (easiest - free tier)
- Render.com (also free tier)

**Paid Options:**
- DigitalOcean ($5/month - most reliable)
- Run on Raspberry Pi at home

See **DEPLOYMENT.md** for detailed instructions.

---

## 🔧 Requirements

- Python 3.8+
- ffmpeg (for audio conversion)
- Telegram Bot Token

---

## 📖 Documentation

- **SETUP.md** - Complete step-by-step setup guide
- **DEPLOYMENT.md** - Cloud hosting and 24/7 deployment
- **Inline comments** - Code is well-documented

---

## 🛠 Troubleshooting

### Bot doesn't respond?
- Check that it's running: Look for "Ready to convert audio files to MP3!"
- Verify it's an admin in your channel
- Check your bot token is set correctly

### Conversion fails?
```bash
# Check if ffmpeg is installed:
ffmpeg -version
```

### Need more help?
Check **SETUP.md** for detailed troubleshooting section.

---

## 🎯 Future Enhancements

Once this is working, we can add:

- 🤖 Direct Google Notebook LLM integration
- 📝 Built-in speech-to-text
- ☁️ Auto-backup to Google Drive
- 🏷️ Automatic file organization
- 📊 Transcription summaries

---

## 🔐 Privacy & Security

- Your audio files are processed locally
- No data is stored permanently
- Bot only has access to your private channel
- Token should be kept secret

---

## 📝 License

Free to use and modify for personal use.

---

## 🙏 Credits

Built to streamline the workflow from voice recording → MP3 → Google Notebook LLM transcription.

Perfect for multilingual users who need reliable transcription in languages like Farsi!

---

**Questions? Issues? Want to add features?**

This bot is designed to save you time. No more manual audio conversion!

**Happy converting! 🎵 → 📝**
