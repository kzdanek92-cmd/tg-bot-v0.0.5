# 🚀 Render.com Deployment Guide

**Date:** November 15, 2025  
**Bot Version:** v0.0.5  
**Status:** ✅ Ready for Deployment

---

## 📋 Pre-Deployment Checklist

- [x] Code pushed to GitHub: `kzdanek92-cmd/tg-bot-v0.0.5`
- [x] `.env` file cleaned and validated
- [x] `bot.py` syntax verified
- [x] `requirements.txt` up to date
- [x] `Procfile` configured
- [x] `runtime.txt` set to Python 3.11.9

---

## 🎯 Deployment Steps

### Step 1: Go to Render.com
**Link:** https://render.com

### Step 2: Sign In with GitHub
- Click **"Sign in"** or **"Sign up"**
- Select **"Continue with GitHub"**
- Authorize with account `kzdanek92-cmd`

### Step 3: Create Web Service
1. Click **"+ New"** button (top left)
2. Select **"Web Service"**
3. Connect your repo: `tg-bot-v0.0.5`
4. Click **"Connect"**

### Step 4: Configure Service

**Fill in the form:**

| Field | Value |
|-------|-------|
| **Name** | `tg-bot-v0.0.5` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r bot_v0.0.2/requirements.txt` |
| **Start Command** | `cd bot_v0.0.2 && python bot.py` |
| **Plan** | Free (or Starter if needed) |
| **Autodeply** | Yes |

### Step 5: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add each variable one by one:

```
BOT_TOKEN=8377810720:AAH_HA42Cezxe0apHh24DuyDxAiBvPstGHI
SUPABASE_URL=https://wqerdkudikouqgsbsrnj.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndxZXJka3VkaWtvdXFnc2Jzcm5qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwOTUwNzAsImV4cCI6MjA3ODY3MTA3MH0._h90y0lRj_gpZD3WYww95bGFM6m1vDo5N6YHLKmKUPs
CRYPTOBOT_TOKEN=487477:AAtpIbP21izkuwcDPWutkWtRfjlF3Gpbedk
LOG_LEVEL=INFO
```

### Step 6: Deploy
Click **"Create Web Service"**

**Wait for:** ~5-10 minutes for build + deployment

---

## ✅ After Deployment

### Get Your Public URL
Once deployment succeeds, you'll see:
```
https://tg-bot-v0.0.5-xxxx.onrender.com
```

### Update CryptoBot Webhook
1. Go to [CryptoBot Dashboard](https://cryptobot.me/app)
2. Navigate to **Settings → Webhook**
3. Set webhook URL to:
```
https://tg-bot-v0.0.5-xxxx.onrender.com/webhook/cryptobot
```

### Test the Webhook
Send `/start` to your bot in Telegram and verify it responds.

---

## 🔍 Monitoring

### View Logs
- In Render dashboard, click your service
- Go to **"Logs"** tab
- Watch for errors or issues

### Common Issues

| Issue | Solution |
|-------|----------|
| Build fails | Check requirements.txt syntax |
| Bot doesn't respond | Check BOT_TOKEN is correct |
| Webhook errors | Verify webhook URL in CryptoBot |
| Python version mismatch | Ensure runtime.txt = 3.11.9 |

---

## 📞 Support

**Need help?** Contact: [@Danyadlyalubvi2](https://t.me/Danyadlyalubvi2)

**GitHub Issues:** [Issues](https://github.com/kzdanek92-cmd/tg-bot-v0.0.5/issues)

---

**Status:** 🟢 Ready for Render Deployment
