"""
Unit tests for scrape_words.py module.

Tests cover:
1. get_word_urls parsing archive HTML correctly (with mocked requests)
2. Existing-word logic with pre-populated CSV
3. save_to_csv functionality including append mode
4. Network error handling
"""

import pytest
import csv
import os
from unittest.mock import patch, Mock, mock_open, MagicMock
import tempfile
from pathlib import Path
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import scrape_words
from scrape_words import get_word_urls, save_to_csv, load_existing_words


class TestGetWordUrls:
    """Test suite for get_word_urls function."""
    
    @patch('scrape_words.requests.get')
    def test_get_word_urls_parses_html_correctly(self, mock_get):
        """Test that get_word_urls correctly parses archive HTML."""
        # Mock HTML response with sample word links
        mock_html = """
        <html>
        <body>
            <a href="/words/ephemeral.html">Ephemeral</a>
            <a href="/words/serendipity.html">Serendipity</a>
            <a href="/words/quixotic.html">Quixotic</a>
            <a href="/other/page.html">Other Link</a>
            <a href="https://external.com">External</a>
        </body>
        </html>
        """
        
        # Setup mock response
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Call function with skip_existing=False to avoid file operations
        with patch('scrape_words.load_existing_words', return_value={}):
            result = get_word_urls(skip_existing=False)
        
        # Verify results
        assert len(result) == 3
        assert "ephemeral" in result
        assert "serendipity" in result
        assert "quixotic" in result
        assert result["ephemeral"] == "https://wordsmith.org/words/ephemeral.html"
        assert result["serendipity"] == "https://wordsmith.org/words/serendipity.html"
        assert result["quixotic"] == "https://wordsmith.org/words/quixotic.html"
        
        # Verify correct URL was called
        mock_get.assert_called_once_with(
            "https://wordsmith.org/awad/archives.html",
            headers=scrape_words.HEADERS
        )
    
    @patch('scrape_words.requests.get')
    def test_get_word_urls_with_existing_words(self, mock_get):
        """Test that get_word_urls correctly handles existing words."""
        # Mock HTML response
        mock_html = """
        <html>
        <body>
            <a href="/words/ephemeral.html">Ephemeral</a>
            <a href="/words/serendipity.html">Serendipity</a>
            <a href="/words/newword.html">New Word</a>
        </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Mock existing words
        existing_words = {
            "ephemeral": "https://wordsmith.org/words/ephemeral.html",
            "serendipity": "https://wordsmith.org/words/serendipity.html"
        }
        
        with patch('scrape_words.load_existing_words', return_value=existing_words):
            with patch('builtins.print') as mock_print:
                result = get_word_urls(skip_existing=True)
        
        # All words should be returned regardless of existing status
        assert len(result) == 3
        assert "newword" in result
        
        # Check that appropriate messages were printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("3 total words" in str(call) for call in print_calls)
        assert any("1 new words found" in str(call) for call in print_calls)
        assert any("2 words already in database" in str(call) for call in print_calls)
    
    @patch('scrape_words.requests.get')
    def test_get_word_urls_network_error(self, mock_get):
        """Test that get_word_urls handles network errors gracefully."""
        import requests
        
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")
        
        with patch('scrape_words.load_existing_words', return_value={}):
            with patch('scrape_words.logging.error') as mock_log_error:
                result = get_word_urls(skip_existing=False)
        
        # Should return empty dict on error
        assert result == {}
        
        # Should log the error
        mock_log_error.assert_called_once()
        error_message = str(mock_log_error.call_args[0][0])
        assert "Error fetching archives page" in error_message
        assert "Network error" in error_message


class TestLoadExistingWords:
    """Test suite for load_existing_words function."""
    
    def test_load_existing_words_from_csv(self, tmp_path):
        """Test loading existing words from a CSV file."""
        # Create a temporary CSV file with sample data
        csv_file = tmp_path / "test_words.csv"
        csv_content = [
            ["Word", "URL"],
            ["ephemeral", "https://wordsmith.org/words/ephemeral.html"],
            ["serendipity", "https://wordsmith.org/words/serendipity.html"],
            ["quixotic", "https://wordsmith.org/words/quixotic.html"]
        ]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(csv_content)
        
        # Load the words
        result = load_existing_words(str(csv_file))
        
        # Verify loaded data
        assert len(result) == 3
        assert result["ephemeral"] == "https://wordsmith.org/words/ephemeral.html"
        assert result["serendipity"] == "https://wordsmith.org/words/serendipity.html"
        assert result["quixotic"] == "https://wordsmith.org/words/quixotic.html"
    
    def test_load_existing_words_file_not_found(self):
        """Test load_existing_words when file doesn't exist."""
        with patch('scrape_words.logging.info') as mock_log:
            result = load_existing_words("nonexistent_file.csv")
        
        # Should return empty dict
        assert result == {}
        
        # Should log appropriate message
        mock_log.assert_called_with("No existing file found. Starting fresh.")
    
    def test_load_existing_words_with_malformed_csv(self, tmp_path):
        """Test load_existing_words handles malformed CSV gracefully."""
        csv_file = tmp_path / "malformed.csv"
        csv_content = [
            ["Word", "URL"],
            ["complete", "https://wordsmith.org/words/complete.html"],
            ["incomplete"],  # Missing URL
            ["another", "https://wordsmith.org/words/another.html"]
        ]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(csv_content)
        
        result = load_existing_words(str(csv_file))
        
        # Should load valid rows only
        assert len(result) == 2
        assert "complete" in result
        assert "another" in result
        assert "incomplete" not in result


class TestSaveToCsv:
    """Test suite for save_to_csv function."""
    
    def test_save_to_csv_creates_new_file(self, tmp_path):
        """Test save_to_csv creates a new CSV file correctly."""
        csv_file = tmp_path / "output.csv"
        word_dict = {
            "zebra": "https://wordsmith.org/words/zebra.html",
            "apple": "https://wordsmith.org/words/apple.html",
            "banana": "https://wordsmith.org/words/banana.html"
        }
        
        save_to_csv(word_dict, str(csv_file), append=False)
        
        # Read and verify the created file
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        # Check header
        assert rows[0] == ["Word", "URL"]
        
        # Check data (should be sorted alphabetically)
        assert rows[1] == ["apple", "https://wordsmith.org/words/apple.html"]
        assert rows[2] == ["banana", "https://wordsmith.org/words/banana.html"]
        assert rows[3] == ["zebra", "https://wordsmith.org/words/zebra.html"]
        assert len(rows) == 4  # header + 3 words
    
    def test_save_to_csv_with_append_mode(self, tmp_path):
        """Test save_to_csv merges with existing data when append=True."""
        csv_file = tmp_path / "existing.csv"
        
        # Create initial CSV file
        initial_content = [
            ["Word", "URL"],
            ["existing1", "https://wordsmith.org/words/existing1.html"],
            ["existing2", "https://wordsmith.org/words/existing2.html"]
        ]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(initial_content)
        
        # New words to add (including one that overwrites existing)
        new_words = {
            "new1": "https://wordsmith.org/words/new1.html",
            "existing2": "https://wordsmith.org/words/existing2_updated.html",  # Overwrite
            "new2": "https://wordsmith.org/words/new2.html"
        }
        
        # Mock load_existing_words to return our initial data
        with patch('scrape_words.load_existing_words') as mock_load:
            mock_load.return_value = {
                "existing1": "https://wordsmith.org/words/existing1.html",
                "existing2": "https://wordsmith.org/words/existing2.html"
            }
            save_to_csv(new_words, str(csv_file), append=True)
        
        # Read and verify the merged file
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        # Should have header + 4 words (existing1, existing2 updated, new1, new2)
        assert len(rows) == 5
        
        # Create dict from rows for easier checking
        result_dict = {row[0]: row[1] for row in rows[1:]}  # Skip header
        
        assert result_dict["existing1"] == "https://wordsmith.org/words/existing1.html"
        assert result_dict["existing2"] == "https://wordsmith.org/words/existing2_updated.html"  # Updated
        assert result_dict["new1"] == "https://wordsmith.org/words/new1.html"
        assert result_dict["new2"] == "https://wordsmith.org/words/new2.html"
    
    def test_save_to_csv_overwrites_when_append_false(self, tmp_path):
        """Test save_to_csv overwrites existing file when append=False."""
        csv_file = tmp_path / "overwrite.csv"
        
        # Create initial file with some content
        initial_content = [
            ["Word", "URL"],
            ["old1", "https://wordsmith.org/words/old1.html"],
            ["old2", "https://wordsmith.org/words/old2.html"]
        ]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(initial_content)
        
        # New words that should completely replace the old ones
        new_words = {
            "new1": "https://wordsmith.org/words/new1.html",
            "new2": "https://wordsmith.org/words/new2.html"
        }
        
        save_to_csv(new_words, str(csv_file), append=False)
        
        # Read and verify file was overwritten
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        # Should only have new words
        assert len(rows) == 3  # header + 2 new words
        assert rows[1] == ["new1", "https://wordsmith.org/words/new1.html"]
        assert rows[2] == ["new2", "https://wordsmith.org/words/new2.html"]
        
        # Old words should not be present
        all_words = [row[0] for row in rows[1:]]
        assert "old1" not in all_words
        assert "old2" not in all_words
    
    def test_save_to_csv_sorts_alphabetically(self, tmp_path):
        """Test that save_to_csv sorts words alphabetically."""
        csv_file = tmp_path / "sorted.csv"
        word_dict = {
            "zebra": "url_z",
            "apple": "url_a",
            "mango": "url_m",
            "banana": "url_b"
        }
        
        save_to_csv(word_dict, str(csv_file), append=False)
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        # Extract just the words (skip header)
        words = [row[0] for row in rows[1:]]
        
        # Should be in alphabetical order
        assert words == ["apple", "banana", "mango", "zebra"]


class TestIntegration:
    """Integration tests for the scrape_words module."""
    
    @patch('scrape_words.requests.get')
    def test_full_scraping_workflow(self, mock_get, tmp_path):
        """Test the complete workflow of scraping and saving words."""
        # Mock HTML response
        mock_html = """
        <html>
        <body>
            <a href="/words/word1.html">Word1</a>
            <a href="/words/word2.html">Word2</a>
        </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        csv_file = tmp_path / "test_output.csv"
        
        # Get words and save them
        with patch('scrape_words.load_existing_words', return_value={}):
            word_dict = get_word_urls(skip_existing=False)
            save_to_csv(word_dict, str(csv_file), append=False)
        
        # Verify the file was created with correct content
        assert csv_file.exists()
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        assert len(rows) == 3  # header + 2 words
        assert rows[0] == ["Word", "URL"]
        assert rows[1][0] == "word1"
        assert rows[2][0] == "word2"
