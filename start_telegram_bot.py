#!/usr/bin/env python3
"""
Start Telegram bot in polling mode.
Run this script and leave it running to receive /search, /help commands.
"""

import os
import sys
import pathlib
from dotenv import load_dotenv

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

load_dotenv()

def start_bot():
    """Start the Telegram bot in polling mode."""
    print("🤖 Starting Telegram Job Search Bot")
    print("=" * 50)
    print("✅ Bot is now listening for commands!")
    print("📱 Try these commands in Telegram:")
    print("   /help   - Show help")
    print("   /search - Run job search")
    print("   /stats  - Show statistics")
    print("   /applied - List applied jobs")
    print("")
    print("🔄 Polling active... Press Ctrl+C to stop")
    print("=" * 50)
    
    from scripts.telegram_bot import telegram_bot
    
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
                        if str(chat_id) == str(os.getenv("TELEGRAM_CHAT_ID", "")):
                            telegram_bot.handle_text_command(message_text, chat_id)
                        else:
                            print(f"   ❌ Ignored - wrong chat ID ({chat_id} vs {os.getenv('TELEGRAM_CHAT_ID', '')})")
                            
            except Exception as e:
                print(f"❌ Polling error: {e}")
                import time
                time.sleep(5)  # Wait before retrying
                
    except KeyboardInterrupt:
        print(f"\n🛑 Bot stopped by user")
        print("✅ Telegram bot polling ended")

if __name__ == "__main__":
    start_bot()
