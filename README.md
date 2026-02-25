# 🚂 Telegram Audio Bot - Railway Deployment (Clean Start)

## What's Included (4 Files Only!)

1. **bot.py** - The bot code (simplified and tested)
2. **requirements.txt** - Python packages
3. **nixpacks.toml** - Railway config (installs Python 3.10 + ffmpeg)
4. **railway.json** - Deployment settings

That's it! No extra files to confuse things.

---

## 🔄 Step 1: Delete Old GitHub Repository

1. Go to: https://github.com/hooya911/telegram-audio-bot
2. Click **"Settings"** (at the top)
3. Scroll all the way down
4. Click **"Delete this repository"**
5. Type: `hooya911/telegram-audio-bot`
6. Click **"I understand the consequences, delete this repository"**

**Done! Old repo deleted.**

---

## 📤 Step 2: Create New GitHub Repository

### Using GitHub Desktop (Easiest):

1. Open GitHub Desktop
2. Click **"File"** → **"New Repository"**
3. Settings:
   - **Name:** `telegram-audio-bot`
   - **Local Path:** Choose where to save
   - **Initialize:** Check "Initialize this repository with a README"
4. Click **"Create Repository"**
5. Click **"Publish repository"**
6. **IMPORTANT:** Uncheck "Keep this code private"
7. Click **"Publish Repository"**

### Now Add the Bot Files:

1. Open the folder where you created the repository
2. Copy these 4 files from the ZIP into that folder:
   - `bot.py`
   - `requirements.txt`
   - `nixpacks.toml`
   - `railway.json`
3. In GitHub Desktop, you'll see these files appear
4. Write commit message: "Initial bot setup"
5. Click **"Commit to main"**
6. Click **"Push origin"**

**Done! Clean repository with only 4 files.**

---

## 🚂 Step 3: Deploy to Railway (Clean Start)

### 3.1 Delete Old Railway Project (If You Have One)

1. Go to: https://railway.app/dashboard
2. Find your old `telegram-audio-bot` project
3. Click on it
4. Go to **"Settings"**
5. Scroll down and click **"Delete Project"**
6. Confirm deletion

### 3.2 Create New Railway Project

1. Go to: https://railway.app/new
2. Click **"Deploy from GitHub repo"**
3. Select your repository: **`telegram-audio-bot`**
4. Railway will automatically detect your configuration!
5. Click **"Deploy Now"**

### 3.3 Add Your Bot Token

1. In Railway, your project will start building
2. Click on your service (the card in the middle)
3. Go to **"Variables"** tab
4. Click **"New Variable"**
5. Add:
   - **Variable:** `TELEGRAM_BOT_TOKEN`
   - **Value:** your bot token (get it from @BotFather)
6. Click **"Add"**

The service will automatically restart with your token!

---

## ✅ Step 4: Verify It's Working

1. In Railway, click **"Deployments"** tab
2. Click on the latest deployment
3. Click **"View Logs"**
4. Wait about 2 minutes for build to complete
5. You should see:
   ```
   🤖 Bot starting...
   ✅ Ready to convert audio files to MP3!
   ```

**SUCCESS!** 🎉

---

## 🧪 Step 5: Test Your Bot

1. Open Telegram
2. Go to your private channel
3. Send a voice message
4. Bot converts it to MP3!

---

## 🎯 Why This Version Will Work

**Differences from before:**

1. ✅ Simplified bot code (one file: `bot.py`)
2. ✅ Explicitly installs Python 3.10 in nixpacks.toml
3. ✅ Uses `python3` command directly (no confusion)
4. ✅ Clean start (no leftover config issues)
5. ✅ Only 4 files (can't go wrong!)

---

## 💰 Railway Free Tier

Railway gives you **$5 credit per month**.

Your bot will use approximately:
- **$0.20 per day** = **$6 per month**

So you get about **25 days free**, then it costs about **$1-2 for the rest of the month**.

**Much cheaper than $7/month from other providers!**

---

## 🆘 Troubleshooting

### Build fails?

Check the build logs in Railway. If you see an error, send me a screenshot and I'll help!

### Bot doesn't respond?

1. Check Railway logs show: "✅ Ready to convert"
2. Make sure bot is admin in your Telegram channel
3. Make sure TELEGRAM_BOT_TOKEN is set correctly

### Want to update the bot?

1. Edit files locally
2. Commit in GitHub Desktop
3. Push to GitHub
4. Railway auto-deploys!

---

## 📝 Summary

**What you did:**

1. ✅ Deleted old messy repo
2. ✅ Created clean new repo (4 files only)
3. ✅ Deployed to Railway
4. ✅ Added bot token
5. ✅ Bot running 24/7!

**Total time:** 15 minutes
**Cost:** ~$1-2/month after first 25 days free

---

**Now you have a clean, working bot running 24/7 in the cloud! 🚀**
