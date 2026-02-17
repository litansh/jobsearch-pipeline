# Job Search Pipeline

**AI-powered job automation that searches 50+ companies, scores 500+ roles using OpenAI embeddings, and delivers daily Telegram digests—saving 40+ hours/month on job hunting.**

---

## 🎯 Why It Exists

**Problem:** Manually searching for senior DevOps/Platform leadership roles is time-consuming and inefficient. Job boards mix junior and senior roles, companies post on different platforms, and tracking applications across sites is tedious.

**Solution:** Automated pipeline that crawls multiple sources (Greenhouse, Lever APIs, Israeli job boards), filters for leadership-only roles, scores against your profile using AI embeddings, tracks job age (1-14 days), and sends daily Telegram digests with interactive buttons.

---

## 🚀 What It Does

- **Multi-Source Crawling:** Searches 50+ companies via Greenhouse/Lever APIs, Israeli job boards (AllJobs, TheMarker, Comeet), top tech companies (2025 unicorns), and manually verified openings
- **Leadership Filtering:** Only Head of DevOps/Platform, Director, Manager, Group Lead roles—excludes Architect, Tech Lead, Principal Engineer
- **AI-Powered Scoring:** OpenAI embeddings compare job descriptions to your profile (`configs/profile.md`) with 0.0-1.0 similarity scores
- **Job Age Tracking:** Tracks jobs 1-14 days, auto-cleans old listings, shows age in digest
- **Deduplication:** Removes duplicate jobs across all sources
- **Telegram Digest:** Daily top 10 matches with interactive buttons (Apply, Snooze, Skip, Cover Letter)
- **Cover Letter Generation:** AI-generated tailored cover letters per job (`make tailor JOB_ID=xxx`)
- **GitHub Actions Automation:** Runs daily at 05:30 UTC (08:30 Israel time) with state persistence

---

## 🏗️ Architecture

### Components

```
Job Sources → Crawlers → Deduplication → Scoring Engine → Job Tracker → Telegram Bot
     ↓             ↓            ↓              ↓              ↓             ↓
Greenhouse    5 crawlers   Remove dups   OpenAI API    Age 1-14 days   Daily digest
Lever APIs    (parallel)   Filter roles  Embeddings    Auto-clean     Interactive
Israeli       Real jobs                  Profile match                 buttons
Job Boards    Top companies
```

### Data Flow

1. **Crawl (5 parallel crawlers):**
   - `crawl.py` - Greenhouse/Lever APIs (50+ companies)
   - `comprehensive_job_search.py` - Israeli job boards
   - `real_job_finder.py` - Verified job sources
   - `israeli_job_sources.py` - AllJobs, TheMarker, Comeet
   - `top_israeli_companies.py` - 2025 unicorns & high-growth
   - `add_known_jobs.py` - Manual additions

2. **Deduplicate:** Remove duplicates by URL/title, filter out non-leadership roles

3. **Track:** Update job ages (1-14 days), clean jobs > 14 days old

4. **Score:** OpenAI embeddings match against `configs/profile.md`, output 0.0-1.0 scores

5. **Digest:** Send top 10 jobs (score > 0.78) via Telegram with interactive buttons

6. **State Sync:** Auto-sync job state to GitHub (seen/snoozed/skipped) every 5 minutes

---

## 🏃 Quickstart

### Demo Mode (No API Keys Required)

**Test the pipeline structure without live searches:**

```bash
git clone https://github.com/litansh/jobsearch-pipeline.git
cd jobsearch-pipeline
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run tests to verify everything works
make test

# Check sample data processing
cat test_data/sample_jobs.jsonl | head -5
```

**What works without API keys:**
- ✅ Deduplication logic
- ✅ Job filtering by seniority/keywords
- ✅ Job tracking (age calculation)
- ✅ Makefile commands
- ❌ Live job searches (requires network)
- ❌ AI-powered scoring (requires OpenAI API key)
- ❌ Telegram notifications (requires bot token)

---

### Local Run (Full Pipeline)

**Production setup with OpenAI API:**

```bash
git clone https://github.com/litansh/jobsearch-pipeline.git
cd jobsearch-pipeline

# Setup environment
cp .env.example .env
# Edit .env: Add OPENAI_API_KEY (required)
# TELEGRAM_* variables are optional

# Install dependencies
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Customize profile
# Edit configs/profile.md with your experience and preferences

# Run full pipeline
make run-all
```

**Time:** < 5 minutes
**Output:** `outputs/scored.jsonl` + Telegram digest (if configured)

---

### Scheduled Run (GitHub Actions)

**Automated daily searches without local setup:**

1. **Fork the repository** on GitHub
2. **Add secrets** (Settings → Secrets and variables → Actions):
   - `OPENAI_API_KEY` (required) - Get from https://platform.openai.com/api-keys
   - `TELEGRAM_BOT_TOKEN` (optional) - Get from @BotFather on Telegram
   - `TELEGRAM_CHAT_ID` (optional) - Your Telegram user ID
3. **Enable Actions** (Actions tab → Enable workflows)
4. **Customize profile:** Edit `configs/profile.md` via GitHub web editor
5. **Done!** Pipeline runs daily at 9 AM UTC

**GitHub will:**
- Search 50+ companies automatically
- Score jobs against your profile
- Send Telegram digest with top matches
- Store results in repository (outputs/ branch)

---

### One-Command Setup

```bash
git clone https://github.com/litansh/jobsearch-pipeline.git
cd jobsearch-pipeline

# Setup environment
cp .env.example .env
# Edit .env: Add OPENAI_API_KEY (required), TELEGRAM_BOT_TOKEN + CHAT_ID (optional)

# Install dependencies
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Customize profile
# Edit configs/profile.md with your experience and preferences

# Run pipeline
make run-all
```

**Time:** < 5 minutes
**Output:** `outputs/scored.jsonl` + Telegram digest (if configured)

---

### Step-by-Step (Manual Control)

```bash
# 1. Search all sources (parallel execution)
make crawl-all

# 2. Remove duplicates and filter roles
make deduplicate

# 3. Update job ages
make track-jobs

# 4. Score against profile
make score

# 5. Send Telegram digest
make digest

# 6. View statistics
make job-stats
```

---

### Telegram Bot Setup (Optional)

**Get daily digests with interactive buttons:**

```bash
# 1. Create bot via @BotFather on Telegram
# 2. Copy bot token to .env:
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# 3. Get your chat ID:
# Visit: https://api.telegram.org/bot{YOUR_TOKEN}/getUpdates
# Send /start to your bot, then refresh the URL above
TELEGRAM_CHAT_ID=123456789

# 4. Test connection
make test-telegram

# 5. Run pipeline (will send digest)
make run-all
```

**Digest includes:**
- Top 10 jobs scored above threshold (default: 0.78)
- Company, role, location, salary (if available)
- Job age (1-14 days)
- Similarity score (0.0-1.0)
- Interactive buttons: Apply, Snooze 3d, Skip, Cover Letter

---

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# ===== REQUIRED =====
# OpenAI API Key for embeddings and LLM
OPENAI_API_KEY=sk-xxx

# ===== OPTIONAL - Telegram =====
# Get from @BotFather
TELEGRAM_BOT_TOKEN=123456789:ABCdef...
TELEGRAM_CHAT_ID=123456789

# ===== OPTIONAL - Notion =====
# Create integration at notion.so/my-integrations
NOTION_API_KEY=secret_xxx
NOTION_DB_ID=abc123...

# ===== PIPELINE SETTINGS =====
# Minimum score for digest (0.0-1.0)
SCORE_THRESHOLD=0.78

# Max jobs in digest
DIGEST_MAX=10
```

### Configuration Files

**configs/profile.md** - Your experience and preferences
```markdown
# About Me
Senior DevOps/Platform Engineering Leader with 10+ years...

# Skills
- Kubernetes, AWS, Terraform, Python, Go...

# Preferences
- Leadership roles (Head of, Director, Manager)
- Remote or Tel Aviv
- Salary: $180K+
```

**configs/boards.yaml** - Target companies and titles
```yaml
companies:
  - wix
  - jfrog
  - monday
  # ... 50+ companies

titles:
  - "Head of DevOps"
  - "Director of Platform Engineering"
  - "DevOps Manager"
  # ...

exclude_titles:
  - "Architect"
  - "Tech Lead"
  - "Principal Engineer"
```

---

## 📊 Observability

### Job Statistics

```bash
make job-stats
```

**Output:**
```
Job Search Pipeline Statistics
==============================

Total Jobs: 127
New (1-3 days): 42
Recent (4-7 days): 31
Older (8-14 days): 54

By Source:
  Greenhouse: 45
  Lever: 23
  Israeli Boards: 35
  Top Companies: 18
  Manual: 6

By Status:
  Unseen: 89
  Snoozed: 12
  Skipped: 26
  Applied: 0

Average Score: 0.72
Top Score: 0.94 (Wix - Head of Platform Engineering)
```

---

### Logs

**Log files:**
- `logs/crawl.log` - Crawler activity and errors
- `logs/score.log` - Scoring results
- `logs/digest.log` - Telegram send status

**View logs:**
```bash
tail -f logs/crawl.log
tail -f logs/score.log
```

---

### GitHub Actions Monitoring

**Daily workflow runs at 05:30 UTC:**
- View runs: https://github.com/litansh/jobsearch-pipeline/actions
- Job summary in workflow output
- Failed runs trigger email notification

**Workflow steps:**
1. Pull job state from Git
2. Run full pipeline (crawl-all → score → digest)
3. Push updated state to Git
4. Report summary (X new jobs, Y sent to Telegram)

---

## 🗺️ Roadmap

### ✅ Phase 1: Core Pipeline (Complete)
- [x] Multi-source crawling (Greenhouse, Lever, Israeli boards)
- [x] AI-powered scoring with OpenAI embeddings
- [x] Job age tracking and auto-cleanup
- [x] Telegram bot with interactive buttons
- [x] GitHub Actions automation
- [x] State persistence and sync

### 🔄 Phase 2: Enhanced Intelligence (In Progress)
- [ ] Salary estimation using ML (based on title, company, location)
- [ ] Company growth prediction (funding, headcount trends)
- [ ] Application success rate tracking (did I get interview?)
- [ ] Interview coaching with AI (company-specific prep)
- [ ] Network analysis (LinkedIn connections at target companies)

### 📋 Phase 3: Advanced Automation (Q2 2026)
- [ ] Auto-apply with generated cover letters (user approval required)
- [ ] Resume tailoring per job (keyword optimization)
- [ ] Follow-up reminders (no response after 7 days → nudge)
- [ ] Interview scheduler integration (Calendly auto-booking)

### 🚀 Phase 4: Multi-User Platform (Q3 2026)
- [ ] Web UI for non-technical users
- [ ] Multi-profile support (different roles, locations)
- [ ] Job marketplace (share verified openings)
- [ ] Recruiter matching (warm intros via network)

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

Copyright (c) 2026 Litan Shamir

---

## ⚠️ Disclaimer

**Responsible Use:**
- This tool automates job searching, not applications—you control when to apply
- Respect job board terms of service (rate limiting, scraping policies)
- Do not spam companies with automated applications
- Review all cover letters before sending

**Data Privacy:**
- Your profile and job data stay local (not shared)
- OpenAI processes job descriptions for scoring (transient, not stored)
- Telegram bot uses end-to-end encryption
- GitHub state file is private (configure repo as private)

**Cost:**
- OpenAI API: ~$1-2/month (500 jobs × $0.002/1K tokens)
- Telegram: Free
- GitHub Actions: Free (2,000 minutes/month for private repos)

**Support:**
- Open issues on GitHub for bugs
- See `docs/design.md` for architecture decisions
- Pull requests welcome

---

## 📚 Additional Documentation

- [Makefile](Makefile) - All available commands
- [.env.example](.env.example) - Environment variable template
- [configs/profile.md](configs/profile.md) - Your profile template
- [configs/boards.yaml](configs/boards.yaml) - Company and title configuration
- [docs/design.md](docs/design.md) - Architecture and design decisions
- [.github/workflows/](.github/workflows/) - GitHub Actions automation

---

## 🛠️ Development

### Run Tests

```bash
make test                # Run test suite
make test-coverage      # Run with coverage report
```

### Local Telegram Bot (Webhook Mode)

```bash
# Start webhook server (for testing Telegram callbacks)
make webhook-server

# Or use polling mode (simpler, no webhooks)
make webhook-poll
```

### Linting & Formatting

```bash
make lint    # Check code style
make format  # Auto-format with Black
```

---

**Built with:** Python 3.9+ | OpenAI API | Telegram Bot API | GitHub Actions | YAML | Makefile
