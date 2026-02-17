# Design Decisions

This document captures key architectural and technical decisions made during the development of the Job Search Pipeline.

---

## 1. OpenAI Embeddings for Scoring (Not Rule-Based)

### Decision
Use OpenAI embeddings to compute semantic similarity between job descriptions and user profile.

### Context
Need to score jobs on relevance beyond keyword matching. Traditional rule-based systems fail on:
- Synonyms ("DevOps" vs. "Platform Engineering" vs. "SRE")
- Context (title vs. actual responsibilities)
- Soft skills ("leadership", "strategic", "mentorship")

### Alternatives Considered
- **Keyword matching**: Fast but brittle; misses semantic similarity
- **TF-IDF cosine similarity**: Better than keywords but no semantic understanding
- **BERT embeddings (local)**: Free but requires GPU and worse quality than OpenAI
- **GPT-4 classification**: More accurate but 10x more expensive ($0.03/job vs. $0.002)

### Rationale
- OpenAI text-embedding-ada-002 captures semantic meaning
- Fast (100ms per job) and cheap ($0.002 per 1K tokens)
- Works well for job descriptions (trained on internet text)
- Easy to tune threshold without retraining

### Trade-offs
- ✅ High accuracy (semantic understanding)
- ✅ Low cost (~$1-2/month for 500 jobs)
- ✅ No GPU or training required
- ❌ API dependency (requires internet)
- ❌ Less control than local models

### Implementation
```python
# Generate embeddings
profile_embedding = openai.Embedding.create(input=profile_text)
job_embedding = openai.Embedding.create(input=job_description)

# Compute cosine similarity
score = cosine_similarity(profile_embedding, job_embedding)

# Filter by threshold
if score >= SCORE_THRESHOLD:  # default: 0.78
    send_to_digest(job)
```

---

## 2. Telegram Bot (Not Web UI or Email)

### Decision
Use Telegram bot with interactive buttons as primary interface.

### Context
Job search is mobile-first. Users check jobs throughout the day (commute, breaks, evening). Need instant notifications and quick actions (Apply, Snooze, Skip).

### Alternatives Considered
- **Email digest**: Familiar but no interactivity; requires email client
- **Web UI**: Better for detailed views but requires login; not mobile-friendly
- **Slack bot**: Great for teams but many job seekers don't use Slack personally
- **SMS**: Simple but no rich formatting or buttons

### Rationale
- Telegram is mobile-first with push notifications
- Interactive buttons (Apply, Snooze 3d, Skip, Cover Letter) enable quick triage
- End-to-end encryption for privacy
- No setup (just send /start to bot)
- Free and widely used internationally

### Trade-offs
- ✅ Mobile-first, instant notifications
- ✅ Interactive buttons (no typing)
- ✅ Free and private
- ❌ Requires Telegram account (not universal like email)
- ❌ Limited formatting vs. web UI

### Implementation
```python
# Inline keyboard with actions
keyboard = [
    [InlineKeyboardButton("🔗 Apply", url=job_url)],
    [InlineKeyboardButton("⏰ Snooze 3d", callback_data=f"snooze:{job_id}")],
    [InlineKeyboardButton("❌ Skip", callback_data=f"skip:{job_id}")],
    [InlineKeyboardButton("📝 Cover Letter", callback_data=f"cover:{job_id}")]
]
```

---

## 3. Multi-Source Crawling (Not Single Job Board)

### Decision
Crawl 5 different sources in parallel instead of relying on one aggregator (LinkedIn, Indeed).

### Context
No single source has all jobs. Companies post on:
- Their career pages (Greenhouse/Lever)
- Israeli job boards (AllJobs, TheMarker)
- International boards (LinkedIn)
- Niche platforms (AngelList for startups)

### Alternatives Considered
- **LinkedIn only**: Largest database but limited API, high noise
- **Indeed only**: Good aggregator but US-focused, limited Israel coverage
- **Company career pages only**: Most accurate but manual to maintain
- **Recruiter network**: High quality but not scalable

### Rationale
- Each source has unique jobs (20-30% exclusive)
- Deduplication handles overlaps
- Parallel execution (5 crawlers) completes in ~3 minutes
- APIs (Greenhouse, Lever) are reliable and free

### Trade-offs
- ✅ Maximum coverage (50+ companies, multiple boards)
- ✅ Redundancy (if one source fails, others work)
- ✅ Fresh data (APIs update in real-time)
- ❌ Complexity (5 crawlers to maintain)
- ❌ Duplicates (solved with deduplication step)

### Implementation
```bash
# Parallel execution via Make
crawl-all: crawl crawl-real crawl-israeli crawl-top-companies crawl-known-jobs
```

**Sources:**
1. **crawl.py** - Greenhouse/Lever APIs (50+ companies)
2. **real_job_finder.py** - Verified sources (manually curated)
3. **israeli_job_sources.py** - AllJobs, TheMarker, Comeet
4. **top_israeli_companies.py** - 2025 unicorns & high-growth
5. **add_known_jobs.py** - Manual additions (networking, referrals)

---

## 4. GitHub Actions for Automation (Not Cron/Jenkins)

### Decision
Use GitHub Actions to run daily pipeline at 05:30 UTC (08:30 Israel time).

### Context
Need scheduled automation without maintaining servers. Must persist state (seen/snoozed jobs) between runs.

### Alternatives Considered
- **Local cron job**: Simple but requires always-on machine
- **AWS Lambda + CloudWatch**: Powerful but overkill and costs money
- **Heroku Scheduler**: Easy but Heroku pricing increased
- **Jenkins**: Full-featured but operational overhead

### Rationale
- Free (2,000 minutes/month for private repos)
- Git-based state persistence (no database needed)
- Native GitHub integration (secrets, artifacts)
- Workflow UI for debugging
- No infrastructure to maintain

### Trade-offs
- ✅ Zero cost (within free tier)
- ✅ Built-in CI/CD features
- ✅ No servers to manage
- ❌ 6-hour minimum interval (not real-time)
- ❌ GitHub dependency

### Implementation
```yaml
# .github/workflows/daily.yml
on:
  schedule:
    - cron: '30 5 * * *'  # 05:30 UTC daily

jobs:
  search:
    steps:
      - run: make run-all
      - run: git commit -am "Update job state"
      - run: git push
```

**State persistence:**
- `data/job_state.json` - Seen/snoozed/skipped jobs
- Committed to Git after each run
- Pulled at start of next run

---

## 5. Job Age Tracking (1-14 Days)

### Decision
Track job age and auto-clean jobs older than 14 days.

### Context
Stale jobs waste time. Job postings that are 2+ weeks old are often filled or lower priority.

### Alternatives Considered
- **Never clean**: Database grows indefinitely, stale jobs in digest
- **Clean after 7 days**: Too aggressive, miss slow-moving roles
- **Clean after 30 days**: Too long, digest cluttered with old jobs
- **Manual cleanup**: Requires user action, doesn't scale

### Rationale
- 14 days balances freshness and coverage
- Job age shown in digest (helps prioritize new jobs)
- Auto-cleanup prevents database bloat
- Configurable via `JOB_MAX_AGE` env var

### Trade-offs
- ✅ Keeps digest fresh (prioritize new jobs)
- ✅ Auto-cleanup (no manual work)
- ✅ Database stays small
- ❌ May miss slow-hiring companies (14+ days to respond)

### Implementation
```python
# job_tracker.py
for job in jobs:
    job['age_days'] = (today - job['first_seen']).days
    if job['age_days'] > JOB_MAX_AGE:
        delete_job(job)
```

**Digest display:**
```
🆕 Wix - Head of Platform Engineering (1 day old)
📅 Monday.com - Director DevOps (5 days old)
📆 JFrog - DevOps Manager (12 days old)
```

---

## 6. Leadership-Only Filtering (Not All DevOps Roles)

### Decision
Hard-filter for leadership roles (Head of, Director, Manager) and exclude IC roles (Architect, Tech Lead, Principal).

### Context
User wants leadership positions only. Mixed results waste time and reduce signal-to-noise ratio.

### Alternatives Considered
- **No filtering**: Let scoring handle it (lower scores for IC roles)
- **Soft filtering**: Include IC roles but rank lower
- **Configurable**: Let user choose (adds complexity)

### Rationale
- Hard filter improves precision (zero false positives)
- Scoring focuses on leadership job quality (not IC vs. leadership)
- Simpler implementation (boolean filter before scoring)
- User can override via `boards.yaml`

### Trade-offs
- ✅ Zero noise (no IC roles in digest)
- ✅ Faster (skip scoring non-relevant jobs)
- ✅ Clear intent (leadership only)
- ❌ May miss "Principal with management responsibilities" roles
- ❌ Less flexible (requires config change to adjust)

### Implementation
```python
# deduplicate_jobs.py
LEADERSHIP_TITLES = [
    "head of", "director", "manager", "group lead", "vp", "chief"
]

EXCLUDE_TITLES = [
    "architect", "tech lead", "team lead", "principal", "staff", "senior"
]

def is_leadership_role(title):
    title_lower = title.lower()
    if any(keyword in title_lower for keyword in LEADERSHIP_TITLES):
        if not any(keyword in title_lower for keyword in EXCLUDE_TITLES):
            return True
    return False
```

---

## 7. State Persistence in Git (Not Database)

### Decision
Store job state (seen, snoozed, skipped) in `data/job_state.json` committed to Git.

### Context
Need to track user interactions (Snooze, Skip) between pipeline runs. GitHub Actions is stateless.

### Alternatives Considered
- **PostgreSQL**: Full-featured but overkill for simple state
- **SQLite**: Lightweight but requires file storage (not in Git)
- **Redis**: Fast but requires server (costs money)
- **JSON file in Git**: Simple, free, built-in backup

### Rationale
- Zero infrastructure (no database server)
- Git provides version history and backup
- Easy to inspect (human-readable JSON)
- Works with GitHub Actions (pull/push in workflow)

### Trade-offs
- ✅ Zero cost and infrastructure
- ✅ Built-in version control
- ✅ Easy to debug (just open JSON file)
- ❌ Git conflicts if multiple instances run (mitigated by single cron)
- ❌ Not suitable for concurrent access (fine for daily batch)

### Implementation
```python
# job_state.py
def load_state():
    with open('data/job_state.json', 'r') as f:
        return json.load(f)

def save_state(state):
    with open('data/job_state.json', 'w') as f:
        json.dump(state, f, indent=2)

# After user clicks "Snooze"
state['jobs'][job_id]['status'] = 'snoozed'
state['jobs'][job_id]['snoozed_until'] = (today + timedelta(days=3)).isoformat()
save_state(state)
```

---

## 8. Threshold-Based Digest (Not All Jobs)

### Decision
Only send jobs with score >= 0.78 (default) in daily digest, max 10 jobs.

### Context
Sending all jobs (100+ daily) overwhelms user. Need to filter to highest-quality matches.

### Alternatives Considered
- **Top N jobs**: Simple but may include low-quality jobs if few high-quality ones
- **Percentile-based**: Top 10% of jobs (e.g., p90) adapts to distribution
- **Fixed threshold**: Consistent quality bar regardless of day's results

### Rationale
- Fixed threshold (0.78) ensures consistent quality
- Max 10 jobs prevents overwhelm (digestible in 5-10 minutes)
- User can adjust threshold via `SCORE_THRESHOLD` env var
- Jobs below threshold are still tracked (viewable via `make job-stats`)

### Trade-offs
- ✅ Consistent quality (always above threshold)
- ✅ Digestible volume (max 10 jobs)
- ✅ Configurable per user
- ❌ May send 0 jobs if no matches above threshold (by design)
- ❌ Doesn't adapt to distribution (fixed threshold)

### Implementation
```python
# digest.py
SCORE_THRESHOLD = float(os.getenv('SCORE_THRESHOLD', '0.78'))
DIGEST_MAX = int(os.getenv('DIGEST_MAX', '10'))

high_quality_jobs = [
    job for job in scored_jobs
    if job['score'] >= SCORE_THRESHOLD
]

digest_jobs = sorted(high_quality_jobs, key=lambda x: x['score'], reverse=True)[:DIGEST_MAX]
```

**Typical distribution:**
- 500 jobs crawled → 200 after deduplication → 50 after leadership filter → 10 in digest (score >= 0.78)

---

## 9. Cover Letter Generation with GPT-4

### Decision
Generate tailored cover letters on-demand using GPT-4 when user clicks "Cover Letter" button.

### Context
Writing custom cover letters takes 20-30 minutes per job. Users skip applying due to effort.

### Alternatives Considered
- **Generic template**: Fast but low quality, obvious automation
- **GPT-3.5**: Cheaper ($0.001/1K tokens) but lower quality for nuanced writing
- **Claude**: Excellent quality but more expensive ($0.015/1K tokens)
- **No automation**: User writes all cover letters manually

### Rationale
- GPT-4 produces human-quality cover letters (better than GPT-3.5)
- On-demand generation (only for jobs user is interested in) keeps cost low
- Cost: ~$0.05/cover letter (500 tokens at $0.03/1K tokens for GPT-4 Turbo)
- User reviews before sending (no auto-apply)

### Trade-offs
- ✅ High quality (indistinguishable from human)
- ✅ On-demand (only generate when needed)
- ✅ Saves 20-30 min per application
- ❌ Cost ($0.05/cover letter vs. free manual)
- ❌ Requires API key

### Implementation
```python
# tailor.py
def generate_cover_letter(job, profile):
    prompt = f"""
    Write a cover letter for this job:

    Job: {job['title']} at {job['company']}
    Description: {job['description']}

    My profile:
    {profile}

    Requirements:
    - Highlight relevant experience
    - Show enthusiasm for company
    - Keep under 300 words
    - Professional but warm tone
    """

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content
```

---

## 10. Makefile for CLI (Not Python Click/Typer)

### Decision
Use Makefile with simple targets instead of custom CLI tool.

### Context
Need easy command interface for running pipeline steps (crawl, score, digest).

### Alternatives Considered
- **Python Click**: Full-featured CLI framework but requires learning custom commands
- **Python Typer**: Modern Click alternative, similar pros/cons
- **Bash scripts**: Simple but no help text or dependency management
- **Makefile**: Ubiquitous, self-documenting, familiar to engineers

### Rationale
- Make is standard on all Unix systems (no install)
- Self-documenting (`make help` auto-generated from comments)
- Tab completion works out of the box
- Familiar to engineers (standard build tool)
- Simple dependency management (`run-all` depends on steps)

### Trade-offs
- ✅ No dependencies (built into OS)
- ✅ Self-documenting help
- ✅ Familiar to all engineers
- ❌ Less flexible than Click/Typer (no nested commands)
- ❌ Windows requires WSL/Cygwin (not native)

### Implementation
```makefile
help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk ...

run-all: crawl-all deduplicate track-jobs score digest  ## Run complete pipeline

crawl:  ## Search Greenhouse/Lever APIs
	PYTHONPATH=. python scripts/crawl.py
```

---

## 11. JSONL for Job Storage (Not CSV or Database)

### Decision
Store jobs in JSONL (JSON Lines) format in `data/` directory.

### Context
Need to store job data between pipeline runs. Jobs have nested structures (arrays, objects).

### Alternatives Considered
- **CSV**: Simple but doesn't handle nested data (arrays, objects)
- **SQLite**: Structured queries but overkill for append-only data
- **PostgreSQL**: Full-featured but requires server
- **Parquet**: Efficient but requires pandas, overkill

### Rationale
- JSONL is line-delimited (easy to append new jobs)
- Handles nested structures (arrays, objects) natively
- Human-readable for debugging
- Easy to process in Python (json.loads per line)
- Works well with Git (line-by-line diffs)

### Trade-offs
- ✅ Simple and flexible (no schema required)
- ✅ Human-readable for debugging
- ✅ Git-friendly (line diffs)
- ❌ No indexing or queries (full scan required)
- ❌ Larger file size than binary formats

### Implementation
```python
# Write jobs
with open('data/raw/jobs.jsonl', 'a') as f:
    for job in new_jobs:
        f.write(json.dumps(job) + '\n')

# Read jobs
jobs = []
with open('data/raw/jobs.jsonl', 'r') as f:
    for line in f:
        jobs.append(json.loads(line))
```

---

## 12. Interactive Buttons (Not Commands)

### Decision
Use Telegram inline keyboard buttons instead of text commands for job actions.

### Context
Users triage jobs quickly on mobile. Typing commands is slow and error-prone.

### Alternatives Considered
- **Text commands**: `/snooze job123` - flexible but slow to type
- **Reply keyboard**: Persistent buttons but clutter chat
- **Inline buttons**: Contextual, disappear after use

### Rationale
- One tap vs. typing (10x faster)
- No typos (button click is precise)
- Contextual (buttons attached to specific job)
- Clean (buttons disappear after action)

### Trade-offs
- ✅ Fast (one tap)
- ✅ No typos
- ✅ Mobile-friendly
- ❌ Limited to 8 buttons per message
- ❌ Callback data size limit (64 bytes)

### Implementation
```python
keyboard = [
    [InlineKeyboardButton("🔗 Apply", url=job['url'])],
    [InlineKeyboardButton("⏰ Snooze 3d", callback_data=f"snooze:{job['id']}")],
    [InlineKeyboardButton("❌ Skip", callback_data=f"skip:{job['id']}")],
    [InlineKeyboardButton("📝 Cover Letter", callback_data=f"cover:{job['id']}")]
]

bot.send_message(
    chat_id=CHAT_ID,
    text=format_job(job),
    reply_markup=InlineKeyboardMarkup(keyboard)
)
```

---

## Future Decisions to Make

### 1. Salary Estimation
**When:** Phase 2
**Question:** Train ML model or use external API (Glassdoor, Payscale)?

### 2. Auto-Apply
**When:** Phase 3
**Question:** How much automation? Require user confirmation per application?

### 3. Multi-User Support
**When:** Phase 4
**Question:** Add user accounts and database, or keep as single-user tool?

---

## References

- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Make Manual](https://www.gnu.org/software/make/manual/)

---

**Last Updated:** February 17, 2026
**Maintained By:** Author
