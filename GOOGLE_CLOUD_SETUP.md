# 🎙️ Google Cloud Speech-to-Text API Setup Guide

Complete step-by-step guide to set up Google Cloud Speech-to-Text for your Telegram bot.

---

## 📋 What You'll Need

- Google account (Gmail)
- Credit card (for verification - you get $300 free credit!)
- 20 minutes for setup

---

## 💰 Pricing

**Google Cloud Speech-to-Text:**
- First 60 minutes per month: **FREE**
- After that: $0.024/minute = $1.44/hour

**Comparison:**
- OpenAI Whisper: $0.36/hour
- Google Cloud: $1.44/hour

Google is 4x more expensive BUT better quality for Farsi!

---

## 🚀 Step 1: Create Google Cloud Account

### 1.1 Go to Google Cloud
1. Open: https://console.cloud.google.com/
2. Sign in with your Gmail account

### 1.2 Start Free Trial
1. Click **"Activate"** or **"Start Free Trial"**
2. Select your country
3. Agree to terms
4. Click **"Continue"**

### 1.3 Add Payment Method
1. Add credit card details (for verification)
2. **Don't worry:** You get $300 free credit
3. They won't charge unless you manually upgrade
4. Click **"Start my free trial"**

---

## 🔧 Step 2: Create a New Project

### 2.1 Create Project
1. Click the project dropdown (top left, next to "Google Cloud")
2. Click **"New Project"**
3. Project name: `Telegram Audio Bot`
4. Click **"Create"**
5. Wait 30 seconds for it to be created

### 2.2 Select Your Project
1. Click the project dropdown again
2. Select **"Telegram Audio Bot"**

---

## 🎯 Step 3: Enable Speech-to-Text API

### 3.1 Go to API Library
1. Click the hamburger menu (☰) on the top left
2. Go to: **APIs & Services** → **Library**

### 3.2 Find Speech-to-Text API
1. In the search bar, type: `Speech-to-Text`
2. Click on **"Cloud Speech-to-Text API"**
3. Click **"Enable"**
4. Wait 10-20 seconds

---

## 🔑 Step 4: Create Service Account & API Key

### 4.1 Go to Credentials
1. Click hamburger menu (☰)
2. Go to: **APIs & Services** → **Credentials**

### 4.2 Create Service Account
1. Click **"+ Create Credentials"** (at the top)
2. Select **"Service Account"**
3. Service account details:
   - Name: `telegram-bot-service`
   - Service account ID: (auto-filled)
   - Description: `For Telegram audio transcription`
4. Click **"Create and Continue"**

### 4.3 Grant Permissions
1. In "Grant this service account access to project"
2. Select role: **"Cloud Speech-to-Text User"**
3. Click **"Continue"**
4. Click **"Done"**

### 4.4 Create JSON Key
1. You'll see your service account in the list
2. Click on the **email address** (telegram-bot-service@...)
3. Go to **"Keys"** tab (at the top)
4. Click **"Add Key"** → **"Create new key"**
5. Choose **JSON** format
6. Click **"Create"**

### 4.5 Download JSON File
1. A JSON file will download automatically
2. **This is your API key file!**
3. Keep it safe - you can only download it once
4. Rename it to something simple: `google-credentials.json`

---

## 🔐 Step 5: Prepare Credentials for Railway

The JSON file looks like this:
```json
{
  "type": "service_account",
  "project_id": "telegram-audio-bot-xxxxx",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "telegram-bot-service@...",
  ...
}
```

### 5.1 Convert to Single Line
Railway needs this as a single-line string. Use this method:

**Option A: Online Tool**
1. Go to: https://www.text-utils.com/json-formatter/
2. Paste your JSON
3. Click "Minify"
4. Copy the result (one long line)

**Option B: Manually**
1. Open the JSON file in Notepad
2. Remove ALL line breaks (make it one long line)
3. Copy everything

---

## 🚂 Step 6: Add to Railway

### 6.1 Go to Railway
1. Open: https://railway.app/dashboard
2. Click on your **telegram-audio-bot** project
3. Click on the service
4. Go to **"Variables"** tab

### 6.2 Remove Old OpenAI Key
1. Find `OPENAI_API_KEY`
2. Click the three dots (⋮)
3. Click **"Remove"**

### 6.3 Add Google Credentials
1. Click **"+ New Variable"**
2. Variable name: `GOOGLE_APPLICATION_CREDENTIALS_JSON`
3. Value: Paste the single-line JSON (from Step 5.1)
4. Click **"Add"**

---

## 📝 Step 7: Update Your Bot Code

I'll give you the updated bot.py file that uses Google Cloud instead of OpenAI.

### Changes needed:
1. Replace `bot.py` with new version (I'll create this)
2. Update `requirements.txt` to include Google Cloud library
3. Push to GitHub
4. Railway auto-deploys

---

## 🧪 Step 8: Test

1. Send audio to Telegram
2. Should see: "🎙️ Transcribing with Google Cloud..."
3. Get high-quality Farsi transcription!

---

## 🎯 Summary - What You Need:

✅ Google Cloud account (free $300 credit)
✅ Speech-to-Text API enabled
✅ Service account created
✅ JSON credentials file downloaded
✅ JSON converted to single line
✅ Added to Railway as `GOOGLE_APPLICATION_CREDENTIALS_JSON`
✅ Updated bot code (next step - I'll provide this)

---

## 💡 Benefits of Google Cloud:

✅ Better Farsi quality (what you experienced with Notebook LLM)
✅ Handles longer files (no 4-minute cutoff)
✅ More reliable for production
✅ First 60 minutes FREE per month
✅ Same technology as Google Notebook LLM

---

## ⚠️ Important Notes:

1. **Keep JSON file secure** - it's like a password
2. **Don't commit to GitHub** - only add to Railway variables
3. **Monitor usage** - Check Google Cloud Console for costs
4. **$300 free credit** - Lasts a long time for this use case

---

## 📊 Cost Estimate:

If you transcribe **20 hours per month:**
- First 1 hour: FREE
- Remaining 19 hours: 19 × $1.44 = **$27.36/month**

With $300 free credit, you get **10+ months free**!

---

**Next: I'll create the updated bot code that uses Google Cloud. Let me know when you've completed these steps!**
