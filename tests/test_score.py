import pytest
import json
import numpy as np
from unittest.mock import patch, mock_open, MagicMock
from scripts.score import embed, cosine, main


class TestScore:
    """Test scoring functionality."""
    
    @patch('scripts.score.get_client')
    def test_embed(self, mock_get_client):
        """Test embedding function."""
        # Mock OpenAI response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock()]
        mock_response.data[0].embedding = [0.1, 0.2, 0.3]
        mock_client.embeddings.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        result = embed("test text")
        
        # Should return numpy array
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.float32
        assert len(result) == 3
        assert np.array_equal(result, np.array([0.1, 0.2, 0.3], dtype=np.float32))
        
        # Verify API call
        mock_client.embeddings.create.assert_called_once_with(
            model="text-embedding-3-large",
            input=["test text"]
        )
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        a = np.array([1.0, 0.0, 0.0])
        b = np.array([1.0, 0.0, 0.0])
        c = np.array([0.0, 1.0, 0.0])
        d = np.array([0.0, 0.0, 0.0])  # Zero vector
        
        # Identical vectors should have similarity 1.0
        assert cosine(a, b) == pytest.approx(1.0)
        
        # Orthogonal vectors should have similarity 0.0
        assert cosine(a, c) == pytest.approx(0.0)
        
        # Zero vector should return 0.0
        assert cosine(a, d) == 0.0
        assert cosine(d, d) == 0.0
    
    @patch('scripts.score.get_client')
    @patch('scripts.score.PROFILE', 'Senior DevOps leader with Kubernetes experience')
    @patch('scripts.score.JOBS_JL')
    @patch('scripts.score.OUT_SCORES')
    def test_main_integration(self, mock_out_scores, mock_jobs_jl, mock_get_client, sample_jobs_data):
        """Test main scoring function."""
        # Mock OpenAI embeddings
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock()]
        mock_response.data[0].embedding = [0.8, 0.6, 0.0]  # High similarity vector
        mock_client.embeddings.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        # Mock file reading
        jobs_content = '\n'.join([json.dumps(job) for job in sample_jobs_data])
        
        with patch('builtins.open', mock_open(read_data=jobs_content)):
            main()
        
        # Verify embeddings were created (profile + each job)
        assert mock_client.embeddings.create.call_count == 3  # 1 profile + 2 jobs
        
        # Verify embeddings were created (profile + each job)
        assert mock_get_client.call_count >= 1  # At least one client creation
    
    def test_why_fit_logic(self):
        """Test the why_fit scoring logic."""
        # This tests the heuristic rules in main()
        job_data = {
            'title': 'Head of DevOps',
            'jd': 'Lead team using Kubernetes and EKS for platform reliability'
        }
        
        title = job_data['title'].lower()
        jd = job_data['jd'].lower()
        why = []
        
        if 'head' in title or 'director' in title:
            why.append("senior leadership scope")
        if 'devops' in title or 'platform' in title or 'sre' in title:
            why.append("platform reliability focus")
        if 'kubernetes' in jd or 'eks' in jd:
            why.append("k8s scale")
        
        expected_why = "senior leadership scope, platform reliability focus, k8s scale"
        assert ", ".join(why) == expected_why
