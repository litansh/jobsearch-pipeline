import pytest
import responses
from scripts.utils import (
    getenv, slug, job_id, now_iso, 
    create_session, safe_get
)


class TestUtils:
    """Test utility functions."""
    
    def test_getenv(self):
        """Test getenv function."""
        # Test with existing env var
        import os
        os.environ['TEST_VAR'] = 'test_value'
        assert getenv('TEST_VAR') == 'test_value'
        
        # Test with default
        assert getenv('NONEXISTENT_VAR', 'default') == 'default'
        
        # Test with None
        assert getenv('NONEXISTENT_VAR') == ''
    
    def test_slug(self):
        """Test slug function."""
        assert slug('Hello World!') == 'hello-world'
        assert slug('Test-123_ABC') == 'test-123-abc'
        assert slug('  Multiple   Spaces  ') == 'multiple-spaces'
        assert slug('Special@#$%Characters') == 'special-characters'
    
    def test_job_id(self):
        """Test job_id function."""
        record1 = {
            'title': 'Head of DevOps',
            'company': 'monday',
            'location': 'Tel Aviv',
            'url': 'https://example.com/job1'
        }
        record2 = {
            'title': 'Head of DevOps',
            'company': 'monday', 
            'location': 'Tel Aviv',
            'url': 'https://example.com/job2'  # Different URL
        }
        
        id1 = job_id(record1)
        id2 = job_id(record2)
        
        # Should be 20 characters
        assert len(id1) == 20
        assert len(id2) == 20
        
        # Should be different for different records
        assert id1 != id2
        
        # Should be consistent for same record
        assert job_id(record1) == id1
    
    def test_now_iso(self):
        """Test now_iso function."""
        iso_time = now_iso()
        
        # Should be a string
        assert isinstance(iso_time, str)
        
        # Should contain date and time components
        assert 'T' in iso_time
        assert '-' in iso_time
        assert ':' in iso_time
    
    def test_create_session(self):
        """Test session creation."""
        session = create_session()
        
        # Should have timeout set
        assert session.timeout == 20
        
        # Should have retry adapters mounted
        assert 'http://' in session.adapters
        assert 'https://' in session.adapters
    
    @responses.activate
    def test_safe_get_success(self):
        """Test successful GET request."""
        responses.add(
            responses.GET,
            'https://api.example.com/data',
            json={'status': 'success'},
            status=200
        )
        
        response = safe_get('https://api.example.com/data')
        assert response.status_code == 200
        assert response.json() == {'status': 'success'}
    
    @responses.activate 
    def test_safe_get_retry(self):
        """Test GET request with retry on failure."""
        # First call fails, second succeeds
        responses.add(
            responses.GET,
            'https://api.example.com/data',
            status=500
        )
        responses.add(
            responses.GET,
            'https://api.example.com/data',
            json={'status': 'success'},
            status=200
        )
        
        response = safe_get('https://api.example.com/data')
        assert response.status_code == 200
        assert response.json() == {'status': 'success'}
    
    @responses.activate
    def test_safe_get_failure(self):
        """Test GET request that ultimately fails."""
        responses.add(
            responses.GET,
            'https://api.example.com/data',
            status=500
        )
        
        with pytest.raises(Exception):
            safe_get('https://api.example.com/data')
