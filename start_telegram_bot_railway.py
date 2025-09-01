#!/usr/bin/env python3
"""
Start Telegram bot for Railway deployment.
This version doesn't rely on .env files - uses Railway environment variables directly.
"""

import os
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Don't load .env on Railway - use environment variables directly
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT = os.environ.get("TELEGRAM_CHAT_ID", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

def start_bot():
    """Start the Telegram bot in polling mode for Railway."""
    print("🚂 Starting Telegram Bot on Railway")
    print("=" * 50)
    
    # Debug environment variables
    print("Environment Check:")
    print(f"TELEGRAM_BOT_TOKEN: {'✅ Set' if TELEGRAM_TOKEN else '❌ Missing'}")
    print(f"TELEGRAM_CHAT_ID: {'✅ Set' if TELEGRAM_CHAT else '❌ Missing'}")
    print(f"GITHUB_TOKEN: {'✅ Set' if GITHUB_TOKEN else '❌ Missing'}")
    print(f"OPENAI_API_KEY: {'✅ Set' if OPENAI_KEY else '❌ Missing'}")
    
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT:
        print("❌ Missing required Telegram credentials!")
        print("Add these environment variables in Railway:")
        print("- TELEGRAM_BOT_TOKEN")
        print("- TELEGRAM_CHAT_ID")
        return
    
    print("✅ Bot is now listening for commands!")
    print("📱 Try these commands in Telegram:")
    print("   /help   - Show help")
    print("   /search - Run job search")
    print("   /stats  - Show statistics")
    print("")
    print("🔄 Polling active...")
    print("=" * 50)
    
    # Set environment variables for the telegram_bot module
    os.environ["TELEGRAM_BOT_TOKEN"] = TELEGRAM_TOKEN
    os.environ["TELEGRAM_CHAT_ID"] = TELEGRAM_CHAT
    if GITHUB_TOKEN:
        os.environ["GITHUB_TOKEN"] = GITHUB_TOKEN
    if OPENAI_KEY:
        os.environ["OPENAI_API_KEY"] = OPENAI_KEY
    
    from scripts.telegram_bot import telegram_bot
    
    print(f"Bot URL: {telegram_bot.base_url}")
    
    offset = 0
    
    try:
        while True:
            try:
                updates = telegram_bot.get_updates(offset)
                
                for update in updates:
                    offset = update["update_id"] + 1
                    
                    # Handle callback queries (button presses)
                    if "callback_query" in update:
                        callback_query = update["callback_query"]
                        callback_data = callback_query.get("data", "")
                        callback_query_id = callback_query["id"]
                        message = callback_query.get("message", {})
                        message_id = message.get("message_id", 0)
                        message_text = message.get("text", "")
                        
                        # Extract job info from message
                        lines = message_text.split('\n')
                        job_title = lines[0].replace('<b>', '').replace('</b>', '') if lines else ""
                        job_company = ""
                        for line in lines:
                            if line.startswith('🏢'):
                                job_company = line.replace('🏢 ', '').split(' •')[0]
                                break
                        
                        print(f"🔘 Button pressed: {callback_data}")
                        telegram_bot.handle_callback_query(
                            callback_data, callback_query_id, message_id, 
                            job_title, job_company
                        )
                    
                    # Handle text messages (commands)
                    if "message" in update and "text" in update["message"]:
                        message_text = update["message"]["text"].strip()
                        chat_id = update["message"]["chat"]["id"]
                        user = update["message"].get("from", {})
                        
                        print(f"📨 Command received: '{message_text}' from {user.get('first_name', 'Unknown')}")
                        
                        # Only respond to messages from the configured chat
                        if str(chat_id) == str(TELEGRAM_CHAT):
                            telegram_bot.handle_text_command(message_text, chat_id)
                        else:
                            print(f"   ❌ Ignored - wrong chat ID ({chat_id} vs {TELEGRAM_CHAT})")
                            
            except Exception as e:
                print(f"❌ Polling error: {e}")
                import time
                time.sleep(5)  # Wait before retrying
                
    except KeyboardInterrupt:
        print(f"\n🛑 Bot stopped")

if __name__ == "__main__":
    start_bot()
