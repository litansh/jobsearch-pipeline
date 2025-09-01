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

def trigger_github_sync_workflow(callback_data, job_title, job_company):
    """Trigger GitHub Actions workflow to sync job state."""
    if not GITHUB_TOKEN:
        print("[WEBHOOK] No GITHUB_TOKEN configured, skipping GitHub sync")
        return False
    
    # Determine action type
    if callback_data.startswith("apply_"):
        action = "applied"
        job_id = callback_data.replace("apply_", "")
    elif callback_data.startswith("ignore_"):
        action = "ignored"
        job_id = callback_data.replace("ignore_", "")
    elif callback_data.startswith("undo_"):
        action = "undo"
        job_id = callback_data.replace("undo_apply_", "").replace("undo_ignore_", "")
    else:
        return False
    
    # Trigger workflow_dispatch on sync-job-state workflow
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/sync-job-state.yml/dispatches"
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    payload = {
        "ref": "main",
        "inputs": {
            "action": action,
            "job_id": job_id,
            "job_title": job_title,
            "job_company": job_company
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        print(f"[WEBHOOK] Triggered GitHub sync workflow for {action} action on {job_title}")
        return True
    except Exception as e:
        print(f"[WEBHOOK] Failed to trigger GitHub workflow: {e}")
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
            
            # Trigger GitHub Actions workflow to sync job state
            try:
                success = trigger_github_sync_workflow(callback_data, job_title, job_company)
                if success:
                    print("[WEBHOOK] ✅ Triggered GitHub Actions to sync job state")
                else:
                    print("[WEBHOOK] ❌ Failed to trigger GitHub Actions sync")
            except Exception as e:
                print(f"[WEBHOOK] Error triggering GitHub sync: {e}")
        
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
