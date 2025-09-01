"""
Flask webhook handler for Telegram bot callbacks.
This can be deployed as a simple web service to handle button presses.
"""

from flask import Flask, request, jsonify
import json
import os
from scripts.telegram_bot import telegram_bot
from dotenv import load_dotenv
import requests
import subprocess

load_dotenv()

app = Flask(__name__)

# Simple secret token for webhook security (optional)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")  # Personal Access Token
GITHUB_REPO = "litansh/jobsearch-pipeline"

def update_github_job_state(callback_data, job_title, job_company):
    """Directly update job state in GitHub repository via API."""
    if not GITHUB_TOKEN:
        print("[WEBHOOK] No GITHUB_TOKEN configured, skipping GitHub sync")
        return False
    
    try:
        # Get current job_state.json from GitHub
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/data/processed/job_state.json"
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # File exists, get current content
            file_data = response.json()
            import base64
            current_content = base64.b64decode(file_data['content']).decode('utf-8')
            current_state = json.loads(current_content)
            sha = file_data['sha']
        else:
            # File doesn't exist, create new
            current_state = {
                "applied": {},
                "ignored": {},
                "sent_to_telegram": {},
                "last_updated": "2025-09-01"
            }
            sha = None
        
        # Apply the action to the state
        if callback_data.startswith("apply_"):
            job_id = callback_data.replace("apply_", "")
            current_state["applied"][job_id] = {
                "date": "2025-09-01",
                "title": job_title,
                "company": job_company
            }
            action_desc = f"marked {job_title} @ {job_company} as applied"
            
        elif callback_data.startswith("ignore_"):
            job_id = callback_data.replace("ignore_", "")
            current_state["ignored"][job_id] = {
                "date": "2025-09-01", 
                "title": job_title,
                "company": job_company,
                "reason": "user_ignored"
            }
            action_desc = f"marked {job_title} @ {job_company} as not relevant"
            
        elif callback_data.startswith("undo_apply_"):
            job_id = callback_data.replace("undo_apply_", "")
            if job_id in current_state["applied"]:
                del current_state["applied"][job_id]
            action_desc = f"undid applied marking for {job_title} @ {job_company}"
            
        elif callback_data.startswith("undo_ignore_"):
            job_id = callback_data.replace("undo_ignore_", "")
            if job_id in current_state["ignored"]:
                del current_state["ignored"][job_id]
            action_desc = f"undid ignore marking for {job_title} @ {job_company}"
        else:
            return False
        
        # Update the file in GitHub
        new_content = json.dumps(current_state, indent=2, ensure_ascii=False)
        encoded_content = base64.b64encode(new_content.encode('utf-8')).decode('utf-8')
        
        commit_data = {
            "message": f"🔘 Telegram sync: {action_desc}",
            "content": encoded_content,
            "branch": "main"
        }
        
        if sha:
            commit_data["sha"] = sha
        
        response = requests.put(url, headers=headers, json=commit_data, timeout=10)
        response.raise_for_status()
        
        print(f"[WEBHOOK] ✅ Successfully synced to GitHub: {action_desc}")
        return True
        
    except Exception as e:
        print(f"[WEBHOOK] ❌ Failed to sync to GitHub: {e}")
        return False

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming webhook from Telegram."""
    try:
        # Verify secret token if configured
        if WEBHOOK_SECRET:
            token = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
            if token != WEBHOOK_SECRET:
                return jsonify({"error": "Unauthorized"}), 401
        
        # Parse update
        update = request.get_json()
        
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
            
            # Handle the callback
            telegram_bot.handle_callback_query(
                callback_data, callback_query_id, message_id, 
                job_title, job_company
            )
            
            # Directly update GitHub job state file
            try:
                success = update_github_job_state(callback_data, job_title, job_company)
                if success:
                    print("[WEBHOOK] ✅ Job state synced directly to GitHub")
                else:
                    print("[WEBHOOK] ❌ Failed to sync job state to GitHub")
            except Exception as e:
                print(f"[WEBHOOK] Error syncing to GitHub: {e}")
        
        return jsonify({"ok": True})
        
    except Exception as e:
        print(f"[ERROR] Webhook error: {e}")
        return jsonify({"error": "Internal error"}), 500

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "telegram_webhook"})

if __name__ == "__main__":
    # For development only - use gunicorn or similar for production
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
