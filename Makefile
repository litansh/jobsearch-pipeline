.PHONY: crawl score digest run-all test test-coverage install-dev crawl-all track-jobs job-stats clean-jobs
crawl:
	PYTHONPATH=. python scripts/crawl.py
crawl-comprehensive:
	PYTHONPATH=. python scripts/comprehensive_job_search.py
crawl-known-jobs:
	PYTHONPATH=. python scripts/add_known_jobs.py
crawl-all: crawl crawl-comprehensive crawl-known-jobs deduplicate
deduplicate:
	PYTHONPATH=. python scripts/deduplicate_jobs.py
track-jobs:
	PYTHONPATH=. python scripts/job_tracker.py update
job-stats:
	PYTHONPATH=. python scripts/job_tracker.py stats
clean-jobs:
	PYTHONPATH=. python scripts/job_tracker.py clean
score:
	PYTHONPATH=. python scripts/score.py
digest:
	PYTHONPATH=. python scripts/digest.py
run-all: crawl-all track-jobs score digest

# Testing
test:
	pytest
test-coverage:
	pytest --cov=scripts --cov-report=html --cov-report=term-missing
install-dev:
	pip install -r requirements.txt
	pip install pytest-cov
