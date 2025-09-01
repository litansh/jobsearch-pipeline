"""
Flask webhook handler for Telegram bot callbacks.
This can be deployed as a simple web service to handle button presses.
"""

from flask import Flask, request, jsonify
import json
import os
from scripts.telegram_bot import telegram_bot
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Simple secret token for webhook security (optional)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

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
