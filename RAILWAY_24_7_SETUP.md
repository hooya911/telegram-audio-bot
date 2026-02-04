# 🚂 Railway.app - 24/7 Deployment Guide

## Why Railway?
- ✅ FREE (500 hours/month = 20 days 24/7)
- ✅ Always running (even when your PC is off)
- ✅ No server management needed
- ✅ Takes 15 minutes to setup
- ✅ Auto-restarts if it crashes

---

## Step 1: Create Railway Account (2 minutes)

1. Go to: https://railway.app
2. Click "Start a New Project"
3. Sign up with GitHub (you'll need a GitHub account)
   - If you don't have GitHub: https://github.com/join
   - It's free and takes 2 minutes

---

## Step 2: Create GitHub Repository (5 minutes)

### Option A: Use GitHub Desktop (Easiest)

1. Download GitHub Desktop: https://desktop.github.com/
2. Install and sign in with your GitHub account
3. Click "File" → "Add Local Repository"
4. Select your `telegram-audio-bot` folder
5. Click "Publish Repository"
6. Make it PUBLIC (Railway needs public repos on free tier)
7. Click "Publish"

### Option B: Use GitHub Website (Alternative)

1. Go to: https://github.com/new
2. Repository name: `telegram-audio-bot`
3. Make it PUBLIC
4. Click "Create repository"
5. Follow the instructions to upload your files
   - Or use GitHub Desktop (easier!)

---

## Step 3: Prepare Your Code (2 minutes)

You need to add 2 small files to your bot folder:

### File 1: Create `Procfile` (no extension!)

Create a new file called exactly `Procfile` (no .txt, no .bat) with this content:

```
worker: python audio_bot.py
```

**How to create Procfile:**
1. Open Notepad
2. Paste: `worker: python audio_bot.py`
3. Save As → Filename: `Procfile` (not Procfile.txt!)
4. Save Type: "All Files"
5. Save in your telegram-audio-bot folder

### File 2: Create `railway.json`

Create `railway.json` with this content:

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "numReplicas": 1,
    "sleepApplication": false,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### File 3: Create `nixpacks.toml`

Create `nixpacks.toml` with this content:

```toml
[phases.setup]
nixPkgs = ["ffmpeg"]
```

This tells Railway to install ffmpeg automatically.

---

## Step 4: Push to GitHub

If using GitHub Desktop:
1. It will show your new files
2. Write commit message: "Add Railway config"
3. Click "Commit to main"
4. Click "Push origin"

Done! Your code is now on GitHub.

---

## Step 5: Deploy to Railway (5 minutes)

1. Go to https://railway.app
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Find and select: `telegram-audio-bot`
5. Click "Deploy Now"

Railway will start building your bot!

---

## Step 6: Add Your Bot Token (IMPORTANT!)

1. In Railway dashboard, click on your project
2. Click "Variables" tab
3. Click "New Variable"
4. Add:
   - **Name:** `TELEGRAM_BOT_TOKEN`
   - **Value:** `8400464691:AAETt_M0L63C3Lwgy9O_nE04NdKjOV2Xvkc`
5. Click "Add"

Railway will automatically restart your bot with the token.

---

## Step 7: Check It's Running

1. In Railway dashboard, click "Deployments"
2. Click on the latest deployment
3. Click "View Logs"
4. You should see:
   ```
   🤖 Bot is starting...
   ✅ Ready to convert audio files to MP3!
   ```

**SUCCESS!** Your bot is now running 24/7! 🎉

---

## Test It

1. Close your computer's Command Prompt (bot doesn't need it anymore!)
2. Go to your Telegram channel
3. Send an audio file
4. Bot converts it automatically!

Your bot is now in the cloud running 24/7 even when your computer is off!

---

## Railway Dashboard

**View Logs:**
- Railway Dashboard → Your Project → Deployments → View Logs

**Restart Bot:**
- Railway Dashboard → Your Project → Settings → Restart

**Stop Bot:**
- Railway Dashboard → Your Project → Settings → Delete Service

---

## Free Tier Limits

Railway free tier includes:
- ✅ $5 credit per month
- ✅ ~500 hours of runtime (20+ days)
- ✅ Enough for 24/7 operation

**Cost:** Your bot uses about $0.20-0.30 per day, so you get ~16-25 days free per month.

**If you need more:** Upgrade to Hobby plan ($5/month, unlimited)

---

## Troubleshooting

### "Build failed" error?

Check these files exist:
- ✅ Procfile (exactly this name)
- ✅ railway.json
- ✅ nixpacks.toml
- ✅ requirements.txt
- ✅ audio_bot.py

### Bot not responding?

Check environment variable:
1. Railway → Variables
2. Make sure `TELEGRAM_BOT_TOKEN` is set correctly

### Want to update code?

1. Edit files locally
2. Commit in GitHub Desktop
3. Push to GitHub
4. Railway auto-deploys!

---

## Summary

After this one-time 15-minute setup:

✅ Bot runs 24/7 in the cloud
✅ No need for your computer to be on
✅ Free (or $5/month for unlimited)
✅ Auto-restarts if it crashes
✅ Easy to update (just push to GitHub)

**Your workflow:**
1. Record meeting on phone
2. Share to Telegram channel
3. Bot converts (always working, even at 3 AM!)
4. Forward MP3 to Notebook LLM
5. Done!

---

**Questions? Let me know! This is the proper way to run bots 24/7! 🚀**
