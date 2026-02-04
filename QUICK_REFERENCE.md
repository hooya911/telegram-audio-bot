# 🎯 Quick Reference Card

## Essential Commands

### First Time Setup
```bash
# 1. Set your bot token
export TELEGRAM_BOT_TOKEN='your-token-from-botfather'

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Install ffmpeg
# Mac:
brew install ffmpeg

# Linux:
sudo apt-get install ffmpeg

# 4. Start the bot
./start_bot.sh
```

### Daily Use
```bash
# Start the bot
./start_bot.sh

# Or run directly
python3 audio_bot.py

# Stop the bot
Press Ctrl+C
```

### Check if Running
```bash
# Check ffmpeg
ffmpeg -version

# Check Python
python3 --version

# Check if token is set
echo $TELEGRAM_BOT_TOKEN
```

---

## Telegram Setup Checklist

- [ ] Talk to @BotFather
- [ ] Send `/newbot`
- [ ] Copy and save the token
- [ ] Create a private channel
- [ ] Add bot as administrator
- [ ] Give "Post messages" permission
- [ ] Test by sending a voice message

---

## Workflow

```
📱 Phone Recording
    ↓
📤 Share to Telegram Channel
    ↓
🤖 Bot Auto-Converts to MP3
    ↓
📥 Download or Forward MP3
    ↓
📝 Send to Google Notebook LLM
    ↓
✅ Get Transcription!
```

---

## Supported Formats

✅ M4A (iPhone voice memos)
✅ OGG (Telegram voice)
✅ OPUS (WhatsApp voice)
✅ WAV
✅ AAC
✅ FLAC
✅ WMA

All convert to → MP3 (128kbps, 44.1kHz)

---

## Troubleshooting

### Bot doesn't start
```bash
# Check token is set
echo $TELEGRAM_BOT_TOKEN

# If empty, set it:
export TELEGRAM_BOT_TOKEN='your-token'
```

### Bot doesn't respond in channel
1. Check bot is running (look for ✅ message)
2. Verify bot is admin in channel
3. Check bot has "Post messages" permission

### Conversion fails
```bash
# Install/reinstall ffmpeg
brew install ffmpeg  # Mac
sudo apt-get install ffmpeg  # Linux
```

---

## File Locations

- `audio_bot.py` - Main bot code
- `requirements.txt` - Dependencies
- `start_bot.sh` - Startup script
- `README.md` - Overview
- `SETUP.md` - Detailed guide
- `DEPLOYMENT.md` - Cloud hosting

---

## Environment Variables

Required:
- `TELEGRAM_BOT_TOKEN` - Your bot token from BotFather

---

## Bot Commands

Send to your bot in Telegram:

`/start` - Get welcome message and instructions

---

## Next Steps

After basic setup works:

1. ✅ Test with different audio formats
2. ✅ Set up 24/7 hosting (see DEPLOYMENT.md)
3. ✅ Integrate with Google Notebook LLM workflow
4. ✅ Add automatic transcription (future)
5. ✅ Add cloud backup (future)

---

## Support

📖 Read SETUP.md for detailed instructions
🚀 Read DEPLOYMENT.md for cloud hosting
💬 Check inline code comments
🔍 Search error messages in logs

---

## Quick Tips

💡 Create separate channels for work vs personal
💡 Name recordings by date/topic before sending
💡 Forward WhatsApp voice messages directly
💡 Process multiple files at once
💡 Keep bot running 24/7 with cloud hosting

---

**Keep this card handy! 📌**
