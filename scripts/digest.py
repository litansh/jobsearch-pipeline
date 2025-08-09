import os, json, pathlib
from dotenv import load_dotenv
from scripts.utils import create_session, safe_get

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
    rows = []
    with open(SCORES, "r", encoding="utf-8") as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except:
                pass
    rows = [r for r in rows if r.get("score",0) >= THRESHOLD]
    rows = rows[:MAX_ITEMS]
    if not rows:
        send_telegram("No matches above threshold today. Try lowering SCORE_THRESHOLD.")
        return
    lines = ["<b>Top job matches for today</b>"]
    for r in rows:
        age_info = f" [Day {r.get('age', 1)}]" if r.get('age') else ""
        lines.append(f"• <b>{r['title']}</b> @ {r['company']} ({r.get('location','')}) — score {r['score']}{age_info}\n  {r['url']}\n  Why: {r['why_fit']}")
    send_telegram("\n\n".join(lines))
    print(f"[OK] Sent digest with {len(rows)} items.")

if __name__ == "__main__":
    main()
