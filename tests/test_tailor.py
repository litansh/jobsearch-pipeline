import pytest
import json
from unittest.mock import patch, mock_open, MagicMock
from scripts.tailor import pick, gen_cover


class TestTailor:
    """Test tailoring functionality."""
    
    def test_pick_job_found(self, sample_scores_data):
        """Test picking a job by ID when it exists."""
        scores_content = '\n'.join([json.dumps(score) for score in sample_scores_data])
        
        with patch('builtins.open', mock_open(read_data=scores_content)):
            job = pick('job123')
        
        assert job['id'] == 'job123'
        assert job['title'] == 'Head of DevOps'
        assert job['company'] == 'monday'
    
    def test_pick_job_not_found(self, sample_scores_data):
        """Test picking a job by ID when it doesn't exist."""
        scores_content = '\n'.join([json.dumps(score) for score in sample_scores_data])
        
        with patch('builtins.open', mock_open(read_data=scores_content)):
            with pytest.raises(SystemExit, match="Job ID not found"):
                pick('nonexistent_job')
    
    @patch('scripts.tailor.get_client')
    @patch('scripts.tailor.PROFILE', 'Senior DevOps leader')
    def test_gen_cover(self, mock_get_client):
        """Test cover letter generation."""
        # Mock OpenAI response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Dear Hiring Manager,\n\nI am excited to apply for the Head of DevOps position..."
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        job = {
            'title': 'Head of DevOps',
            'company': 'monday',
            'url': 'https://example.com/job'
        }
        
        cover = gen_cover(job)
        
        assert "Dear Hiring Manager" in cover
        assert "Head of DevOps" in mock_client.chat.completions.create.call_args[1]['messages'][0]['content']
        assert "monday" in mock_client.chat.completions.create.call_args[1]['messages'][0]['content']
        
        # Verify model and parameters
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs['model'] == 'gpt-4o-mini'
        assert call_kwargs['temperature'] == 0.4
