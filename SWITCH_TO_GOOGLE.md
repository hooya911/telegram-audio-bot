# 🎯 Switch to Google Cloud Speech-to-Text - Quick Start

## Why Switch?

✅ **Better Farsi quality** (same as Google Notebook LLM)
✅ **No 4-minute cutoff** (handles full 8-minute files)
✅ **More reliable** for longer audio
✅ **First 60 minutes FREE** per month

---

## 📋 What You Need to Do:

### Part 1: Google Cloud Setup (20 minutes)
**Follow GOOGLE_CLOUD_SETUP.md for detailed steps**

Quick summary:
1. Create Google Cloud account (get $300 free credit!)
2. Enable Speech-to-Text API
3. Create service account
4. Download JSON credentials file
5. Convert JSON to single line

### Part 2: Update Bot (5 minutes)

1. **Replace files** from new ZIP:
   - bot.py (now uses Google Cloud)
   - requirements.txt (new libraries)
   
2. **Push to GitHub** (GitHub Desktop)

3. **Update Railway Variables:**
   - Remove: `OPENAI_API_KEY`
   - Add: `GOOGLE_APPLICATION_CREDENTIALS_JSON` = (your JSON single line)

4. **Test!**

---

## 💰 Cost Comparison

| Service | Cost/Hour | Quality (Farsi) | File Limit |
|---------|-----------|-----------------|------------|
| OpenAI Whisper | $0.36 | ⭐⭐⭐ Good | 25 MB |
| Google Cloud | $1.44 | ⭐⭐⭐⭐⭐ Excellent | Unlimited |

**Google is 4x more expensive BUT:**
- First 60 minutes FREE monthly
- $300 free credit = ~208 hours = ~10 months free!
- Way better quality for Farsi

---

## 🔧 What Changed in Bot:

**Before (OpenAI):**
- ❌ Cut off at 4 minutes
- ❌ Lower quality for Farsi
- ✅ Cheaper ($0.36/hour)

**After (Google Cloud):**
- ✅ Full transcription (no cutoffs)
- ✅ Same quality as Notebook LLM
- ✅ Handles longer files
- ⚠️ More expensive ($1.44/hour after free tier)

---

## 📝 New Features:

1. **Auto language detection** - Farsi, English, Turkish, Arabic
2. **Long audio support** - Files up to 480 minutes (8 hours!)
3. **Better punctuation** - Automatic punctuation in Farsi
4. **No cutoffs** - Complete transcription every time

---

## ⚡ Quick Steps:

1. ✅ Complete GOOGLE_CLOUD_SETUP.md
2. ✅ Get JSON credentials
3. ✅ Replace bot.py and requirements.txt
4. ✅ Push to GitHub
5. ✅ Add JSON to Railway variables
6. ✅ Test with 8-minute Farsi audio!

---

**Start with GOOGLE_CLOUD_SETUP.md for complete instructions!**
