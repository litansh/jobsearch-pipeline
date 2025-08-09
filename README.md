# Job Search Pipeline (MVP)

A tiny, agent-lite pipeline that:
1) **Crawls** select careers pages (Greenhouse / Lever) for Israel-based senior DevOps leadership roles.
2) **Scores** matches against your profile using embeddings.
3) **Sends a Telegram** morning digest of the top roles.

## Quick Start

1. Clone/download this folder.
2. Create `.env` from `.env.example` and fill tokens:
   - `OPENAI_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
3. (Optional) Edit `configs/boards.yaml` to add companies/sources/titles.
4. Create a Python venv and install deps:
   ```bash
   python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
5. Put your master bullets in `configs/profile.md` (already has a starter from this chat).
6. Run the pipeline:
   ```bash
   make run-all
   ```
   This will crawl → score → send a Telegram digest of top matches.

## Schedule (Linux/macOS cron)
Edit your crontab (`crontab -e`) to run daily at 08:30 Israel time:
```
30 8 * * * cd $HOME/jobsearch-pipeline && . .venv/bin/activate && make run-all >> cron.log 2>&1
```

## Notes
- This MVP intentionally uses **public JSON APIs** for Greenhouse & Lever (safer than scraping restricted sites).
- Add/remove companies and search titles in `configs/boards.yaml`.
- All found jobs are saved to `data/raw/YYYY-MM-DD.json` and a normalized `data/processed/jobs.jsonl`.
- Tweak the similarity threshold in `scripts/score.py` to show more/fewer jobs in the digest.

## Extras
- `scripts/notion_writer.py` — push top matches to a Notion database (set NOTION_API_KEY/NOTION_DB_ID).
- `scripts/network.py <company>` — search your LinkedIn connections CSV (`data/connections.csv`) for warm-intro candidates.
- `scripts/coach.py` — generate tailored interview questions and score one of your answers.

## GitHub Actions (CI/CD)
Create repository secrets: `OPENAI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` (and optionally `NOTION_API_KEY`, `NOTION_DB_ID`).  
The following workflows are included:
- `.github/workflows/daily.yml` — runs daily at **05:30 UTC** (≈ 08:30 Israel) to crawl → score → send a Telegram digest, then (optionally) push top matches to Notion.
- `.github/workflows/tailor.yml` — manual trigger with `job_id`; produces a tailored cover note and uploads it as an artifact + step summary.

