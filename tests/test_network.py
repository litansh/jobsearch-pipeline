import pytest
import csv
import io
from unittest.mock import patch, mock_open
from scripts.network import norm, main


class TestNetwork:
    """Test networking functionality."""
    
    def test_norm(self):
        """Test string normalization."""
        assert norm("  Hello World  ") == "hello world"
        assert norm("UPPERCASE") == "uppercase"
        assert norm(None) == ""
        assert norm("") == ""
    
    def test_main_no_args(self, capsys):
        """Test main function with no arguments."""
        with patch('sys.argv', ['network.py']):
            with pytest.raises(SystemExit):
                main()
        
        captured = capsys.readouterr()
        assert "Usage:" in captured.out
    
    def test_main_missing_csv(self, capsys):
        """Test main function with missing CSV file."""
        with patch('sys.argv', ['network.py', 'monday']):
            with patch('scripts.network.CSV') as mock_csv:
                mock_csv.exists.return_value = False
                with pytest.raises(SystemExit):
                    main()
        
        captured = capsys.readouterr()
        assert "Missing data/connections.csv" in captured.out
    
    def test_main_with_matches(self, capsys):
        """Test main function with matching connections."""
        # Mock CSV data
        csv_data = [
            {
                'First Name': 'John',
                'Last Name': 'Doe', 
                'Company': 'Monday.com',
                'Email Address': 'john@example.com',
                'Position': 'Engineer'
            },
            {
                'First Name': 'Jane',
                'Last Name': 'Smith',
                'Company': 'Monday.com',
                'Email Address': 'jane@example.com', 
                'Position': 'Manager'
            }
        ]
        
        # Convert to CSV string
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=csv_data[0].keys())
        writer.writeheader()
        writer.writerows(csv_data)
        csv_content = output.getvalue()
        
        with patch('sys.argv', ['network.py', 'monday']):
            with patch('scripts.network.CSV') as mock_csv:
                mock_csv.exists.return_value = True
                with patch('builtins.open', mock_open(read_data=csv_content)):
                    main()
        
        captured = capsys.readouterr()
        assert "Potential connectors for 'monday'" in captured.out
        assert "John Doe" in captured.out
        assert "Jane Smith" in captured.out
        assert "Monday.com" in captured.out
        assert "Suggested intro DM:" in captured.out
    
    def test_main_no_matches(self, capsys):
        """Test main function with no matching connections."""
        # Mock CSV data with no matches
        csv_data = [
            {
                'First Name': 'John',
                'Last Name': 'Doe',
                'Company': 'Other Corp',
                'Email Address': 'john@example.com',
                'Position': 'Engineer'
            }
        ]
        
        # Convert to CSV string
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=csv_data[0].keys())
        writer.writeheader()
        writer.writerows(csv_data)
        csv_content = output.getvalue()
        
        with patch('sys.argv', ['network.py', 'monday']):
            with patch('scripts.network.CSV') as mock_csv:
                mock_csv.exists.return_value = True
                with patch('builtins.open', mock_open(read_data=csv_content)):
                    main()
        
        captured = capsys.readouterr()
        assert "No likely connectors found." in captured.out
