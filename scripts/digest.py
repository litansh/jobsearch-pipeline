import os, json, pathlib
from dotenv import load_dotenv
from scripts.utils import create_session, safe_get
from scripts.job_state import job_state
from scripts.telegram_bot import telegram_bot

load_dotenv()
ROOT = pathlib.Path(__file__).resolve().parents[1]
SCORES = ROOT / "outputs" / "scores.jsonl"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN","")
TELEGRAM_CHAT = os.getenv("TELEGRAM_CHAT_ID","")

THRESHOLD = float(os.getenv("SCORE_THRESHOLD","0.78"))
MAX_ITEMS = int(os.getenv("DIGEST_MAX","10"))

def send_telegram(text: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT:
        print("[WARN] Telegram env vars missing; printing digest instead:\n")
        print(text)
        return
    session = create_session()
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    try:
        r = session.post(url, json=payload, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print(f"[WARN] Failed to send Telegram message: {e}")
        print("Digest content:")
        print(text)

def main():
    # Load all scored jobs
    rows = []
    with open(SCORES, "r", encoding="utf-8") as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except:
                pass
    
    # Filter by score threshold
    rows = [r for r in rows if r.get("score",0) >= THRESHOLD]
    
    # Filter out jobs that were already sent, applied to, or ignored
    unsent_rows = job_state.get_unsent_jobs(rows)
    
    if not unsent_rows:
        # Check if there were any jobs above threshold at all
        if not rows:
            send_telegram("No matches above threshold today. Try lowering SCORE_THRESHOLD.")
        else:
            print(f"[INFO] Found {len(rows)} jobs above threshold, but all were already sent/applied/ignored")
        return
    
    # Limit to MAX_ITEMS
    unsent_rows = unsent_rows[:MAX_ITEMS]
    
    # Send processing notification
    if unsent_rows:
        processing_msg = f"🔄 <b>Processing {len(unsent_rows)} new job match{'es' if len(unsent_rows) != 1 else ''}...</b>\n"
        processing_msg += f"<i>Found {len(rows)} total jobs above threshold, sending {len(unsent_rows)} new ones</i>"
        telegram_bot.send_message(processing_msg)
    
    # Send interactive digest using new telegram bot
    telegram_bot.send_job_digest(unsent_rows)
    
    # Send completion summary
    if unsent_rows:
        summary_msg = f"✅ <b>Job Digest Complete!</b>\n\n"
        summary_msg += f"📊 <b>Summary:</b>\n"
        summary_msg += f"• {len(unsent_rows)} new jobs sent\n"
        summary_msg += f"• {len(rows) - len(unsent_rows)} jobs already seen/processed\n"
        summary_msg += f"• {len(rows)} total jobs above score threshold\n\n"
        summary_msg += f"💡 <b>Next Steps:</b>\n"
        summary_msg += f"• Click 🔗 <i>Apply Now</i> to open job applications\n"
        summary_msg += f"• Click ✅ <i>Mark Applied</i> after applying\n"
        summary_msg += f"• Click ❌ <i>Not Relevant</i> to hide irrelevant jobs\n\n"
        summary_msg += f"🤖 I'll remember your choices and won't show these jobs again!"
        telegram_bot.send_message(summary_msg)
    
    print(f"[OK] Sent {len(unsent_rows)} new jobs to Telegram (out of {len(rows)} total above threshold)")

if __name__ == "__main__":
    main()
