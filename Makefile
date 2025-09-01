# Job Search Pipeline Makefile

.PHONY: help install test clean run-all crawl crawl-comprehensive crawl-known-jobs deduplicate track-jobs score digest job-stats clean-jobs tailor test-telegram webhook-server

help:  ## Show this help message
	@echo "Job Search Pipeline - Available Commands:"
	@echo "========================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install Python dependencies
	pip install -r requirements.txt

test:  ## Run test suite
	PYTHONPATH=. pytest tests/ -v

test-coverage:  ## Run tests with coverage report
	PYTHONPATH=. pytest tests/ -v --cov=scripts --cov-report=html

clean:  ## Clean temporary files and outputs
	rm -rf outputs/*.jsonl
	rm -rf data/raw/*.json
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Main pipeline commands
run-all: crawl-all deduplicate track-jobs score digest  ## Run complete pipeline

crawl-all: crawl crawl-real crawl-israeli crawl-top-companies crawl-known-jobs  ## Run all crawling methods

crawl:  ## Search Greenhouse/Lever APIs
	PYTHONPATH=. python scripts/crawl.py

crawl-comprehensive:  ## Search Israeli companies + job boards
	PYTHONPATH=. python scripts/comprehensive_job_search.py

crawl-real:  ## Search using real job finder (verified sources)
	PYTHONPATH=. python scripts/real_job_finder.py

crawl-israeli:  ## Search Israeli job platforms (AllJobs, TheMarker, Comeet, etc.)
	PYTHONPATH=. python scripts/israeli_job_sources.py

crawl-top-companies:  ## Search top Israeli tech companies (2025 unicorns & high-growth)
	PYTHONPATH=. python scripts/top_israeli_companies.py

crawl-known-jobs:  ## Add manually verified jobs
	PYTHONPATH=. python scripts/add_known_jobs.py

deduplicate:  ## Remove duplicates and filter roles
	PYTHONPATH=. python scripts/deduplicate_jobs.py

track-jobs:  ## Update job ages and clean old ones
	PYTHONPATH=. python scripts/job_tracker.py update

score:  ## Score jobs against your profile
	PYTHONPATH=. python scripts/score.py

digest:  ## Send Telegram digest with interactive buttons
	PYTHONPATH=. python scripts/digest.py

# Utility commands
job-stats:  ## Show job tracking statistics
	PYTHONPATH=. python scripts/job_tracker.py stats
	PYTHONPATH=. python scripts/job_state.py stats

clean-jobs:  ## Remove jobs older than 14 days
	PYTHONPATH=. python scripts/job_tracker.py clean

tailor:  ## Generate tailored cover letter (usage: make tailor JOB_ID=abc123)
	PYTHONPATH=. python scripts/tailor.py $(JOB_ID)

# Telegram bot commands
test-telegram:  ## Test Telegram bot connection
	PYTHONPATH=. python scripts/telegram_bot.py test

webhook-server:  ## Start webhook server for Telegram callbacks (dev mode)
	PYTHONPATH=. python scripts/webhook_handler.py

webhook-poll:  ## Start polling mode for Telegram callbacks (alternative to webhook)
	PYTHONPATH=. python scripts/telegram_bot.py poll

auto-sync:  ## Start auto-sync of job state to GitHub (run alongside telegram bot)
	PYTHONPATH=. python scripts/auto_sync_state.py start

# GitHub Actions helpers
gh-setup:  ## Setup git config for GitHub Actions
	PYTHONPATH=. python scripts/github_actions_helper.py setup-git

gh-pull-state:  ## Pull job state from repository (for GitHub Actions)
	PYTHONPATH=. python scripts/github_actions_helper.py pull

gh-push-state:  ## Push job state to repository (for GitHub Actions)
	PYTHONPATH=. python scripts/github_actions_helper.py push

gh-init-state:  ## Initialize state files (for GitHub Actions)
	PYTHONPATH=. python scripts/github_actions_helper.py init

gh-summary:  ## Show job state summary (for GitHub Actions)
	PYTHONPATH=. python scripts/github_actions_helper.py summary

# Development commands
lint:  ## Run linting checks
	flake8 scripts/ --max-line-length=120 --ignore=E203,W503

format:  ## Format code with black
	black scripts/ tests/ --line-length=120

# Docker commands (if needed for webhook deployment)
docker-build:  ## Build Docker image for webhook server
	docker build -t jobsearch-webhook .

docker-run:  ## Run webhook server in Docker
	docker run -p 5000:5000 --env-file .env jobsearch-webhook