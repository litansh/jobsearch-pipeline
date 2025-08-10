# Job Search Pipeline

An intelligent, automated pipeline that finds and scores senior DevOps leadership positions from top Israeli tech companies. Features comprehensive job search, AI-powered scoring, Telegram notifications, and job tracking.

## 🎯 **What It Does**

1. **Comprehensive Job Search** - Crawls multiple sources for real DevOps leadership roles:
   - Greenhouse & Lever APIs (50+ companies)
   - Direct career page scraping for Israeli tech companies
   - Research-based verified job openings
   - Job board aggregation (LinkedIn, Glassdoor, Indeed)

2. **Smart Filtering** - Focuses on leadership roles only:
   - ✅ **Head of DevOps/Platform**
   - ✅ **DevOps/Platform Director** 
   - ✅ **DevOps/Platform Manager**
   - ✅ **DevOps/Platform Group Lead**
   - ❌ **Excludes**: Architect, Tech Lead, Team Lead, Principal Engineer

3. **AI-Powered Scoring** - Uses OpenAI embeddings to match jobs against your profile

4. **Daily Digest** - Sends top matches via Telegram with job age tracking

5. **Job Tracking** - Ages jobs daily (1-14 days) and automatically cleans old ones

6. **Deduplication** - Removes duplicate jobs across all sources

## 🚀 **Quick Start**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/litansh/jobsearch-pipeline.git
   cd jobsearch-pipeline
   ```

2. **Set up environment:**
   ```bash
   # Create .env from template
   cp .env.example .env
   
   # Edit .env with your API keys:
   # - OPENAI_API_KEY (required)
   # - TELEGRAM_BOT_TOKEN (optional)
   # - TELEGRAM_CHAT_ID (optional)
   # - NOTION_API_KEY (optional)
   # - NOTION_DB_ID (optional)
   ```

3. **Install dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Customize your profile:**
   - Edit `configs/profile.md` with your experience and preferences
   - Modify `configs/boards.yaml` to add/remove companies or job titles

5. **Run the pipeline:**
   ```bash
   make run-all
   ```

## 📋 **Pipeline Steps**

The pipeline runs these steps in sequence:

```bash
make crawl-all          # Comprehensive job search
make deduplicate        # Remove duplicates and filter roles
make track-jobs         # Update job ages
make score              # AI-powered job scoring
make digest             # Send Telegram digest
```

### **Individual Commands:**

- `make crawl` - Search Greenhouse/Lever APIs
- `make crawl-comprehensive` - Search Israeli companies + job boards
- `make crawl-known-jobs` - Add manually verified jobs
- `make deduplicate` - Remove duplicates and unwanted roles
- `make track-jobs` - Update job ages and clean old ones
- `make score` - Score jobs against your profile
- `make digest` - Send Telegram digest
- `make job-stats` - Show job statistics
- `make clean-jobs` - Remove jobs older than 14 days

## 🤖 **Telegram Integration**

1. **Create a bot** via [@BotFather](https://t.me/botfather)
2. **Get your bot token** and add to `.env`:
   ```
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
3. **Start the bot** by sending `/start` to `@your_bot_name`
4. **Get your chat ID** by visiting:
   ```
   https://api.telegram.org/bot{YOUR_TOKEN}/getUpdates
   ```
5. **Add chat ID** to `.env`:
   ```
   TELEGRAM_CHAT_ID=123456789
   ```

## ⚙️ **Configuration**

### **Environment Variables** (`.env`):
```bash
# Required
OPENAI_API_KEY=sk-...

# Optional - Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCdef...
TELEGRAM_CHAT_ID=123456789

# Optional - Notion
NOTION_API_KEY=secret_...
NOTION_DB_ID=abc123...

# Pipeline Settings
SCORE_THRESHOLD=0.50    # Minimum score for digest (0.0-1.0)
DIGEST_MAX=10          # Max jobs in digest
JOB_MAX_AGE=14         # Days to track jobs
```

### **Job Search Configuration** (`configs/boards.yaml`):
- **Companies**: Add/remove target companies
- **Job Titles**: Modify search criteria
- **Locations**: Filter by location preferences

### **Profile** (`configs/profile.md`):
- Your experience and skills
- Preferred job characteristics
- Used for AI-powered job matching

## 📅 **Automation**

### **Local Cron (Linux/macOS):**
```bash
# Edit crontab
crontab -e

# Add daily run at 08:30 Israel time
30 8 * * * cd $HOME/jobsearch-pipeline && . .venv/bin/activate && make run-all >> cron.log 2>&1
```

### **GitHub Actions:**
The repository includes automated workflows:

- **Daily Job Search** (`.github/workflows/daily.yml`):
  - Runs daily at **05:30 UTC** (≈ 08:30 Israel time)
  - Crawls → scores → sends Telegram digest
  - Optionally pushes to Notion

- **Cover Letter Generator** (`.github/workflows/tailor.yml`):
  - Manual trigger with `job_id`
  - Generates tailored cover letter
  - Uploads as artifact

**Setup GitHub Secrets:**
- `OPENAI_API_KEY`
- `TELEGRAM_BOT_TOKEN` 
- `TELEGRAM_CHAT_ID`
- `NOTION_API_KEY` (optional)
- `NOTION_DB_ID` (optional)

## 🛠️ **Additional Tools**

### **Cover Letter Generation:**
```bash
make tailor JOB_ID=abc123
# Generates tailored cover letter for specific job
```

### **Interview Coaching:**
```bash
python scripts/coach.py
# Generates interview questions and scores your answers
```

### **Network Analysis:**
```bash
python scripts/network.py <company>
# Searches LinkedIn connections for warm intros
```

### **Notion Integration:**
```bash
python scripts/notion_writer.py
# Pushes top matches to Notion database
```

## 📊 **Job Sources**

### **API-Based (Reliable):**
- **Greenhouse**: 30+ companies (Wix, JFrog, Snyk, Redis, etc.)
- **Lever**: 20+ companies (Spotify, etc.)

### **Research-Based (Verified):**
- Manually verified job openings
- Direct career page links
- User-reported positions

### **Comprehensive Search:**
- 50+ Israeli tech companies
- Multiple job boards
- Career page scraping

## 🔍 **Job Filtering**

### **Included Roles:**
- Head of DevOps/Platform
- DevOps/Platform Director
- DevOps/Platform Manager  
- DevOps/Platform Group Lead
- VP of Infrastructure
- Site Reliability Engineering Manager

### **Excluded Roles:**
- Architect
- Tech Lead
- Team Lead
- Principal Engineer
- Staff Engineer
- Senior Engineer

## 📁 **File Structure**

```
jobsearch-pipeline/
├── configs/
│   ├── boards.yaml          # Job search configuration
│   ├── profile.md           # Your profile for AI matching
│   └── prompts/
│       └── cover_note.j2    # Cover letter template
├── scripts/
│   ├── crawl.py             # Main job crawler
│   ├── comprehensive_job_search.py  # Extended search
│   ├── add_known_jobs.py    # Verified job additions
│   ├── deduplicate_jobs.py  # Remove duplicates
│   ├── job_tracker.py       # Job age tracking
│   ├── score.py             # AI job scoring
│   ├── digest.py            # Telegram digest
│   ├── tailor.py            # Cover letter generation
│   ├── coach.py             # Interview coaching
│   ├── network.py           # LinkedIn network search
│   ├── notion_writer.py     # Notion integration
│   └── utils.py             # Shared utilities
├── data/
│   ├── raw/                 # Raw job data
│   └── processed/           # Normalized job data
├── outputs/                 # Generated files
├── tests/                   # Test suite
├── .github/workflows/       # GitHub Actions
├── Makefile                 # Build automation
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables
```

## 🧪 **Testing**

Run the test suite:
```bash
make test              # Run all tests
make test-coverage     # Run with coverage report
```

## 📈 **Monitoring**

### **Job Statistics:**
```bash
make job-stats
# Shows job counts, ages, sources
```

### **Pipeline Logs:**
- Check `cron.log` for local runs
- GitHub Actions logs for automated runs
- Telegram notifications for results

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **"No module named 'scripts'"**:
   - Use `PYTHONPATH=. python scripts/script.py`
   - Or run via `make` commands

2. **Telegram 403/404 errors**:
   - Ensure bot token includes bot ID: `123456789:ABCdef...`
   - Start conversation with bot first
   - Use correct numeric chat ID

3. **No jobs found**:
   - Check `configs/boards.yaml` for companies/titles
   - Lower `SCORE_THRESHOLD` in `.env`
   - Verify API keys are working

4. **GitHub Actions workflow permission error**:
   - Update Personal Access Token to include `workflow` scope
   - Or manually create workflows in GitHub UI

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 **License**

This project is for personal use. Please respect the terms of service of the APIs and websites being accessed.

