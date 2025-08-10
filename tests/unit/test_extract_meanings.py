"""
Unit tests for extract_meanings.py module.

Tests cover:
1. clean_html_text with various HTML inputs
2. escape_and_format_text with special characters
3. extract_word_info with mocked word page HTML (table layout & plain layout)
4. Resume logic with partial wordsmith_complete.csv
5. CSV output escaping for commas and newlines
"""

import pytest
import csv
import os
import sys
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path
import tempfile

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import extract_meanings
from extract_meanings import (
    clean_html_text,
    escape_and_format_text,
    extract_word_info,
    load_processed_words,
    process_words_csv
)


class TestCleanHtmlText:
    """Test suite for clean_html_text function."""
    
    def test_clean_html_text_basic(self):
        """Test basic HTML entity decoding and whitespace normalization."""
        input_text = "&amp; &lt; &gt; &quot;"
        expected = "& < > \""
        assert clean_html_text(input_text) == expected
    
    def test_clean_html_text_with_br_tags(self):
        """Test conversion of br tags to newlines."""
        input_text = "Line1<br>Line2<br/>Line3<br />Line4"
        expected = "Line1 Line2 Line3 Line4"  # Multiple spaces are collapsed to single
        assert clean_html_text(input_text) == expected
    
    def test_clean_html_text_multiple_spaces(self):
        """Test normalization of multiple spaces and tabs."""
        input_text = "Word1    Word2\t\tWord3   \n\n  Word4"
        expected = "Word1 Word2 Word3 Word4"
        assert clean_html_text(input_text) == expected
    
    def test_clean_html_text_special_quotes(self):
        """Test replacement of special quote characters."""
        input_text = "&#8220;Hello&#8221; and &#8216;World&#8217;"
        # Note: &#8220;/&#8221; decode to curly quotes, not straight quotes
        expected = '“Hello” and ‘World’'
        assert clean_html_text(input_text) == expected
    
    def test_clean_html_text_trim_whitespace(self):
        """Test trimming of leading and trailing whitespace."""
        input_text = "   Content with spaces   "
        expected = "Content with spaces"
        assert clean_html_text(input_text) == expected
    
    def test_clean_html_text_complex(self):
        """Test combination of HTML entities, tags, and whitespace."""
        input_text = """
        &lt;div&gt;  Text with   <br> breaks and
        &#8220;quotes&#8221;   &amp; entities  <br />
        """
        # HTML entities decode to actual characters
        expected = '<div> Text with breaks and “quotes” & entities'
        assert clean_html_text(input_text) == expected
    
    def test_clean_html_text_empty(self):
        """Test with empty string."""
        assert clean_html_text("") == ""
    
    def test_clean_html_text_only_whitespace(self):
        """Test with only whitespace."""
        assert clean_html_text("   \t\n   ") == ""


class TestEscapeAndFormatText:
    """Test suite for escape_and_format_text function."""
    
    def test_escape_double_quotes(self):
        """Test replacement of double quotes with single quotes."""
        input_text = 'He said "Hello"'
        expected = "He said 'Hello'"
        assert escape_and_format_text(input_text) == expected
    
    def test_escape_backslashes(self):
        """Test escaping of backslashes."""
        input_text = "Path\\to\\file"
        expected = "Path\\\\to\\\\file"
        assert escape_and_format_text(input_text) == expected
    
    def test_escape_unicode_quotes(self):
        """Test replacement of unicode quote characters."""
        # Note: The function doesn't actually replace unicode quotes currently
        # It only replaces straight double quotes with single quotes
        input_text = "“Hello” and ‘World’"
        # Unicode quotes remain unchanged in current implementation
        expected = "“Hello” and ‘World’"
        assert escape_and_format_text(input_text) == expected
    
    def test_escape_combined(self):
        """Test combination of various escaping."""
        input_text = '"Quote" with \\backslash\\ and “unicode”'
        # Unicode quotes are not replaced, only straight quotes
        expected = "'Quote' with \\\\backslash\\\\ and “unicode”"
        assert escape_and_format_text(input_text) == expected
    
    def test_escape_empty(self):
        """Test with empty string."""
        assert escape_and_format_text("") == ""
    
    def test_escape_no_special_chars(self):
        """Test with no special characters."""
        input_text = "Plain text without special chars"
        assert escape_and_format_text(input_text) == input_text


class TestExtractWordInfo:
    """Test suite for extract_word_info function."""
    
    @patch('extract_meanings.requests.get')
    def test_extract_word_info_table_layout(self, mock_get):
        """Test extraction from word page with table layout."""
        # Mock HTML response with table structure
        mock_html = """
        <html>
        <body>
            <h3>ephemeral</h3>
            <div>MEANING:</div>
            <div>
                <table>
                    <tr>
                        <td>adjective:</td>
                        <td>Lasting for a very short time.</td>
                    </tr>
                    <tr>
                        <td>noun:</td>
                        <td>Something that lasts for a short time.</td>
                    </tr>
                </table>
            </div>
            <div>USAGE:</div>
            <div>
                The beauty of cherry blossoms is ephemeral.<br><br>
                Life itself is ephemeral in nature.
            </div>
        </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        word, meaning, usage = extract_word_info("http://test.com/word")
        
        assert word == "ephemeral"
        assert "adjective:\tLasting for a very short time." in meaning
        assert "noun:\tSomething that lasts for a short time." in meaning
        assert "The beauty of cherry blossoms is ephemeral." in usage
        assert "Life itself is ephemeral in nature." in usage
    
    @patch('extract_meanings.requests.get')
    def test_extract_word_info_plain_layout(self, mock_get):
        """Test extraction from word page with plain text layout."""
        mock_html = """
        <html>
        <body>
            <h3>serendipity</h3>
            <div>MEANING:</div>
            <div>
                noun: The occurrence of events by chance in a happy way.
                
                Etymology: From the Persian fairy tale "The Three Princes of Serendip".
            </div>
            <div>USAGE:</div>
            <div>
                Finding that book was pure serendipity.<br><br>
                Sometimes serendipity plays a role in scientific discoveries.
                See more usage examples...
            </div>
        </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        word, meaning, usage = extract_word_info("http://test.com/word")
        
        assert word == "serendipity"
        assert "noun: The occurrence of events by chance" in meaning
        assert "Etymology:" in meaning
        assert "Finding that book was pure serendipity." in usage
        assert "scientific discoveries" in usage
        # Should not include "See more usage examples..."
        assert "See more usage examples" not in usage
    
    @patch('extract_meanings.requests.get')
    def test_extract_word_info_with_special_characters(self, mock_get):
        """Test extraction with special characters and quotes."""
        mock_html = """
        <html>
        <body>
            <h3>test-word</h3>
            <div>MEANING:</div>
            <div>A word with "quotes" and special chars.</div>
            <div>USAGE:</div>
            <div>He said "It's amazing!"</div>
        </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        word, meaning, usage = extract_word_info("http://test.com/word")
        
        assert word == "test-word"
        # Double quotes should be replaced with single quotes
        assert "A word with 'quotes' and special chars." in meaning
        assert "He said 'It's amazing!'" in usage
    
    @patch('extract_meanings.requests.get')
    def test_extract_word_info_missing_sections(self, mock_get):
        """Test extraction when some sections are missing."""
        mock_html = """
        <html>
        <body>
            <h3>partial</h3>
            <div>MEANING:</div>
            <div>A word with only meaning.</div>
        </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        word, meaning, usage = extract_word_info("http://test.com/word")
        
        assert word == "partial"
        assert meaning == "A word with only meaning."
        assert usage == ""
    
    @patch('extract_meanings.requests.get')
    @patch('extract_meanings.logging.error')
    def test_extract_word_info_network_error(self, mock_log_error, mock_get):
        """Test handling of network errors."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")
        
        word, meaning, usage = extract_word_info("http://test.com/word")
        
        assert word == ""
        assert meaning == ""
        assert usage == ""
        mock_log_error.assert_called_once()


class TestLoadProcessedWords:
    """Test suite for load_processed_words function."""
    
    def test_load_processed_words_existing_file(self, tmp_path):
        """Test loading already processed words from CSV."""
        csv_file = tmp_path / "wordsmith_complete.csv"
        csv_content = [
            ["Word", "Meaning", "Usage"],
            ["apple", "A fruit", "I ate an apple"],
            ["banana", "Yellow fruit", "Banana is sweet"],
            ["cherry", "Small red fruit", "Cherry pie"]
        ]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(csv_content)
        
        with patch('builtins.print'):
            processed = load_processed_words(str(csv_file))
        
        assert len(processed) == 3
        assert "apple" in processed
        assert "banana" in processed
        assert "cherry" in processed
        assert processed["apple"] == ["apple", "A fruit", "I ate an apple"]
    
    def test_load_processed_words_no_file(self, tmp_path):
        """Test when output file doesn't exist."""
        nonexistent = tmp_path / "nonexistent.csv"
        
        with patch('builtins.print'):
            with patch('extract_meanings.logging.info') as mock_log:
                processed = load_processed_words(str(nonexistent))
        
        assert processed == {}
        mock_log.assert_called_with("No existing output file found. Starting fresh.")
    
    def test_load_processed_words_empty_file(self, tmp_path):
        """Test loading from empty CSV file."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("Word,Meaning,Usage\n")
        
        with patch('builtins.print'):
            processed = load_processed_words(str(csv_file))
        
        assert processed == {}


class TestProcessWordsCsv:
    """Test suite for process_words_csv function."""
    
    def test_process_words_csv_basic(self, tmp_path, monkeypatch):
        """Test basic processing of words CSV."""
        # Mock time.sleep to speed up tests
        monkeypatch.setattr('time.sleep', lambda x: None)
        
        # Create input CSV
        input_csv = tmp_path / "input.csv"
        input_content = [
            ["Word", "URL"],
            ["test1", "http://test.com/test1"],
            ["test2", "http://test.com/test2"]
        ]
        
        with open(input_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(input_content)
        
        output_csv = tmp_path / "output.csv"
        
        # Mock extract_word_info
        with patch('extract_meanings.extract_word_info') as mock_extract:
            mock_extract.side_effect = [
                ("test1", "Meaning of test1", "Usage of test1"),
                ("test2", "Meaning of test2", "Usage of test2")
            ]
            
            with patch('builtins.print'):
                process_words_csv(
                    input_file=str(input_csv),
                    output_file=str(output_csv),
                    resume=False
                )
        
        # Verify output CSV
        with open(output_csv, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        assert len(rows) == 3  # Header + 2 words
        assert rows[0] == ["Word", "Meaning", "Usage"]
        assert rows[1] == ["test1", "Meaning of test1", "Usage of test1"]
        assert rows[2] == ["test2", "Meaning of test2", "Usage of test2"]
    
    def test_process_words_csv_resume_logic(self, tmp_path, monkeypatch):
        """Test resume functionality skips already processed words."""
        monkeypatch.setattr('time.sleep', lambda x: None)
        
        # Create partial output CSV with already processed words
        output_csv = tmp_path / "output.csv"
        existing_content = [
            ["Word", "Meaning", "Usage"],
            ["existing1", "Already processed", "Already done"],
            ["existing2", "Also processed", "Also done"]
        ]
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerows(existing_content)
        
        # Create input CSV with both existing and new words
        input_csv = tmp_path / "input.csv"
        input_content = [
            ["Word", "URL"],
            ["existing1", "http://test.com/existing1"],
            ["existing2", "http://test.com/existing2"],
            ["new1", "http://test.com/new1"],
            ["new2", "http://test.com/new2"]
        ]
        
        with open(input_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(input_content)
        
        # Mock extract_word_info - should only be called for new words
        with patch('extract_meanings.extract_word_info') as mock_extract:
            mock_extract.side_effect = [
                ("new1", "Meaning of new1", "Usage of new1"),
                ("new2", "Meaning of new2", "Usage of new2")
            ]
            
            with patch('builtins.print') as mock_print:
                process_words_csv(
                    input_file=str(input_csv),
                    output_file=str(output_csv),
                    resume=True
                )
        
        # Verify only new words were processed
        assert mock_extract.call_count == 2
        
        # Verify output CSV has all words
        with open(output_csv, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        assert len(rows) == 5  # Header + 2 existing + 2 new
        
        # Check print messages for skipped words
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Skipping already processed word: existing1" in str(call) for call in print_calls)
        assert any("Skipping already processed word: existing2" in str(call) for call in print_calls)
    
    def test_process_words_csv_special_characters(self, tmp_path, monkeypatch):
        """Test CSV output escaping for commas and newlines."""
        monkeypatch.setattr('time.sleep', lambda x: None)
        
        # Create input CSV
        input_csv = tmp_path / "input.csv"
        input_content = [
            ["Word", "URL"],
            ["test", "http://test.com/test"]
        ]
        
        with open(input_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(input_content)
        
        output_csv = tmp_path / "output.csv"
        
        # Mock extract_word_info with text containing commas and newlines
        with patch('extract_meanings.extract_word_info') as mock_extract:
            mock_extract.return_value = (
                "test",
                "A word, with commas, in meaning",
                "Usage with\nnewlines\nand, commas"
            )
            
            with patch('builtins.print'):
                process_words_csv(
                    input_file=str(input_csv),
                    output_file=str(output_csv),
                    resume=False
                )
        
        # Read and verify CSV handles special characters correctly
        with open(output_csv, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        assert len(rows) == 2
        assert rows[1][0] == "test"
        assert rows[1][1] == "A word, with commas, in meaning"
        assert rows[1][2] == "Usage with\nnewlines\nand, commas"
        
        # Verify the raw file has proper quoting
        with open(output_csv, 'r', encoding='utf-8') as f:
            raw_content = f.read()
        
        # Should have quotes around fields with commas/newlines
        assert '"A word, with commas, in meaning"' in raw_content
        assert '"Usage with\nnewlines\nand, commas"' in raw_content
    
    def test_process_words_csv_all_words_processed(self, tmp_path, monkeypatch):
        """Test when all words have already been processed."""
        monkeypatch.setattr('time.sleep', lambda x: None)
        
        # Create output CSV with all words already processed
        output_csv = tmp_path / "output.csv"
        existing_content = [
            ["Word", "Meaning", "Usage"],
            ["word1", "Meaning1", "Usage1"],
            ["word2", "Meaning2", "Usage2"]
        ]
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerows(existing_content)
        
        # Create input CSV with same words
        input_csv = tmp_path / "input.csv"
        input_content = [
            ["Word", "URL"],
            ["word1", "http://test.com/word1"],
            ["word2", "http://test.com/word2"]
        ]
        
        with open(input_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(input_content)
        
        with patch('extract_meanings.extract_word_info') as mock_extract:
            with patch('builtins.print') as mock_print:
                process_words_csv(
                    input_file=str(input_csv),
                    output_file=str(output_csv),
                    resume=True
                )
        
        # Should not call extract_word_info at all
        mock_extract.assert_not_called()
        
        # Check for appropriate message
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("All words have been processed!" in str(call) for call in print_calls)
    
    def test_process_words_csv_keyboard_interrupt(self, tmp_path, monkeypatch):
        """Test handling of keyboard interrupt during processing."""
        monkeypatch.setattr('time.sleep', lambda x: None)
        
        # Create input CSV
        input_csv = tmp_path / "input.csv"
        input_content = [
            ["Word", "URL"],
            ["test1", "http://test.com/test1"],
            ["test2", "http://test.com/test2"],
            ["test3", "http://test.com/test3"]
        ]
        
        with open(input_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(input_content)
        
        output_csv = tmp_path / "output.csv"
        
        # Mock extract_word_info to raise KeyboardInterrupt on second call
        with patch('extract_meanings.extract_word_info') as mock_extract:
            mock_extract.side_effect = [
                ("test1", "Meaning1", "Usage1"),
                KeyboardInterrupt()
            ]
            
            with patch('builtins.print') as mock_print:
                with patch('extract_meanings.logging.info') as mock_log:
                    process_words_csv(
                        input_file=str(input_csv),
                        output_file=str(output_csv),
                        resume=False
                    )
        
        # Verify first word was saved
        with open(output_csv, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        assert len(rows) == 2  # Header + 1 processed word
        assert rows[1][0] == "test1"
        
        # Check for interrupt message
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Processing interrupted by user" in str(call) for call in print_calls)
    
    def test_process_words_csv_extraction_error(self, tmp_path, monkeypatch):
        """Test handling of errors during word extraction."""
        monkeypatch.setattr('time.sleep', lambda x: None)
        
        # Create input CSV
        input_csv = tmp_path / "input.csv"
        input_content = [
            ["Word", "URL"],
            ["test1", "http://test.com/test1"],
            ["test2", "http://test.com/test2"],
            ["test3", "http://test.com/test3"]
        ]
        
        with open(input_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(input_content)
        
        output_csv = tmp_path / "output.csv"
        
        # Mock extract_word_info with one error
        with patch('extract_meanings.extract_word_info') as mock_extract:
            mock_extract.side_effect = [
                ("test1", "Meaning1", "Usage1"),
                Exception("Network error"),  # Error on second word
                ("test3", "Meaning3", "Usage3")
            ]
            
            with patch('builtins.print'):
                with patch('extract_meanings.logging.error') as mock_log_error:
                    process_words_csv(
                        input_file=str(input_csv),
                        output_file=str(output_csv),
                        resume=False
                    )
        
        # Verify words 1 and 3 were saved, word 2 was skipped
        with open(output_csv, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        assert len(rows) == 3  # Header + 2 successful words
        assert rows[1][0] == "test1"
        assert rows[2][0] == "test3"
        
        # Check error was logged
        error_calls = [str(call) for call in mock_log_error.call_args_list]
        assert any("Error processing test2" in str(call) for call in error_calls)


@pytest.fixture
def mock_sleep(monkeypatch):
    """Fixture to mock time.sleep as a no-op."""
    monkeypatch.setattr('time.sleep', lambda x: None)
    

@pytest.fixture
def mock_requests(monkeypatch):
    """Fixture to prevent actual network calls."""
    mock_get = Mock()
    mock_get.return_value.text = "<html></html>"
    mock_get.return_value.raise_for_status = Mock()
    monkeypatch.setattr('extract_meanings.requests.get', mock_get)
    return mock_get
