#!/usr/bin/env python3
"""
Simple test to check if Railway environment variables are working.
"""

import os
import sys

def test_vars():
    """Test Railway environment variables."""
    print("🚂 Railway Environment Variable Test")
    print("=" * 50)
    
    # Test each variable
    vars_to_check = [
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID", 
        "GITHUB_TOKEN",
        "OPENAI_API_KEY"
    ]
    
    all_good = True
    
    for var in vars_to_check:
        value = os.environ.get(var, "")
        if value:
            print(f"✅ {var}: Set ({value[:20]}...)")
        else:
            print(f"❌ {var}: Missing")
            all_good = False
    
    print("=" * 50)
    
    if all_good:
        print("✅ All variables set! Bot should work now.")
        
        # Test Telegram API
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        if token:
            import requests
            try:
                url = f"https://api.telegram.org/bot{token}/getMe"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    bot_info = response.json()
                    print(f"✅ Telegram API working: @{bot_info['result']['username']}")
                else:
                    print(f"❌ Telegram API error: {response.status_code}")
            except Exception as e:
                print(f"❌ Telegram API test failed: {e}")
    else:
        print("❌ Missing variables! Add them in Railway dashboard.")
        print("Variables tab → Add Variable → Name/Value → Save")
    
    print("\nIf all variables show ✅, the bot should work!")

if __name__ == "__main__":
    test_vars()
