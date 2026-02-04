# 🚂 Telegram Audio Bot with OpenAI Whisper Transcription

## ✨ New Feature: Automatic Transcription!

Your bot now:
1. ✅ Converts audio to MP3
2. ✅ **Automatically transcribes with OpenAI Whisper**
3. ✅ **Supports Farsi, Turkish, Arabic** (99 languages!)
4. ✅ Sends both MP3 + transcript to Telegram

---

## 🔄 Update Steps (5 Minutes)

### Step 1: Update Files on GitHub

1. In GitHub Desktop, replace your files with the new versions
2. Commit message: "Add OpenAI Whisper transcription"
3. Push to GitHub

### Step 2: Add OpenAI API Key

1. Get your key: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-proj-...`)

### Step 3: Add Key to Railway

1. Go to Railway dashboard
2. Click your **telegram-audio-bot** project
3. Go to **Variables** tab
4. Click **New Variable**:
   - Variable: `OPENAI_API_KEY`
   - Value: (paste your key)
5. Click **Add**

Bot restarts automatically with transcription enabled!

---

## 💰 Cost

**OpenAI Whisper:** $0.006/min = $0.36/hour

**Examples:**
- 10-min meeting: $0.06
- 30-min meeting: $0.18  
- 1-hour meeting: $0.36

**Total monthly (with 20 hours of meetings):**
- Railway: ~$2
- Whisper: ~$7
- **Total: ~$9/month**

---

## 🎯 How It Works

```
1. You send voice message to Telegram
   ↓
2. Bot: "🎵 Converting to MP3..."
   ↓
3. Bot sends MP3 file
   ↓
4. Bot: "🎙️ Transcribing..."
   ↓
5. Bot sends full transcript!
   (Farsi, English, etc. - auto-detected)
```

---

## 📏 Limits

- **MP3 conversion:** Unlimited size
- **Transcription:** 25 MB limit (most 2-hour meetings fit!)

If file > 25MB, you still get MP3, just no transcription.

---

## ✅ Supported Languages (Auto-Detected!)

- ✅ Farsi/Persian (فارسی)
- ✅ Turkish (Türkçe)
- ✅ Arabic (العربية)
- ✅ English
- ✅ 95+ more languages

No configuration needed!

---

## 🔧 Troubleshooting

**No transcription?**

Check Railway logs:
- Should see: "✅ OpenAI Whisper enabled"
- If not, check OPENAI_API_KEY is set

**Transcription quality issues?**
- Record in quieter environment
- Use better microphone
- Whisper works best with clear audio

---

## 🎉 You're Done!

Just update your code and add the OpenAI key - that's it!

**No more manual transcription work! 🚀**
