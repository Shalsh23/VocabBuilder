"""
End-to-end integration test for the complete WordADay pipeline.
Tests the entire flow from scraping to serving without live HTTP calls.

This integration test module validates the complete data pipeline:
1. Scraping word URLs from a mocked archive page (3 test words)
2. Saving scraped words to CSV
3. Extracting meanings from mocked word pages
4. Loading data into Flask app and verifying endpoints

Key Features:
- No live HTTP requests - all external calls are mocked
- Uses temporary files for CSV data
- Tests individual pipeline steps and complete end-to-end flow
- Verifies Flask app serves correct data with 3 test words

Test Methods:
- test_step1_scrape_word_urls: Tests scraping word URLs from archive
- test_step2_save_words_to_csv: Tests saving scraped words to CSV
- test_step3_extract_meanings: Tests extracting meanings from word pages
- test_step4_flask_app: Tests Flask app with test data
- test_complete_pipeline: Tests the entire pipeline end-to-end
"""

import pytest
import tempfile
import os
import csv
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add src and web directories to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'web'))

import scrape_words
import extract_meanings
from app import app, load_word_data, WORD_DATA


class TestEndToEndPipeline:
    """Test the complete pipeline from scraping to serving."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and cleanup for each test."""
        # Store original data
        original_word_data = WORD_DATA.copy()
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.words_csv = os.path.join(self.temp_dir, 'words.csv')
        self.complete_csv = os.path.join(self.temp_dir, 'complete.csv')
        
        yield
        
        # Restore original data
        WORD_DATA.clear()
        WORD_DATA.extend(original_word_data)
        
        # Cleanup temp files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_mock_archive_page(self):
        """Create mock HTML for the archives page with 3 words."""
        return """
        <html>
        <body>
            <h2>Word Archives</h2>
            <a href="/words/ephemeral.html">ephemeral</a>
            <a href="/words/serendipity.html">serendipity</a>
            <a href="/words/mellifluous.html">mellifluous</a>
            <a href="/about.html">About</a>
            <a href="/contact.html">Contact</a>
        </body>
        </html>
        """
    
    def create_mock_word_page(self, word):
        """Create mock HTML for an individual word page."""
        word_data = {
            'ephemeral': {
                'meaning': 'adjective: Lasting for a very short time; transitory.',
                'usage': 'The beauty of cherry blossoms is ephemeral, lasting only a few weeks. Nature Magazine; 2023'
            },
            'serendipity': {
                'meaning': 'noun: The occurrence of events by chance in a happy or beneficial way.',
                'usage': 'It was pure serendipity that led me to discover this hidden bookstore. Literary Review; 2023'
            },
            'mellifluous': {
                'meaning': 'adjective: Sweet or musical; pleasant to hear.',
                'usage': 'Her mellifluous voice captivated the entire audience. Music Weekly; 2023'
            }
        }
        
        data = word_data.get(word, {'meaning': 'Unknown', 'usage': 'No usage available'})
        
        return f"""
        <html>
        <body>
            <h3>{word}</h3>
            <div>MEANING:</div>
            <div>{data['meaning']}</div>
            <div>USAGE:</div>
            <div>{data['usage']}</div>
        </body>
        </html>
        """
    
    @patch('scrape_words.requests.get')
    def test_step1_scrape_word_urls(self, mock_get):
        """Test Step 1: Scrape word URLs from the archive page."""
        # Mock the archive page response
        mock_response = MagicMock()
        mock_response.text = self.create_mock_archive_page()
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Run the scraping function
        word_dict = scrape_words.get_word_urls(skip_existing=False)
        
        # Verify we got 3 words
        assert len(word_dict) == 3
        assert 'ephemeral' in word_dict
        assert 'serendipity' in word_dict
        assert 'mellifluous' in word_dict
        
        # Verify URLs are correct
        assert word_dict['ephemeral'] == 'https://wordsmith.org/words/ephemeral.html'
        assert word_dict['serendipity'] == 'https://wordsmith.org/words/serendipity.html'
        assert word_dict['mellifluous'] == 'https://wordsmith.org/words/mellifluous.html'
        
        return word_dict
    
    @patch('scrape_words.requests.get')
    def test_step2_save_words_to_csv(self, mock_get):
        """Test Step 2: Save scraped words to CSV file."""
        # Mock the archive page response
        mock_response = MagicMock()
        mock_response.text = self.create_mock_archive_page()
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Get word URLs
        word_dict = scrape_words.get_word_urls(skip_existing=False)
        
        # Save to CSV
        scrape_words.save_to_csv(word_dict, filename=self.words_csv, append=False)
        
        # Verify CSV was created and contains correct data
        assert os.path.exists(self.words_csv)
        
        with open(self.words_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            # Check header
            assert rows[0] == ['Word', 'URL']
            
            # Check we have 3 words (plus header)
            assert len(rows) == 4
            
            # Check words are sorted alphabetically
            assert rows[1][0] == 'ephemeral'
            assert rows[2][0] == 'mellifluous'
            assert rows[3][0] == 'serendipity'
    
    @patch('extract_meanings.requests.get')
    def test_step3_extract_meanings(self, mock_get):
        """Test Step 3: Extract meanings from word pages."""
        # First, create the words CSV file
        with open(self.words_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Word', 'URL'])
            writer.writerow(['ephemeral', 'https://wordsmith.org/words/ephemeral.html'])
            writer.writerow(['serendipity', 'https://wordsmith.org/words/serendipity.html'])
            writer.writerow(['mellifluous', 'https://wordsmith.org/words/mellifluous.html'])
        
        # Mock responses for each word page
        def mock_get_side_effect(url, headers=None):
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            
            if 'ephemeral' in url:
                mock_response.text = self.create_mock_word_page('ephemeral')
            elif 'serendipity' in url:
                mock_response.text = self.create_mock_word_page('serendipity')
            elif 'mellifluous' in url:
                mock_response.text = self.create_mock_word_page('mellifluous')
            else:
                mock_response.text = '<html><body>Not found</body></html>'
            
            return mock_response
        
        mock_get.side_effect = mock_get_side_effect
        
        # Process words with mocked time.sleep
        with patch('extract_meanings.time.sleep'):
            extract_meanings.process_words_csv(
                input_file=self.words_csv,
                output_file=self.complete_csv,
                resume=False
            )
        
        # Verify complete CSV was created
        assert os.path.exists(self.complete_csv)
        
        # Read and verify the complete CSV
        with open(self.complete_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            words = list(reader)
            
            # Check we have 3 words
            assert len(words) == 3
            
            # Verify each word has meaning and usage
            for word in words:
                assert word['Word'] in ['ephemeral', 'serendipity', 'mellifluous']
                assert len(word['Meaning']) > 0
                assert len(word['Usage']) > 0
                
                # Check specific content
                if word['Word'] == 'ephemeral':
                    assert 'short time' in word['Meaning'].lower()
                elif word['Word'] == 'serendipity':
                    assert 'chance' in word['Meaning'].lower()
                elif word['Word'] == 'mellifluous':
                    assert 'sweet' in word['Meaning'].lower() or 'musical' in word['Meaning'].lower()
    
    def test_step4_flask_app(self):
        """Test Step 4: Start Flask app and verify endpoints."""
        # Create a complete CSV file with test data
        with open(self.complete_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Word', 'Meaning', 'Usage'])
            writer.writerow([
                'ephemeral',
                'adjective: Lasting for a very short time; transitory.',
                'The beauty of cherry blossoms is ephemeral, lasting only a few weeks. Nature Magazine; 2023'
            ])
            writer.writerow([
                'serendipity',
                'noun: The occurrence of events by chance in a happy or beneficial way.',
                'It was pure serendipity that led me to discover this hidden bookstore. Literary Review; 2023'
            ])
            writer.writerow([
                'mellifluous',
                'adjective: Sweet or musical; pleasant to hear.',
                'Her mellifluous voice captivated the entire audience. Music Weekly; 2023'
            ])
        
        # Set environment variable to point to our test CSV
        with patch.dict(os.environ, {'CSV_FILE': self.complete_csv}):
            # Patch the CSV_FILE constant in the app module
            with patch('app.CSV_FILE', self.complete_csv):
                # Clear and reload word data
                WORD_DATA.clear()
                load_word_data()
                
                # Create test client
                with app.test_client() as client:
                    # Test home page
                    response = client.get('/')
                    assert response.status_code == 200
                    
                    # Check that the total count is 3
                    data = response.get_data(as_text=True)
                    assert '3' in data or 'three' in data.lower()
                    
                    # Test words list page
                    response = client.get('/words')
                    assert response.status_code == 200
                    
                    # Check that all 3 words are present
                    data = response.get_data(as_text=True)
                    assert 'ephemeral' in data.lower()
                    assert 'serendipity' in data.lower()
                    assert 'mellifluous' in data.lower()
                    
                    # Verify count display
                    assert '3' in data
    
    @patch('scrape_words.requests.get')
    @patch('extract_meanings.requests.get')
    def test_complete_pipeline(self, mock_extract_get, mock_scrape_get):
        """Test the complete end-to-end pipeline."""
        # Step 1 & 2: Mock scraping and save to CSV
        mock_scrape_response = MagicMock()
        mock_scrape_response.text = self.create_mock_archive_page()
        mock_scrape_response.raise_for_status = MagicMock()
        mock_scrape_get.return_value = mock_scrape_response
        
        # Scrape and save words
        word_dict = scrape_words.get_word_urls(skip_existing=False)
        scrape_words.save_to_csv(word_dict, filename=self.words_csv, append=False)
        
        # Verify words CSV exists
        assert os.path.exists(self.words_csv)
        
        # Step 3: Mock extraction of meanings
        def mock_extract_side_effect(url, headers=None):
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            
            if 'ephemeral' in url:
                mock_response.text = self.create_mock_word_page('ephemeral')
            elif 'serendipity' in url:
                mock_response.text = self.create_mock_word_page('serendipity')
            elif 'mellifluous' in url:
                mock_response.text = self.create_mock_word_page('mellifluous')
            else:
                mock_response.text = '<html><body>Not found</body></html>'
            
            return mock_response
        
        mock_extract_get.side_effect = mock_extract_side_effect
        
        # Process words with mocked time.sleep
        with patch('extract_meanings.time.sleep'):
            extract_meanings.process_words_csv(
                input_file=self.words_csv,
                output_file=self.complete_csv,
                resume=False
            )
        
        # Verify complete CSV exists
        assert os.path.exists(self.complete_csv)
        
        # Step 4: Test Flask app with the generated data
        with patch.dict(os.environ, {'CSV_FILE': self.complete_csv}):
            with patch('app.CSV_FILE', self.complete_csv):
                # Clear and reload word data
                WORD_DATA.clear()
                load_word_data()
                
                # Verify we loaded 3 words
                assert len(WORD_DATA) == 3
                
                # Create test client
                with app.test_client() as client:
                    # Test home page
                    response = client.get('/')
                    assert response.status_code == 200
                    
                    # Test words list
                    response = client.get('/words')
                    assert response.status_code == 200
                    data = response.get_data(as_text=True)
                    
                    # Verify all 3 words are displayed
                    assert 'ephemeral' in data.lower()
                    assert 'serendipity' in data.lower()
                    assert 'mellifluous' in data.lower()
                    
                    # Test individual word pages
                    for word_name in ['ephemeral', 'serendipity', 'mellifluous']:
                        response = client.get(f'/word/{word_name}')
                        assert response.status_code == 200
                        data = response.get_data(as_text=True)
                        assert word_name in data.lower()
                    
                    # Test API endpoints
                    response = client.get('/api/search?q=ephemeral')
                    assert response.status_code == 200
                    json_data = response.get_json()
                    assert 'results' in json_data
                    assert len(json_data['results']) > 0
                    
                    # Test random word API
                    response = client.get('/api/random-word')
                    assert response.status_code == 200
                    json_data = response.get_json()
                    assert 'word' in json_data
                    assert json_data['word'] in ['ephemeral', 'serendipity', 'mellifluous']
        
        print("✅ Complete end-to-end pipeline test passed!")
