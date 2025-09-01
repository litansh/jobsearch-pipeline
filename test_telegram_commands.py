#!/usr/bin/env python3
"""
Test Telegram bot commands locally.
This script helps debug why /search and /help commands aren't working.
"""

import os
import sys
import pathlib
from dotenv import load_dotenv

# Add the project root to Python path
ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

load_dotenv()

def test_telegram_config():
    """Test Telegram bot configuration."""
    print("🤖 Testing Telegram Bot Configuration")
    print("=" * 50)
    
    # Check environment variables
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    github_token = os.getenv("GITHUB_TOKEN", "")
    
    print(f"TELEGRAM_BOT_TOKEN: {'✅ Set' if token else '❌ Missing'}")
    print(f"TELEGRAM_CHAT_ID: {'✅ Set' if chat_id else '❌ Missing'}")
    print(f"GITHUB_TOKEN: {'✅ Set' if github_token else '❌ Missing'}")
    
    if not token or not chat_id:
        print("\n❌ Missing Telegram credentials!")
        print("Add to your .env file:")
        print("TELEGRAM_BOT_TOKEN=your_bot_token_here")
        print("TELEGRAM_CHAT_ID=your_chat_id_here")
        return False
    
    # Test bot connection
    try:
        from scripts.telegram_bot import telegram_bot
        
        print("\n🔄 Testing bot connection...")
        success = telegram_bot.send_message("🧪 <b>Test Message</b>\n\nTesting bot connectivity and command handling!")
        
        if success:
            print("✅ Bot can send messages!")
            
            # Test command handling
            print("\n🔄 Testing command handling...")
            telegram_bot.handle_text_command("/help", int(chat_id))
            print("✅ Help command processed!")
            
            return True
        else:
            print("❌ Bot cannot send messages!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing bot: {e}")
        return False

def check_webhook_status():
    """Check current webhook configuration."""
    print("\n🌐 Checking Webhook Status")
    print("=" * 30)
    
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        print("❌ No token available")
        return
    
    import requests
    try:
        url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
        response = requests.get(url, timeout=10)
        webhook_info = response.json()
        
        if webhook_info.get("ok"):
            webhook_url = webhook_info.get("result", {}).get("url", "")
            if webhook_url:
                print(f"✅ Webhook configured: {webhook_url}")
            else:
                print("❌ No webhook configured - commands won't work!")
                print("\n💡 Solutions:")
                print("1. Set up webhook with a public URL")
                print("2. Run bot in polling mode:")
                print("   python scripts/telegram_bot.py poll")
        else:
            print(f"❌ API Error: {webhook_info}")
            
    except Exception as e:
        print(f"❌ Error checking webhook: {e}")

def show_solutions():
    """Show solutions for fixing Telegram commands."""
    print("\n🔧 How to Fix Telegram Commands")
    print("=" * 40)
    
    print("The /search and /help commands aren't working because:")
    print("1. No webhook is configured AND")
    print("2. Bot is not running in polling mode")
    print()
    print("💡 Solutions:")
    print()
    print("🔄 Option 1: Run bot in polling mode (temporary)")
    print("   python scripts/telegram_bot.py poll")
    print("   (Keep this running in terminal to receive commands)")
    print()
    print("🌐 Option 2: Set up webhook (permanent)")
    print("   - Deploy webhook_handler.py to a public server")
    print("   - Set webhook URL: python scripts/telegram_bot.py webhook_set <url>")
    print()
    print("⚡ Option 3: GitHub Actions integration")
    print("   - Commands trigger GitHub Actions workflows")
    print("   - Results sent back via Telegram")
    print("   - Requires GITHUB_TOKEN in environment")

if __name__ == "__main__":
    config_ok = test_telegram_config()
    check_webhook_status()
    show_solutions()
    
    if config_ok:
        print("\n🚀 Bot configuration is working!")
        print("Try running: python scripts/telegram_bot.py poll")
    else:
        print("\n❌ Fix configuration issues first")
