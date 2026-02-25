# Telegram Audio Bot — Project Guide for Claude

## What This Bot Does
A Telegram bot that:
1. Receives audio files (voice messages, .m4a, .ogg, .opus, .wav, .aac, .flac, .wma, .mp3)
2. Converts them to MP3 using pydub + ffmpeg
3. Transcribes the audio using Google Gemini AI (Farsi + English mixed audio)
4. Sends both the MP3 file and the transcription back to the user in Telegram

## Deployment Stack
- **Platform:** Railway (https://railway.app)
- **Builder:** Nixpacks (defined in nixpacks.toml)
- **Auto-deploy:** Every push to the `main` branch on GitHub triggers a Railway deploy
- **Python version:** 3.10
- **System dependency:** ffmpeg (installed by nixpacks)

## Repository Structure
```
bot.py              ← Main bot code (THE only file that matters for logic)
requirements.txt    ← Python dependencies
nixpacks.toml       ← Railway build config (installs Python 3.10 + ffmpeg)
railway.json        ← Railway deploy config (always-on, restart on failure)
CLAUDE.md           ← This file
README.md           ← Setup instructions
.gitignore          ← Excludes credentials, subfolder, cache
```

## ⚠️ IMPORTANT — Do NOT touch these files unless necessary
- `nixpacks.toml` — changing this can break the Railway build
- `railway.json` — leave as-is
- `.gitignore` — the `telegram-audio-bot/` subfolder must stay ignored

## Environment Variables (set in Railway dashboard, NOT in code)
| Variable | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather on Telegram |
| `GEMINI_API_KEY` | Google AI Studio API key for transcription |

**Never hardcode these values in bot.py or any file.**

## Key Libraries
```
python-telegram-bot==20.7   ← Telegram API
pydub==0.25.1               ← Audio conversion
google-generativeai>=0.7.0  ← Gemini AI for transcription
```

## How the Bot Works (bot.py logic)
1. `handle_audio()` — catches voice/audio/document messages
2. Downloads the file from Telegram
3. Converts to MP3 (tries 128k → falls back to 64k mono → splits in 2 if too large)
4. Sends the MP3 back to the user
5. If `GEMINI_API_KEY` is set: calls `transcribe_with_gemini()`
6. `transcribe_with_gemini()` uploads to Gemini Files API, waits for processing, gets transcription
7. `send_transcription()` sends the text back (splits into multiple messages if > 4000 chars)

## Audio Language
The bot handles **mixed Farsi (Persian) + English** audio.
Transcription prompt instructs Gemini to:
- Write Farsi in Persian script (فارسی)
- Write English in English
- Add timestamps every ~2 minutes
- Never translate, always transcribe

## Planned Features (implement when requested)
- [ ] AI summary after transcription (using Gemini)
- [ ] /start command with welcome message
- [ ] Support for video files (extract audio)

## How to Make Changes (cloud workflow)
1. Go to https://github.com/hooya911/telegram-audio-bot
2. Click "Issues" → "New Issue"
3. Describe the change
4. Assign to @claude
5. Claude writes the code and opens a Pull Request
6. Review and merge the PR
7. Railway auto-deploys within ~2 minutes
