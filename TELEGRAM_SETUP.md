# Interactive Telegram Bot Setup

The job search pipeline now includes interactive Telegram functionality with buttons to manage job applications.

## 🎯 New Features

### ✅ **Issues Fixed:**
1. **No more duplicate jobs daily** - Jobs are tracked and only sent once
2. **Better job links** - Links go directly to application pages  
3. **Interactive buttons** - Apply/Ignore buttons for each job

### 🔘 **Interactive Buttons:**
Each job message now includes:
- **🔗 Apply Now** - Opens job application in browser
- **✅ Mark Applied** - Marks job as applied (won't appear again)
- **❌ Not Relevant** - Ignores job (won't appear again)

## 🚀 Quick Setup

### Option 1: Polling Mode (Easiest)
No webhook setup needed - bot checks for button presses periodically:

```bash
# Test the bot
make test-telegram

# Start polling for button presses (run in background)
nohup make webhook-poll > telegram_bot.log 2>&1 &
```

### Option 2: Webhook Mode (Advanced)
For real-time button responses, set up a webhook server:

```bash
# Start webhook server (for development)
make webhook-server

# Or deploy to a cloud service and set webhook URL
python scripts/telegram_bot.py webhook_set https://your-domain.com/webhook
```

## 📱 How It Works

1. **Daily digest runs** (via GitHub Actions or cron)
2. **New jobs are sent** with interactive buttons
3. **Click buttons to manage jobs:**
   - Apply Now → Opens job page + marks as applied
   - Not Relevant → Hides job permanently
4. **No duplicates** - Applied/ignored jobs won't appear again

## 🔧 Environment Variables

Make sure your `.env` includes:
```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdef...
TELEGRAM_CHAT_ID=123456789

# Optional: For webhook security
WEBHOOK_SECRET=your_secret_key
```

## 📊 Job State Management

Track your job application status:

```bash
# View statistics
make job-stats

# Manual job state management
python scripts/job_state.py stats
python scripts/job_state.py applied <job_id>
python scripts/job_state.py ignored <job_id>
```

## 🤖 Bot Commands

```bash
# Test bot connection
make test-telegram

# Start polling mode (checks for button presses)
make webhook-poll

# Start webhook server (real-time responses)
make webhook-server

# Set webhook URL (for production deployment)
python scripts/telegram_bot.py webhook_set https://your-domain.com/webhook

# Remove webhook (switch back to polling)
python scripts/telegram_bot.py webhook_delete
```

## 🔄 Migration from Old System

Your existing pipeline will automatically:
1. ✅ Stop sending duplicate jobs
2. ✅ Add interactive buttons to new jobs  
3. ✅ Track job states (applied/ignored)
4. ✅ Continue working with GitHub Actions

No configuration changes needed - just update and run!

## 🐛 Troubleshooting

**Bot not responding to buttons:**
- Make sure polling is running: `make webhook-poll`
- Check bot logs: `tail -f telegram_bot.log`

**Still getting duplicate jobs:**
- Job state file might be missing - run `make digest` once to initialize
- Check `data/processed/job_state.json` exists

**Buttons not showing:**
- Update your bot token - old bots might not support inline keyboards
- Test with: `make test-telegram`
