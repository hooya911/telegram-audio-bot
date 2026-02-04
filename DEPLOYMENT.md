# Advanced Deployment Guide - 24/7 Cloud Hosting

This guide covers deploying your bot to run 24/7 on cloud platforms.

---

## 🌐 Option 1: Railway.app (Recommended - Free Tier)

Railway is perfect for this bot - free tier includes 500 hours/month (enough to run 24/7 for 20 days).

### Prerequisites
- GitHub account
- Your bot code in a GitHub repository

### Step-by-Step Railway Deployment

#### 1. Prepare Your Repository

Create these files in your GitHub repo:

**Procfile** (tells Railway how to run your bot):
```
worker: python3 audio_bot.py
```

**runtime.txt** (specifies Python version):
```
python-3.11.0
```

**requirements.txt** (already created):
```
python-telegram-bot==20.7
pydub==0.25.1
```

**railway.json** (optional - configures Railway):
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "numReplicas": 1,
    "sleepApplication": false
  }
}
```

#### 2. Deploy to Railway

1. Go to https://railway.app
2. Click "Start a New Project"
3. Click "Deploy from GitHub repo"
4. Select your repository
5. Click "Deploy Now"

#### 3. Configure Environment Variables

1. In Railway dashboard, click your project
2. Go to "Variables" tab
3. Add variable:
   - Name: `TELEGRAM_BOT_TOKEN`
   - Value: Your bot token from BotFather

#### 4. Install ffmpeg

Railway needs ffmpeg for audio conversion. Add this to your project:

**nixpacks.toml** (place in repository root):
```toml
[phases.setup]
nixPkgs = ["...", "ffmpeg"]
```

OR create **Aptfile**:
```
ffmpeg
```

#### 5. Monitor Your Bot

- Railway dashboard shows logs in real-time
- Check "Deployments" tab to see if bot is running
- Logs will show: "✅ Ready to convert audio files to MP3!"

### Railway Tips

- Free tier: $5 credit/month (plenty for this bot)
- Automatic deployments when you push to GitHub
- Easy to pause/restart from dashboard
- Built-in monitoring and logs

---

## 🔵 Option 2: Render.com (Also Free)

Render offers 750 free hours/month.

### Step-by-Step Render Deployment

#### 1. Create render.yaml

Add this file to your repository:

```yaml
services:
  - type: worker
    name: audio-converter-bot
    env: python
    buildCommand: "pip install -r requirements.txt && apt-get update && apt-get install -y ffmpeg"
    startCommand: "python audio_bot.py"
    envVars:
      - key: TELEGRAM_BOT_TOKEN
        sync: false
```

#### 2. Deploy

1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Blueprint"
4. Connect your GitHub repository
5. Render will detect `render.yaml` and configure automatically

#### 3. Set Environment Variable

1. Go to dashboard → Your service
2. Click "Environment"
3. Add:
   - Key: `TELEGRAM_BOT_TOKEN`
   - Value: Your token

#### 4. Deploy

Click "Manual Deploy" → "Deploy latest commit"

### Render Tips

- Free tier includes 750 hours/month
- Automatically redeploys on git push
- Great logging interface
- Can set up health checks

---

## 💧 Option 3: DigitalOcean ($5/month)

For more control and reliability.

### Step-by-Step DigitalOcean Deployment

#### 1. Create a Droplet

1. Sign up at https://www.digitalocean.com
2. Create a Droplet:
   - Ubuntu 22.04 LTS
   - Basic plan ($5/month)
   - Choose datacenter near you

#### 2. SSH into Your Droplet

```bash
ssh root@your-droplet-ip
```

#### 3. Install Dependencies

```bash
# Update system
apt-get update && apt-get upgrade -y

# Install Python and ffmpeg
apt-get install -y python3 python3-pip ffmpeg

# Install bot dependencies
pip3 install python-telegram-bot pydub
```

#### 4. Upload and Configure Bot

```bash
# Create directory
mkdir -p /opt/telegram-bot
cd /opt/telegram-bot

# Upload your bot files (use scp or git clone)
# If using git:
git clone https://github.com/yourusername/telegram-audio-bot.git .

# Set environment variable
echo 'export TELEGRAM_BOT_TOKEN="your-token-here"' >> /root/.bashrc
source /root/.bashrc
```

#### 5. Create Systemd Service (Run 24/7)

Create `/etc/systemd/system/telegram-bot.service`:

```ini
[Unit]
Description=Telegram Audio Converter Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/telegram-bot
Environment="TELEGRAM_BOT_TOKEN=your-token-here"
ExecStart=/usr/bin/python3 /opt/telegram-bot/audio_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 6. Start the Service

```bash
# Reload systemd
systemctl daemon-reload

# Start bot
systemctl start telegram-bot

# Enable auto-start on boot
systemctl enable telegram-bot

# Check status
systemctl status telegram-bot
```

#### 7. View Logs

```bash
# Real-time logs
journalctl -u telegram-bot -f

# Last 100 lines
journalctl -u telegram-bot -n 100
```

### DigitalOcean Tips

- Most reliable option
- Full control over server
- Can run multiple bots
- Easy to upgrade resources

---

## 🏠 Option 4: Home Server / Raspberry Pi

Run on a Raspberry Pi or old computer at home.

### Raspberry Pi Setup

#### 1. Install Raspberry Pi OS

Use Raspberry Pi Imager to install Raspberry Pi OS Lite

#### 2. SSH to Your Pi

```bash
ssh pi@raspberrypi.local
# Default password: raspberry (change this!)
```

#### 3. Install Dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip ffmpeg git

pip3 install python-telegram-bot pydub
```

#### 4. Download Bot

```bash
cd ~
git clone https://github.com/yourusername/telegram-audio-bot.git
cd telegram-audio-bot
```

#### 5. Create Auto-Start Service

Same as DigitalOcean Step 5 above.

### Home Server Tips

- Zero hosting costs
- Complete privacy
- Great for learning
- Use systemd for auto-start
- Set up port forwarding if needed

---

## 🐳 Option 5: Docker (Any Platform)

Run the bot in a Docker container.

### Dockerfile

Create `Dockerfile` in your repository:

```dockerfile
FROM python:3.11-slim

# Install ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY audio_bot.py .

# Run bot
CMD ["python", "audio_bot.py"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  telegram-bot:
    build: .
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
```

### Run with Docker

```bash
# Build
docker-compose build

# Run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 📊 Comparison Table

| Platform | Cost | Ease | Uptime | Control |
|----------|------|------|--------|---------|
| Railway | Free/$5 | ⭐⭐⭐⭐⭐ | 99%+ | Medium |
| Render | Free | ⭐⭐⭐⭐ | 99%+ | Medium |
| DigitalOcean | $5/mo | ⭐⭐⭐ | 99.9%+ | High |
| Raspberry Pi | One-time | ⭐⭐ | 95%+ | Full |
| Docker | Varies | ⭐⭐⭐⭐ | Varies | Full |

---

## 🎯 Recommended Setup

**For Beginners:** Railway.app
- Easiest setup
- Free tier
- Great dashboard

**For Reliability:** DigitalOcean
- Best uptime
- Full control
- Professional solution

**For Learning:** Raspberry Pi
- Learn server management
- Complete privacy
- One-time cost

---

## 🔐 Security Best Practices

### 1. Protect Your Token

Never commit your token to GitHub:

**.gitignore**:
```
.env
*.log
__pycache__/
```

**.env** (local only):
```
TELEGRAM_BOT_TOKEN=your-token-here
```

### 2. Use Environment Variables

Load from `.env` file:

```python
from dotenv import load_dotenv
load_dotenv()

token = os.getenv('TELEGRAM_BOT_TOKEN')
```

### 3. Enable Firewall

On DigitalOcean/VPS:
```bash
ufw allow ssh
ufw enable
```

### 4. Regular Updates

```bash
apt-get update && apt-get upgrade -y
pip install --upgrade python-telegram-bot pydub
```

---

## 📈 Monitoring and Logs

### View Logs on Railway
- Dashboard → Deployments → View Logs

### View Logs on Render
- Dashboard → Logs tab

### View Logs on DigitalOcean
```bash
journalctl -u telegram-bot -f
```

### Log Rotation

For long-running servers, set up log rotation:

**/etc/logrotate.d/telegram-bot**:
```
/var/log/telegram-bot.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

---

## 🚨 Troubleshooting

### Bot not starting?

**Check logs:**
- Railway: Dashboard logs
- DigitalOcean: `journalctl -u telegram-bot`

**Common issues:**
- Token not set: Check environment variables
- ffmpeg missing: Install ffmpeg
- Port conflicts: Change port or kill conflicting process

### Out of memory?

If bot crashes with memory errors:
- Upgrade to larger plan
- Add swap space (DigitalOcean)
- Process files in smaller chunks

### High CPU usage?

- Normal during conversions
- Reduce concurrent conversions
- Upgrade server resources

---

## 📞 Support

If you run into issues:

1. Check logs for error messages
2. Verify all dependencies installed
3. Test locally first
4. Check platform status pages

---

**Happy deploying! 🚀**
