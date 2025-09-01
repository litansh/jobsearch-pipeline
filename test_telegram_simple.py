#!/usr/bin/env python3
"""
Simple Telegram bot test that shows exactly what's happening with commands.
"""

import os
import sys
import pathlib
from dotenv import load_dotenv

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

load_dotenv()

def test_simple_commands():
    """Test Telegram commands with immediate feedback."""
    print("🤖 Testing Telegram Commands")
    print("=" * 40)
    
    from scripts.telegram_bot import telegram_bot
    
    # Test 1: Send a simple message
    print("1. Testing basic message sending...")
    success = telegram_bot.send_message("🧪 <b>Command Test Active</b>\n\nBot is ready to receive commands!")
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 2: Process help command manually
    print("\n2. Testing /help command processing...")
    try:
        chat_id = int(os.getenv("TELEGRAM_CHAT_ID", ""))
        telegram_bot.handle_text_command("/help", chat_id)
        print("   Result: ✅ Help command processed")
    except Exception as e:
        print(f"   Result: ❌ Error: {e}")
    
    # Test 3: Process stats command
    print("\n3. Testing /stats command...")
    try:
        telegram_bot.handle_text_command("/stats", chat_id)
        print("   Result: ✅ Stats command processed")
    except Exception as e:
        print(f"   Result: ❌ Error: {e}")
    
    print("\n✅ Commands should now appear in your Telegram chat!")
    print("If you don't see them, the issue might be:")
    print("- Chat ID mismatch")
    print("- Bot not added to the chat")
    print("- Telegram API issues")
    
    return True

def start_simple_polling():
    """Start a simple polling loop with debug output."""
    print("\n🔄 Starting Simple Polling Mode")
    print("=" * 40)
    print("Send /help or /search in Telegram now...")
    print("Press Ctrl+C to stop")
    
    from scripts.telegram_bot import telegram_bot
    
    offset = 0
    update_count = 0
    
    try:
        while True:
            updates = telegram_bot.get_updates(offset)
            
            if updates:
                print(f"\n📨 Received {len(updates)} update(s)")
                
            for update in updates:
                update_count += 1
                offset = update["update_id"] + 1
                
                print(f"Update #{update_count}: {update.get('update_id')}")
                
                # Handle text messages (commands)
                if "message" in update and "text" in update["message"]:
                    message_text = update["message"]["text"].strip()
                    chat_id = update["message"]["chat"]["id"]
                    user = update["message"].get("from", {})
                    
                    print(f"  📝 Message: '{message_text}'")
                    print(f"  👤 From: {user.get('first_name', 'Unknown')} (ID: {chat_id})")
                    print(f"  🎯 Expected Chat ID: {os.getenv('TELEGRAM_CHAT_ID', '')}")
                    
                    # Only respond to messages from the configured chat
                    if str(chat_id) == str(os.getenv("TELEGRAM_CHAT_ID", "")):
                        print(f"  ✅ Processing command: {message_text}")
                        telegram_bot.handle_text_command(message_text, chat_id)
                    else:
                        print(f"  ❌ Ignoring - wrong chat ID")
                
                # Handle callback queries (button presses)
                elif "callback_query" in update:
                    callback_query = update["callback_query"]
                    callback_data = callback_query.get("data", "")
                    print(f"  🔘 Button pressed: {callback_data}")
                    # Handle callback as before...
                    
    except KeyboardInterrupt:
        print(f"\n🛑 Stopped polling. Processed {update_count} updates.")
    except Exception as e:
        print(f"\n❌ Polling error: {e}")

if __name__ == "__main__":
    # First test commands manually
    test_simple_commands()
    
    # Then start polling to receive live commands
    input("\nPress Enter to start live polling (or Ctrl+C to exit)...")
    start_simple_polling()
