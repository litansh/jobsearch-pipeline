#!/bin/bash
# Set Railway environment variables via CLI

echo "Setting Railway environment variables..."

# Install Railway CLI if not installed
if ! command -v railway &> /dev/null; then
    echo "Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "Login to Railway (this will open browser):"
railway login

# Link to your project
echo "Linking to your Railway project..."
railway link

# Set environment variables
echo ""
echo "==========================================="
echo "IMPORTANT: Set your environment variables"
echo "==========================================="
echo ""
echo "Run these commands with YOUR OWN credentials:"
echo ""
echo "railway variables set TELEGRAM_BOT_TOKEN=<your_bot_token_from_@BotFather>"
echo "railway variables set TELEGRAM_CHAT_ID=<your_chat_id>"
echo "railway variables set GITHUB_TOKEN=<your_github_token>"
echo "railway variables set OPENAI_API_KEY=<your_openai_key>"
echo ""
echo "To get your Telegram bot token:"
echo "  1. Message @BotFather on Telegram"
echo "  2. Send /newbot"
echo "  3. Follow instructions to get token"
echo ""
echo "To get your Telegram chat ID:"
echo "  1. Message your bot with /start"
echo "  2. Visit: https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates"
echo "  3. Look for 'chat':{'id': YOUR_CHAT_ID}"
echo ""
echo "After setting all variables, deploy:"
echo "railway up --detach"
echo ""
