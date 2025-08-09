import os, json, pathlib
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()
ROOT = pathlib.Path(__file__).resolve().parents[1]
SCORES = ROOT / "outputs" / "scores.jsonl"

NOTION_API_KEY = os.getenv("NOTION_API_KEY","")
NOTION_DB_ID   = os.getenv("NOTION_DB_ID","")

def ensure_notion():
    if not NOTION_API_KEY or not NOTION_DB_ID:
        raise SystemExit("NOTION_API_KEY / NOTION_DB_ID missing. Skipping.")
    return Client(auth=NOTION_API_KEY)

def upsert_row(notion, row):
    props = {
        "Title": {"title": [{"text": {"content": row.get("title","")}}]},
        "Company": {"rich_text": [{"text": {"content": row.get("company","")}}]},
        "Location": {"rich_text": [{"text": {"content": row.get("location","")}}]},
        "Score": {"number": float(row.get("score",0))},
        "URL": {"url": row.get("url","")},
        "Status": {"select": {"name": "New"}},
        "Why": {"rich_text": [{"text": {"content": row.get("why_fit","")}}]},
    }
    notion.pages.create(parent={"database_id": NOTION_DB_ID}, properties=props)

def main():
    notion = ensure_notion()
    rows = []
    with open(SCORES, "r", encoding="utf-8") as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except:
                pass
    # Only push top 15 to avoid clutter
    rows = sorted(rows, key=lambda r: r.get("score",0), reverse=True)[:15]
    for r in rows:
        upsert_row(notion, r)
    print(f"[OK] Pushed {len(rows)} rows to Notion.")

if __name__ == "__main__":
    main()
