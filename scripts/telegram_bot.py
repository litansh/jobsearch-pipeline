"""
Interactive Telegram bot for job search pipeline.
Handles callback queries for Apply/Ignore buttons and webhook setup.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv
from scripts.utils import create_session
from scripts.job_state import job_state
import urllib.parse
from datetime import timedelta

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT = os.getenv("TELEGRAM_CHAT_ID", "")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.token = TELEGRAM_TOKEN
        self.chat_id = TELEGRAM_CHAT
        self.session = create_session()
        self.base_url = f"https://api.telegram.org/bot{self.token}"
    
    def send_message(self, text: str, reply_markup: Optional[Dict] = None, parse_mode: str = "HTML"):
        """Send a message to Telegram with optional inline keyboard."""
        if not self.token or not self.chat_id:
            print("[WARN] Telegram env vars missing; printing message instead:\n")
            print(text)
            if reply_markup:
                print("Buttons:", reply_markup)
            return False
        
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }
        
        if reply_markup:
            payload["reply_markup"] = reply_markup
        
        try:
            response = self.session.post(url, json=payload, timeout=20)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            print("Message content:")
            print(text)
            return False
    
    def create_job_keyboard(self, job_id: str, job_url: str) -> Dict:
        """Create inline keyboard with Apply/Ignore buttons for a job."""
        # Encode job data for callbacks
        apply_data = f"apply_{job_id}"
        ignore_data = f"ignore_{job_id}"
        
        return {
            "inline_keyboard": [
                [
                    {
                        "text": "🔗 Apply Now",
                        "url": job_url
                    },
                    {
                        "text": "✅ Mark Applied",
                        "callback_data": apply_data
                    }
                ],
                [
                    {
                        "text": "❌ Not Relevant",
                        "callback_data": ignore_data
                    }
                ]
            ]
        }
    
    def send_job_digest(self, jobs: list):
        """Send job digest with interactive buttons."""
        if not jobs:
            self.send_message("No new job matches found today.")
            return
        
        # Send header message
        header = f"<b>🎯 {len(jobs)} New Job Match{'es' if len(jobs) != 1 else ''}</b>\n"
        header += f"<i>Found on {datetime.now().strftime('%Y-%m-%d')}</i>"
        self.send_message(header)
        
        # Send each job as a separate message with buttons
        for job in jobs:
            job_id = job.get("id", "")
            title = job.get("title", "")
            company = job.get("company", "")
            location = job.get("location", "")
            score = job.get("score", 0)
            why_fit = job.get("why_fit", "")
            age_info = f" [Day {job.get('age', 1)}]" if job.get('age') else ""
            url = job.get("url", "")
            
            # Create message text
            message = f"<b>{title}</b>\n"
            message += f"🏢 {company}"
            if location:
                message += f" • 📍 {location}"
            message += f"\n⭐ Score: {score}{age_info}"
            if why_fit:
                message += f"\n💡 {why_fit}"
            
            # Create keyboard
            keyboard = self.create_job_keyboard(job_id, url)
            
            # Send message with buttons
            success = self.send_message(message, reply_markup=keyboard)
            
            if success:
                # Mark as sent to telegram
                job_state.mark_sent_to_telegram(job_id)
        
        print(f"[OK] Sent {len(jobs)} jobs to Telegram with interactive buttons")
    
    def handle_callback_query(self, callback_data: str, callback_query_id: str, 
                            message_id: int, job_title: str = "", job_company: str = ""):
        """Handle button press callbacks."""
        try:
            # Send processing message first
            self.answer_callback_query(callback_query_id, "🔄 Processing...")
            
            # Parse callback data
            if callback_data.startswith("apply_"):
                job_id = callback_data.replace("apply_", "")
                job_state.mark_applied(job_id, job_title, job_company)
                
                # Update message to show it's been applied to
                new_text = f"✅ <b>APPLIED</b>\n<s>{job_title}</s>\n<s>🏢 {job_company}</s>\n\n💪 <i>Great choice! This job won't appear in future digests. Good luck with your application!</i>"
                self.edit_message(message_id, new_text)
                
                # Send follow-up confirmation message
                confirmation = f"✅ <b>Job Marked as Applied</b>\n\n"
                confirmation += f"📝 <b>{job_title}</b> at <b>{job_company}</b> has been marked as applied.\n\n"
                confirmation += f"🎯 This job will no longer appear in your daily digest.\n"
                confirmation += f"🚀 Best of luck with your application!"
                self.send_message(confirmation)
                
            elif callback_data.startswith("ignore_"):
                job_id = callback_data.replace("ignore_", "")
                job_state.mark_ignored(job_id, job_title, job_company, "user_ignored")
                
                # Update message to show it's been ignored
                new_text = f"❌ <b>NOT RELEVANT</b>\n<s>{job_title}</s>\n<s>🏢 {job_company}</s>\n\n🎯 <i>Got it! I'll use this feedback to improve future job matches.</i>"
                self.edit_message(message_id, new_text)
                
                # Send follow-up confirmation message
                confirmation = f"❌ <b>Job Marked as Not Relevant</b>\n\n"
                confirmation += f"📝 <b>{job_title}</b> at <b>{job_company}</b> has been marked as not relevant.\n\n"
                confirmation += f"🎯 This job will no longer appear in your daily digest.\n"
                confirmation += f"🤖 I'll use this feedback to better match your preferences in future searches!"
                self.send_message(confirmation)
                
            else:
                self.answer_callback_query(callback_query_id, "Unknown action")
                
        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            self.answer_callback_query(callback_query_id, "❌ Error processing request")
    
    def edit_message(self, message_id: int, new_text: str):
        """Edit an existing message."""
        url = f"{self.base_url}/editMessageText"
        payload = {
            "chat_id": self.chat_id,
            "message_id": message_id,
            "text": new_text,
            "parse_mode": "HTML"
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=20)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to edit message: {e}")
    
    def answer_callback_query(self, callback_query_id: str, text: str):
        """Answer a callback query (show notification to user)."""
        url = f"{self.base_url}/answerCallbackQuery"
        payload = {
            "callback_query_id": callback_query_id,
            "text": text,
            "show_alert": False
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=20)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to answer callback query: {e}")
    
    def set_webhook(self, webhook_url: str):
        """Set webhook URL for receiving updates."""
        url = f"{self.base_url}/setWebhook"
        payload = {"url": webhook_url}
        
        try:
            response = self.session.post(url, json=payload, timeout=20)
            response.raise_for_status()
            print(f"[OK] Webhook set to: {webhook_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
            return False
    
    def delete_webhook(self):
        """Delete webhook (use polling instead)."""
        url = f"{self.base_url}/deleteWebhook"
        
        try:
            response = self.session.post(url, timeout=20)
            response.raise_for_status()
            print("[OK] Webhook deleted")
            return True
        except Exception as e:
            logger.error(f"Failed to delete webhook: {e}")
            return False
    
    def get_updates(self, offset: int = 0) -> list:
        """Get updates using polling (alternative to webhooks)."""
        url = f"{self.base_url}/getUpdates"
        payload = {"offset": offset, "timeout": 10}
        
        try:
            response = self.session.post(url, json=payload, timeout=15)
            response.raise_for_status()
            return response.json().get("result", [])
        except Exception as e:
            logger.error(f"Failed to get updates: {e}")
            return []

# Global bot instance
telegram_bot = TelegramBot()

def main():
    """CLI interface for telegram bot management."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python telegram_bot.py [test|webhook_set <url>|webhook_delete|poll]")
        return
    
    command = sys.argv[1]
    
    if command == "test":
        # Test sending a message
        telegram_bot.send_message("🤖 Telegram bot test - interactive job search pipeline is working!")
        
    elif command == "webhook_set" and len(sys.argv) > 2:
        webhook_url = sys.argv[2]
        telegram_bot.set_webhook(webhook_url)
        
    elif command == "webhook_delete":
        telegram_bot.delete_webhook()
        
    elif command == "poll":
        # Simple polling example
        print("Starting polling for updates...")
        offset = 0
        while True:
            try:
                updates = telegram_bot.get_updates(offset)
                for update in updates:
                    offset = update["update_id"] + 1
                    
                    # Handle callback queries
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
                        
                        telegram_bot.handle_callback_query(
                            callback_data, callback_query_id, message_id, 
                            job_title, job_company
                        )
                
            except KeyboardInterrupt:
                print("\nStopping polling...")
                break
            except Exception as e:
                logger.error(f"Error in polling: {e}")
                
    else:
        print("Invalid command")

if __name__ == "__main__":
    main()
