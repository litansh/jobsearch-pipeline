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
echo "Setting environment variables..."
railway variables set TELEGRAM_BOT_TOKEN=8267615813:AAGmagw5Bh4a6NETvcaIIL-G1_Jv1OLjKoI
railway variables set TELEGRAM_CHAT_ID=277031361

echo "Please set these manually (sensitive):"
echo "railway variables set GITHUB_TOKEN=your_github_token_here"
echo "railway variables set OPENAI_API_KEY=your_openai_key_here"

echo "After setting all variables, redeploy:"
echo "railway up --detach"
