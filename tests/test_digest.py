import pytest
import json
import responses
from unittest.mock import patch, mock_open
from scripts.digest import send_telegram, main


class TestDigest:
    """Test digest functionality."""
    
    @responses.activate
    def test_send_telegram_success(self, mock_env_vars):
        """Test successful Telegram message sending."""
        responses.add(
            responses.POST,
            'https://api.telegram.org/bottest-telegram-token/sendMessage',
            json={'ok': True, 'result': {'message_id': 123}},
            status=200
        )
        
        # Patch the module-level variables directly
        with patch('scripts.digest.TELEGRAM_TOKEN', 'test-telegram-token'):
            with patch('scripts.digest.TELEGRAM_CHAT', 'test-chat-id'):
                send_telegram("Test message")
        
        # Verify API call was made
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        payload = json.loads(request.body)
        
        assert payload['chat_id'] == 'test-chat-id'
        assert payload['text'] == 'Test message'
        assert payload['parse_mode'] == 'HTML'
        assert payload['disable_web_page_preview'] == True
    
    @responses.activate 
    def test_send_telegram_failure(self, mock_env_vars, capsys):
        """Test Telegram message sending failure."""
        responses.add(
            responses.POST,
            'https://api.telegram.org/bottest-telegram-token/sendMessage',
            status=500
        )
        
        # Patch the module-level variables directly
        with patch('scripts.digest.TELEGRAM_TOKEN', 'test-telegram-token'):
            with patch('scripts.digest.TELEGRAM_CHAT', 'test-chat-id'):
                send_telegram("Test message")
        
        # Should print warning and message content
        captured = capsys.readouterr()
        assert "[WARN] Failed to send Telegram message" in captured.out
        assert "Test message" in captured.out
    
    def test_send_telegram_no_credentials(self, capsys):
        """Test Telegram sending without credentials."""
        with patch.dict('os.environ', {}, clear=True):
            send_telegram("Test message")
        
        captured = capsys.readouterr()
        assert "[WARN] Telegram env vars missing" in captured.out
        assert "Test message" in captured.out
    
    @patch('scripts.digest.SCORES')
    @patch('scripts.digest.send_telegram')
    def test_main_with_matches(self, mock_send_telegram, mock_scores, sample_scores_data):
        """Test main function with job matches."""
        # Mock scores file content
        scores_content = '\n'.join([json.dumps(score) for score in sample_scores_data])
        
        with patch('builtins.open', mock_open(read_data=scores_content)):
            with patch('scripts.digest.THRESHOLD', 0.7):  # Lower threshold to include both jobs
                main()
        
        # Verify Telegram was called
        mock_send_telegram.assert_called_once()
        
        # Check the message content
        call_args = mock_send_telegram.call_args[0][0]
        assert '<b>Top job matches for today</b>' in call_args
        assert 'Head of DevOps' in call_args
        assert 'Director of Platform' in call_args
        assert 'monday' in call_args
        assert 'lemonade' in call_args
    
    @patch('scripts.digest.SCORES')
    @patch('scripts.digest.send_telegram')
    def test_main_no_matches(self, mock_send_telegram, mock_scores, sample_scores_data):
        """Test main function with no matches above threshold."""
        # Mock scores file content
        scores_content = '\n'.join([json.dumps(score) for score in sample_scores_data])
        
        with patch('builtins.open', mock_open(read_data=scores_content)):
            with patch('scripts.digest.THRESHOLD', 0.9):  # High threshold to exclude all jobs
                main()
        
        # Verify Telegram was called with no matches message
        mock_send_telegram.assert_called_once_with(
            "No matches above threshold today. Try lowering SCORE_THRESHOLD."
        )
    
    @patch('scripts.digest.SCORES')
    @patch('scripts.digest.send_telegram')
    def test_main_with_max_items_limit(self, mock_send_telegram, mock_scores):
        """Test main function with MAX_ITEMS limit."""
        # Create more jobs than the limit
        many_scores = []
        for i in range(15):
            many_scores.append({
                "id": f"job{i}",
                "title": f"Job Title {i}",
                "company": f"Company {i}",
                "location": "Tel Aviv, Israel",
                "url": f"https://example.com/job{i}",
                "score": 0.8,
                "why_fit": "good match"
            })
        
        scores_content = '\n'.join([json.dumps(score) for score in many_scores])
        
        with patch('builtins.open', mock_open(read_data=scores_content)):
            with patch('scripts.digest.MAX_ITEMS', 5):  # Limit to 5 items
                main()
        
        # Verify message was sent
        mock_send_telegram.assert_called_once()
        
        # Count job entries in the message (each job should have a bullet point)
        call_args = mock_send_telegram.call_args[0][0]
        job_count = call_args.count('• <b>')
        assert job_count == 5  # Should be limited to MAX_ITEMS
