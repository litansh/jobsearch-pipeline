#!/usr/bin/env python3
"""
Debug script to check Railway environment variables.
"""

import os
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

def debug_env():
    """Debug environment variables on Railway."""
    print("🔍 Railway Environment Debug")
    print("=" * 40)
    
    # Check if .env loading works
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ dotenv imported and loaded")
    except Exception as e:
        print(f"❌ dotenv error: {e}")
    
    # Check environment variables
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    github_token = os.getenv("GITHUB_TOKEN", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    
    print(f"TELEGRAM_BOT_TOKEN: {'✅ Set (' + token[:20] + '...)' if token else '❌ Missing'}")
    print(f"TELEGRAM_CHAT_ID: {'✅ Set (' + chat_id + ')' if chat_id else '❌ Missing'}")
    print(f"GITHUB_TOKEN: {'✅ Set (' + github_token[:20] + '...)' if github_token else '❌ Missing'}")
    print(f"OPENAI_API_KEY: {'✅ Set (' + openai_key[:20] + '...)' if openai_key else '❌ Missing'}")
    
    # Test Telegram bot initialization
    if token and chat_id:
        try:
            from scripts.telegram_bot import TelegramBot
            bot = TelegramBot()
            print(f"✅ Bot initialized")
            print(f"Bot base URL: {bot.base_url}")
            
            # Test a simple API call
            import requests
            url = f"https://api.telegram.org/bot{token}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                bot_info = response.json()
                print(f"✅ Bot API working: @{bot_info['result']['username']}")
            else:
                print(f"❌ Bot API error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Bot initialization error: {e}")
    else:
        print("❌ Cannot test bot - missing credentials")
    
    print("\n🚀 If all variables show as set, try redeploying Railway")

if __name__ == "__main__":
    debug_env()
