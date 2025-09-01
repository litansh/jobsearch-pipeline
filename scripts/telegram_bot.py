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
import requests

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT = os.getenv("TELEGRAM_CHAT_ID", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO = "litansh/jobsearch-pipeline"

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
                
                # Create undo keyboard
                undo_keyboard = {
                    "inline_keyboard": [
                        [
                            {
                                "text": "↩️ Undo (Mark as Not Applied)",
                                "callback_data": f"undo_apply_{job_id}"
                            }
                        ]
                    ]
                }
                
                logger.info(f"Created undo keyboard for job {job_id}: {undo_keyboard}")
                
                # Update message to show it's been applied to
                new_text = f"✅ <b>APPLIED</b>\n<s>{job_title}</s>\n<s>🏢 {job_company}</s>\n\n💪 <i>Great choice! This job won't appear in future digests. Good luck with your application!</i>"
                logger.info(f"Editing message {message_id} with undo keyboard")
                self.edit_message(message_id, new_text, reply_markup=undo_keyboard)
                
                # Trigger GitHub sync via repository dispatch
                self.trigger_github_sync("applied", job_id, job_title, job_company)
                
                # Send follow-up confirmation message
                confirmation = f"✅ <b>Job Marked as Applied</b>\n\n"
                confirmation += f"📝 <b>{job_title}</b> at <b>{job_company}</b> has been marked as applied.\n\n"
                confirmation += f"🎯 This job will no longer appear in your daily digest.\n"
                confirmation += f"🚀 Best of luck with your application!\n\n"
                confirmation += f"🤖 <i>Automatically syncing with GitHub Actions...</i>"
                self.send_message(confirmation)
                
            elif callback_data.startswith("ignore_"):
                job_id = callback_data.replace("ignore_", "")
                job_state.mark_ignored(job_id, job_title, job_company, "user_ignored")
                
                # Create undo keyboard
                undo_keyboard = {
                    "inline_keyboard": [
                        [
                            {
                                "text": "↩️ Undo (Mark as Relevant)",
                                "callback_data": f"undo_ignore_{job_id}"
                            }
                        ]
                    ]
                }
                
                # Update message to show it's been ignored
                new_text = f"❌ <b>NOT RELEVANT</b>\n<s>{job_title}</s>\n<s>🏢 {job_company}</s>\n\n🎯 <i>Got it! I'll use this feedback to improve future job matches.</i>"
                self.edit_message(message_id, new_text, reply_markup=undo_keyboard)
                
                # Trigger GitHub sync via repository dispatch  
                self.trigger_github_sync("ignored", job_id, job_title, job_company)
                
                # Send follow-up confirmation message
                confirmation = f"❌ <b>Job Marked as Not Relevant</b>\n\n"
                confirmation += f"📝 <b>{job_title}</b> at <b>{job_company}</b> has been marked as not relevant.\n\n"
                confirmation += f"🎯 This job will no longer appear in your daily digest.\n"
                confirmation += f"🤖 I'll use this feedback to better match your preferences in future searches!\n\n"
                confirmation += f"🤖 <i>Automatically syncing with GitHub Actions...</i>"
                self.send_message(confirmation)
                
            elif callback_data.startswith("undo_apply_"):
                job_id = callback_data.replace("undo_apply_", "")
                success = job_state.remove_applied(job_id)
                
                if success:
                    # Remove the undo button and show success
                    new_text = f"↩️ <b>UNDONE</b>\n{job_title}\n🏢 {job_company}\n\n✅ <i>Removed from applied list. This job may appear in future digests again.</i>"
                    self.edit_message(message_id, new_text)
                    self.answer_callback_query(callback_query_id, "✅ Undone! Job removed from applied list")
                else:
                    self.answer_callback_query(callback_query_id, "❌ Could not undo - job not found in applied list")
                    
            elif callback_data.startswith("undo_ignore_"):
                job_id = callback_data.replace("undo_ignore_", "")
                success = job_state.remove_ignored(job_id)
                
                if success:
                    # Remove the undo button and show success
                    new_text = f"↩️ <b>UNDONE</b>\n{job_title}\n🏢 {job_company}\n\n✅ <i>Removed from ignored list. This job may appear in future digests again.</i>"
                    self.edit_message(message_id, new_text)
                    self.answer_callback_query(callback_query_id, "✅ Undone! Job removed from ignored list")
                else:
                    self.answer_callback_query(callback_query_id, "❌ Could not undo - job not found in ignored list")
                
            else:
                self.answer_callback_query(callback_query_id, "Unknown action")
                
        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            self.answer_callback_query(callback_query_id, "❌ Error processing request")
    
    def edit_message(self, message_id: int, new_text: str, reply_markup: Optional[Dict] = None):
        """Edit an existing message."""
        url = f"{self.base_url}/editMessageText"
        payload = {
            "chat_id": self.chat_id,
            "message_id": message_id,
            "text": new_text,
            "parse_mode": "HTML"
        }
        
        if reply_markup:
            payload["reply_markup"] = reply_markup
        
        try:
            response = self.session.post(url, json=payload, timeout=20)
            response.raise_for_status()
            logger.info(f"Successfully edited message {message_id}")
        except Exception as e:
            logger.error(f"Failed to edit message {message_id}: {e}")
            logger.error(f"Payload was: {payload}")
    
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
    
    def trigger_github_sync(self, action: str, job_id: str, job_title: str, job_company: str):
        """Trigger GitHub repository dispatch to sync job state."""
        if not GITHUB_TOKEN:
            logger.warning("No GITHUB_TOKEN configured, skipping GitHub sync")
            return False
        
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"
            headers = {
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            payload = {
                "event_type": "telegram_job_action",
                "client_payload": {
                    "action": action,
                    "job_id": job_id,
                    "job_title": job_title,
                    "job_company": job_company
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Successfully triggered GitHub sync: {action} for {job_title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to trigger GitHub sync: {e}")
            return False
    
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
    
    def handle_text_command(self, message_text: str, chat_id: int):
        """Handle text commands from Telegram."""
        command = message_text.lower().strip()
        
        if command in ["/start", "/help"]:
            help_text = """🤖 <b>Job Search Pipeline Bot</b>

<b>Available Commands:</b>
🔍 <code>/search</code> - Run complete job search pipeline
🔍 <code>/crawl</code> - Quick search (Greenhouse/Lever only)
📊 <code>/stats</code> - Show job statistics
📝 <code>/applied</code> - List applied jobs
❌ <code>/ignored</code> - List ignored jobs
🧹 <code>/clean</code> - Clean old jobs
🔄 <code>/help</code> - Show this help

<b>Interactive Features:</b>
• Click 🔗 <i>Apply Now</i> to open job applications
• Click ✅ <i>Mark Applied</i> after applying
• Click ❌ <i>Not Relevant</i> to hide jobs
• Click ↩️ <i>Undo</i> to reverse actions

All button clicks automatically sync with GitHub Actions! 🚀"""
            
            self.send_message(help_text)
            
        elif command == "/search":
            self.send_message("🔍 <b>Starting Complete Job Search...</b>\n\n⏳ This will take 2-3 minutes. I'll send you results when ready!")
            self.trigger_github_search_pipeline("full")
            
        elif command == "/crawl":
            self.send_message("🔍 <b>Starting Quick Job Search...</b>\n\n⏳ Searching Greenhouse/Lever APIs...")
            self.trigger_github_search_pipeline("quick")
            
        elif command == "/stats":
            stats = job_state.get_stats()
            stats_text = f"""📊 <b>Job Statistics</b>

✅ <b>Applied to:</b> {stats['applied']} jobs
❌ <b>Ignored:</b> {stats['ignored']} jobs  
📤 <b>Sent to Telegram:</b> {stats['sent_to_telegram']} jobs
📅 <b>Last updated:</b> {stats['last_updated']}

Use /applied or /ignored to see specific jobs."""
            self.send_message(stats_text)
            
        elif command == "/applied":
            self.list_job_category("applied")
            
        elif command == "/ignored":
            self.list_job_category("ignored")
            
        elif command == "/clean":
            self.send_message("🧹 <b>Cleaning Old Jobs...</b>\n\n⏳ Removing jobs older than 14 days...")
            self.trigger_github_search_pipeline("clean")
            
        else:
            self.send_message("❓ Unknown command. Send /help to see available commands.")
    
    def list_job_category(self, category: str):
        """List jobs from a specific category (applied/ignored)."""
        if category == "applied":
            jobs_dict = job_state.data.get("applied", {})
            title = "📝 Applied Jobs"
            emoji = "✅"
        else:
            jobs_dict = job_state.data.get("ignored", {})
            title = "❌ Ignored Jobs"
            emoji = "❌"
        
        if not jobs_dict:
            self.send_message(f"{emoji} <b>{title}</b>\n\nNo {category} jobs found.")
            return
        
        message = f"{emoji} <b>{title}</b>\n\n"
        for job_id, job_info in list(jobs_dict.items())[:10]:  # Limit to 10
            message += f"• <b>{job_info.get('title', 'Unknown')}</b>\n"
            message += f"  🏢 {job_info.get('company', 'Unknown')}\n"
            message += f"  📅 {job_info.get('date', 'Unknown')}\n"
            if category == "ignored":
                message += f"  💭 {job_info.get('reason', 'Unknown')}\n"
            message += f"  🆔 <code>{job_id[:12]}...</code>\n\n"
        
        if len(jobs_dict) > 10:
            message += f"... and {len(jobs_dict) - 10} more jobs"
        
        self.send_message(message)
    
    def trigger_github_search_pipeline(self, search_type: str):
        """Trigger GitHub Actions to run job search pipeline."""
        if not GITHUB_TOKEN:
            self.send_message("❌ GitHub integration not configured. Cannot trigger remote search.")
            return False
        
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"
            headers = {
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            payload = {
                "event_type": "telegram_search_command",
                "client_payload": {
                    "search_type": search_type,
                    "triggered_by": "telegram_bot"
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Successfully triggered GitHub search pipeline: {search_type}")
            
            if search_type == "full":
                self.send_message("✅ <b>Job Search Pipeline Started!</b>\n\n🔍 Running comprehensive search across all sources...\n📱 You'll receive results in 2-3 minutes!")
            elif search_type == "quick":
                self.send_message("✅ <b>Quick Search Started!</b>\n\n🔍 Searching Greenhouse/Lever APIs...\n📱 You'll receive results shortly!")
            elif search_type == "clean":
                self.send_message("✅ <b>Job Cleanup Started!</b>\n\n🧹 Removing old jobs from database...")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to trigger GitHub search pipeline: {e}")
            self.send_message(f"❌ <b>Failed to start job search:</b>\n\n{str(e)}")
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
                    
                    # Handle text messages (commands)
                    if "message" in update and "text" in update["message"]:
                        message_text = update["message"]["text"].strip()
                        chat_id = update["message"]["chat"]["id"]
                        
                        # Only respond to messages from the configured chat
                        if str(chat_id) == str(TELEGRAM_CHAT):
                            telegram_bot.handle_text_command(message_text, chat_id)
                    
            except KeyboardInterrupt:
                print("\nStopping polling...")
                break
            except Exception as e:
                logger.error(f"Error in polling: {e}")
                    
    else:
        print("Invalid command")

if __name__ == "__main__":
    main()
