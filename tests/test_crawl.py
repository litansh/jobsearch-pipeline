import pytest
import json
import responses
from unittest.mock import patch, mock_open
from scripts.crawl import (
    greenhouse_company_jobs, lever_company_jobs,
    normalize_gh, normalize_lever,
    title_matches, location_matches, main
)
from scripts.utils import create_session


class TestCrawl:
    """Test crawling functionality."""
    
    @responses.activate
    def test_greenhouse_company_jobs(self, sample_greenhouse_response):
        """Test Greenhouse API call."""
        responses.add(
            responses.GET,
            'https://boards-api.greenhouse.io/v1/boards/monday/jobs',
            json=sample_greenhouse_response,
            status=200
        )
        
        session = create_session()
        jobs = greenhouse_company_jobs('monday', session)
        
        assert len(jobs) == 2
        assert jobs[0]['title'] == 'Head of DevOps'
        assert jobs[1]['title'] == 'Senior Software Engineer'
    
    @responses.activate
    def test_lever_company_jobs(self, sample_lever_response):
        """Test Lever API call."""
        responses.add(
            responses.GET,
            'https://api.lever.co/v0/postings/lemonade?mode=json',
            json=sample_lever_response,
            status=200
        )
        
        session = create_session()
        jobs = lever_company_jobs('lemonade', session)
        
        assert len(jobs) == 1
        assert jobs[0]['text'] == 'Director of Platform Engineering'
    
    def test_normalize_gh(self):
        """Test Greenhouse job normalization."""
        gh_job = {
            'title': 'Head of DevOps',
            'absolute_url': 'https://boards.greenhouse.io/monday/jobs/123',
            'location': {'name': 'Tel Aviv, Israel'},
            'updated_at': '2024-01-15T10:00:00Z'
        }
        
        normalized = normalize_gh(gh_job)
        
        assert normalized['title'] == 'Head of DevOps'
        assert normalized['company'] == 'monday'
        assert normalized['location'] == 'Tel Aviv, Israel'
        assert normalized['url'] == 'https://boards.greenhouse.io/monday/jobs/123'
        assert normalized['source'] == 'greenhouse'
        assert normalized['posted_at'] == '2024-01-15T10:00:00Z'
    
    def test_normalize_lever(self):
        """Test Lever job normalization."""
        lever_job = {
            'text': 'Director of Platform',
            'hostedUrl': 'https://jobs.lever.co/lemonade/456',
            'categories': {
                'team': 'Engineering',
                'location': 'Tel Aviv, Israel'
            },
            'createdAt': '1705320000000',
            'descriptionPlain': 'Lead our platform team...'
        }
        
        normalized = normalize_lever(lever_job)
        
        assert normalized['title'] == 'Director of Platform'
        assert normalized['company'] == 'Engineering'
        assert normalized['location'] == 'Tel Aviv, Israel'
        assert normalized['url'] == 'https://jobs.lever.co/lemonade/456'
        assert normalized['source'] == 'lever'
        assert normalized['jd'] == 'Lead our platform team...'
    
    def test_title_matches(self):
        """Test title matching logic."""
        # Mock the config
        with patch('scripts.crawl.CFG', {'titles': ['Head of DevOps', 'Director of Platform']}):
            assert title_matches('Head of DevOps Engineering') == True
            assert title_matches('Senior DevOps Engineer') == False
            assert title_matches('Director of Platform Architecture') == True
            assert title_matches('Software Engineer') == False
    
    def test_location_matches(self):
        """Test location matching logic."""
        assert location_matches('Tel Aviv, Israel') == True
        assert location_matches('Herzliya, Israel') == True
        assert location_matches('Kfar Saba, Israel') == True
        assert location_matches('New York, USA') == False
        assert location_matches('London, UK') == False
        assert location_matches('') == False
        assert location_matches(None) == False
    
    @responses.activate
    @patch('scripts.crawl.CFG')
    @patch('scripts.crawl.OUT_RAW')
    @patch('scripts.crawl.OUT_JL')
    def test_main_integration(self, mock_out_jl, mock_out_raw, mock_cfg, 
                            sample_greenhouse_response, sample_lever_response):
        """Test main crawling function."""
        # Mock config
        mock_cfg.get.return_value = {
            'greenhouse': {'companies': ['monday']},
            'lever': {'companies': ['lemonade']}
        }
        
        # Mock file operations
        mock_out_raw.write_text = lambda x: None
        mock_out_jl.exists.return_value = False
        
        # Mock API responses
        responses.add(
            responses.GET,
            'https://boards-api.greenhouse.io/v1/boards/monday/jobs',
            json=sample_greenhouse_response,
            status=200
        )
        responses.add(
            responses.GET,
            'https://api.lever.co/v0/postings/lemonade?mode=json',
            json=sample_lever_response,
            status=200
        )
        
        # Mock open for writing to jsonl
        with patch('builtins.open', mock_open()):
            with patch('scripts.crawl.title_matches', return_value=True):
                with patch('scripts.crawl.location_matches', return_value=True):
                    main()
        
        # Verify API calls were made
        assert len(responses.calls) == 2
