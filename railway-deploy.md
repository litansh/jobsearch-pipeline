# 🚂 Deploy Telegram Bot to Railway.app

## 📋 **Prerequisites**
- GitHub account (you have this ✅)
- Railway.app account (free to start)
- Your Telegram bot already works locally ✅

## 🚀 **Step-by-Step Deployment**

### **Step 1: Create Railway Files** ✅
I've created these files for you:
- `Procfile` - Tells Railway how to run the bot
- `railway.json` - Railway configuration
- `runtime.txt` - Python version specification

### **Step 2: Push to GitHub**
```bash
# Add the new Railway files
git add Procfile railway.json runtime.txt start_telegram_bot.py TELEGRAM_DEPLOYMENT_OPTIONS.md

# Commit the changes
git commit -m "🚂 Add Railway.app deployment configuration

- Add Procfile for Railway deployment
- Add railway.json with worker configuration  
- Add start_telegram_bot.py for 24/7 polling
- Add deployment documentation"

# Push to GitHub
git push origin main
```

### **Step 3: Deploy to Railway**

1. **Go to Railway.app**: https://railway.app
2. **Sign up/Login** with your GitHub account
3. **Create New Project** → **Deploy from GitHub repo**
4. **Select** your `jobsearch-pipeline` repository
5. **Deploy** (it will auto-detect Python and install dependencies)

### **Step 4: Add Environment Variables**
In Railway dashboard, go to your project → **Variables** tab:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here  
GITHUB_TOKEN=your_github_token_here
OPENAI_API_KEY=your_openai_key_here
```

### **Step 5: Start the Service**
- Railway will automatically deploy and start your bot
- Check the **Logs** tab to see if it's running
- Look for: "🤖 Starting Telegram Job Search Bot"

## 🎯 **After Deployment**

### **Test Your Bot**
Send these commands in Telegram:
- `/help` - Should work immediately
- `/search` - Will trigger GitHub Actions
- `/stats` - Show job statistics

### **Monitor Your Bot**
- **Railway Dashboard**: Check logs and metrics
- **GitHub Actions**: Monitor triggered workflows
- **Telegram**: Bot should respond 24/7

## 💰 **Pricing**
- **Free Tier**: 500 hours/month (enough for 24/7 bot)
- **Pro Plan**: $5/month for unlimited usage
- **Your bot**: Very lightweight, should stay in free tier

## 🔧 **Troubleshooting**

### **Bot Not Starting**
Check Railway logs for:
- Missing environment variables
- Python import errors
- Network connectivity issues

### **Commands Not Working**
- Verify `TELEGRAM_CHAT_ID` matches your chat
- Check GitHub token has repository permissions
- Ensure bot is added to your Telegram chat

### **GitHub Actions Not Triggering**
- Verify `GITHUB_TOKEN` has `repo` and `actions` permissions
- Check if repository dispatch events are enabled

## 📊 **Expected Behavior**
1. **Bot runs 24/7** on Railway
2. **Receives commands** instantly via polling
3. **Triggers GitHub Actions** for job searches
4. **Sends results** back to Telegram with buttons
5. **Auto-restarts** if it crashes

## 🚀 **Ready to Deploy?**
Run the git commands in Step 2, then follow the Railway setup!
