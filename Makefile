.PHONY: crawl score digest run-all test test-coverage install-dev
crawl:
	python scripts/crawl.py
score:
	python scripts/score.py
digest:
	python scripts/digest.py
run-all: crawl score digest

# Testing
test:
	pytest
test-coverage:
	pytest --cov=scripts --cov-report=html --cov-report=term-missing
install-dev:
	pip install -r requirements.txt
	pip install pytest-cov
