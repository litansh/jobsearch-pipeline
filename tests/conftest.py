import pytest
import tempfile
import pathlib
import json
import os
from unittest.mock import patch


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield pathlib.Path(tmp_dir)


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        'OPENAI_API_KEY': 'test-openai-key',
        'TELEGRAM_BOT_TOKEN': 'test-telegram-token',
        'TELEGRAM_CHAT_ID': 'test-chat-id',
        'NOTION_API_KEY': 'test-notion-key',
        'NOTION_DB_ID': 'test-db-id',
        'SCORE_THRESHOLD': '0.75',
        'DIGEST_MAX': '5'
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def sample_greenhouse_response():
    """Sample Greenhouse API response."""
    return {
        "jobs": [
            {
                "title": "Head of DevOps",
                "absolute_url": "https://boards.greenhouse.io/monday/jobs/123",
                "location": {"name": "Tel Aviv, Israel"},
                "updated_at": "2024-01-15T10:00:00Z"
            },
            {
                "title": "Senior Software Engineer",
                "absolute_url": "https://boards.greenhouse.io/monday/jobs/124",
                "location": {"name": "New York, USA"},
                "updated_at": "2024-01-15T09:00:00Z"
            }
        ]
    }


@pytest.fixture
def sample_lever_response():
    """Sample Lever API response."""
    return [
        {
            "text": "Director of Platform Engineering",
            "hostedUrl": "https://jobs.lever.co/lemonade/456",
            "categories": {
                "team": "Engineering",
                "location": "Tel Aviv, Israel"
            },
            "createdAt": 1705320000000,
            "descriptionPlain": "Lead our platform engineering team..."
        }
    ]


@pytest.fixture
def sample_jobs_data():
    """Sample processed jobs data."""
    return [
        {
            "id": "job123",
            "title": "Head of DevOps",
            "company": "monday",
            "location": "Tel Aviv, Israel",
            "url": "https://boards.greenhouse.io/monday/jobs/123",
            "source": "greenhouse",
            "posted_at": "2024-01-15T10:00:00Z",
            "jd": "Lead DevOps team..."
        },
        {
            "id": "job456",
            "title": "Director of Platform",
            "company": "lemonade",
            "location": "Tel Aviv, Israel", 
            "url": "https://jobs.lever.co/lemonade/456",
            "source": "lever",
            "posted_at": "1705320000000",
            "jd": "Lead our platform engineering team..."
        }
    ]


@pytest.fixture
def sample_scores_data():
    """Sample scored jobs data."""
    return [
        {
            "id": "job123",
            "title": "Head of DevOps",
            "company": "monday",
            "location": "Tel Aviv, Israel",
            "url": "https://boards.greenhouse.io/monday/jobs/123",
            "score": 0.85,
            "why_fit": "senior leadership scope, platform reliability focus"
        },
        {
            "id": "job456", 
            "title": "Director of Platform",
            "company": "lemonade",
            "location": "Tel Aviv, Israel",
            "url": "https://jobs.lever.co/lemonade/456",
            "score": 0.72,
            "why_fit": "strong profile alignment"
        }
    ]
