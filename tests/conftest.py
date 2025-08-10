"""
Pytest configuration and fixtures for WordADay tests
"""

import pytest
import os
import sys
import tempfile
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web')))


@pytest.fixture
def sample_archives_html():
    """
    Fixture providing static HTML of wordsmith archive page.
    Returns sample HTML content similar to https://wordsmith.org/awad/archives.html
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>A.Word.A.Day Archives</title>
    </head>
    <body>
        <h1>A.Word.A.Day Archives</h1>
        <div class="archives">
            <p>Browse our collection of words:</p>
            <ul>
                <li><a href="/words/serendipity.html">serendipity</a> - The occurrence of events by chance in a happy way</li>
                <li><a href="/words/ephemeral.html">ephemeral</a> - Lasting for a very short time</li>
                <li><a href="/words/quixotic.html">quixotic</a> - Extremely idealistic and unrealistic</li>
                <li><a href="/words/mellifluous.html">mellifluous</a> - Sweet or musical; pleasant to hear</li>
                <li><a href="/words/ubiquitous.html">ubiquitous</a> - Present, appearing, or found everywhere</li>
                <li><a href="/words/perspicacious.html">perspicacious</a> - Having keen mental perception</li>
                <li><a href="/words/ineffable.html">ineffable</a> - Too great to be expressed in words</li>
                <li><a href="/words/sanguine.html">sanguine</a> - Optimistic or positive in difficult situations</li>
                <li><a href="/words/petrichor.html">petrichor</a> - The pleasant smell of earth after rain</li>
                <li><a href="/words/limerence.html">limerence</a> - The state of being infatuated with another person</li>
            </ul>
            <p>More archives:</p>
            <ul>
                <li><a href="/words/test-word.html">test-word</a></li>
                <li><a href="/words/another-word.html">another-word</a></li>
                <li><a href="https://example.com/external.html">External Link</a></li>
                <li><a href="/about.html">About Page</a></li>
            </ul>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def sample_word_html():
    """
    Fixture providing static HTML for one word page.
    Returns sample HTML content for a single word definition page.
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>serendipity - A.Word.A.Day</title>
    </head>
    <body>
        <div class="word-content">
            <h1>serendipity</h1>
            <div class="pronunciation">
                <strong>Pronunciation:</strong> /ˌserənˈdɪpɪti/
            </div>
            
            <div class="meaning">
                <h2>MEANING:</h2>
                <p><strong>noun:</strong> The occurrence and development of events by chance in a happy or beneficial way.</p>
                <p><strong>adjective (serendipitous):</strong> Occurring or discovered by chance in a happy or beneficial way.</p>
            </div>
            
            <div class="etymology">
                <h2>ETYMOLOGY:</h2>
                <p>Coined by Horace Walpole in 1754, from the Persian fairy tale "The Three Princes of Serendip", 
                whose heroes were always making discoveries of things they were not in quest of.</p>
            </div>
            
            <div class="usage">
                <h2>USAGE:</h2>
                <p>"A fortunate stroke of serendipity brought the two old friends together after decades." 
                - The New York Times; Jan 15, 2023</p>
                <p>"The discovery of penicillin was a classic case of scientific serendipity." 
                - Nature Magazine; Mar 10, 2022</p>
                <p>"Sometimes the best moments in life come from serendipity rather than careful planning." 
                - The Guardian; Dec 5, 2023</p>
            </div>
            
            <div class="notes">
                <h2>NOTES:</h2>
                <p>Serendipity is often cited as one of the most beautiful words in the English language. 
                It captures the magic of unexpected discoveries and happy accidents that enrich our lives.</p>
            </div>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def tmp_csv(tmp_path):
    """
    Fixture providing a temporary path factory to write/read CSVs.
    Returns a function that creates temporary CSV files.
    """
    def _create_csv(filename="test.csv", content=None):
        """
        Create a temporary CSV file with optional content.
        
        Args:
            filename: Name of the CSV file
            content: Optional content to write to the file (list of lists or string)
        
        Returns:
            Path object pointing to the created CSV file
        """
        csv_path = tmp_path / filename
        
        if content is not None:
            import csv
            
            if isinstance(content, str):
                # Write string content directly
                csv_path.write_text(content)
            elif isinstance(content, list):
                # Write list of lists as CSV rows
                with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    for row in content:
                        writer.writerow(row)
        else:
            # Create empty file
            csv_path.touch()
        
        return csv_path
    
    return _create_csv


@pytest.fixture
def app_client():
    """
    Fixture providing Flask test client with app.testing = True.
    Returns a Flask test client for the VocabBuilder web application.
    """
    from web.app import app
    
    # Set testing configuration
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Create test client
    with app.test_client() as client:
        # Establish application context
        with app.app_context():
            yield client


@pytest.fixture
def monkeypatch_requests_get(monkeypatch):
    """
    Helper fixture to mock requests.get responses.
    Returns a function that can be used to set up mocked responses.
    """
    import requests
    from unittest.mock import Mock, MagicMock
    
    def _mock_get(url_responses=None, default_response=None):
        """
        Set up mocked responses for requests.get.
        
        Args:
            url_responses: Dict mapping URLs to response data. Response data can be:
                - String: returned as response.text
                - Dict with keys: 'text', 'status_code', 'json', 'raise_for_status'
                - Mock object: returned directly
            default_response: Default response for URLs not in url_responses
        
        Returns:
            The mock object for further configuration if needed
        """
        mock_get = Mock()
        
        def get_side_effect(url, *args, **kwargs):
            # Create response mock
            response = Mock()
            response.raise_for_status = Mock()
            
            # Check if we have a specific response for this URL
            if url_responses and url in url_responses:
                response_data = url_responses[url]
                
                if isinstance(response_data, str):
                    # Simple text response
                    response.text = response_data
                    response.status_code = 200
                    response.json.return_value = None
                elif isinstance(response_data, dict):
                    # Detailed response configuration
                    response.text = response_data.get('text', '')
                    response.status_code = response_data.get('status_code', 200)
                    
                    if 'json' in response_data:
                        response.json.return_value = response_data['json']
                    
                    if 'raise_for_status' in response_data and response_data['raise_for_status']:
                        response.raise_for_status.side_effect = requests.exceptions.HTTPError()
                elif isinstance(response_data, Mock):
                    # Return the mock directly
                    return response_data
                else:
                    # Return as text by default
                    response.text = str(response_data)
                    response.status_code = 200
            elif default_response:
                # Use default response
                if isinstance(default_response, str):
                    response.text = default_response
                    response.status_code = 200
                elif isinstance(default_response, dict):
                    response.text = default_response.get('text', '')
                    response.status_code = default_response.get('status_code', 200)
                    if 'json' in default_response:
                        response.json.return_value = default_response['json']
                else:
                    return default_response
            else:
                # Default empty response
                response.text = ''
                response.status_code = 404
                response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
            
            return response
        
        mock_get.side_effect = get_side_effect
        monkeypatch.setattr(requests, 'get', mock_get)
        
        return mock_get
    
    return _mock_get


# Additional helper fixtures

@pytest.fixture
def sample_csv_data():
    """
    Fixture providing sample CSV data for testing.
    Returns a list of lists representing CSV rows.
    """
    return [
        ['Word', 'URL', 'Meaning', 'Usage'],
        ['serendipity', 'https://wordsmith.org/words/serendipity.html', 
         'noun: The occurrence of events by chance in a happy way', 
         'A fortunate stroke of serendipity brought them together.'],
        ['ephemeral', 'https://wordsmith.org/words/ephemeral.html',
         'adjective: Lasting for a very short time',
         'The beauty of cherry blossoms is ephemeral.'],
        ['quixotic', 'https://wordsmith.org/words/quixotic.html',
         'adjective: Extremely idealistic and unrealistic',
         'His quixotic quest for perfection was admirable but impractical.']
    ]


@pytest.fixture
def mock_wordsmith_data():
    """
    Fixture providing mock data structure for wordsmith words.
    Returns a dictionary of word data.
    """
    return {
        'serendipity': {
            'url': 'https://wordsmith.org/words/serendipity.html',
            'meaning': 'noun: The occurrence of events by chance in a happy way',
            'usage': 'A fortunate stroke of serendipity brought them together.',
            'etymology': 'From the Persian fairy tale "The Three Princes of Serendip"'
        },
        'ephemeral': {
            'url': 'https://wordsmith.org/words/ephemeral.html',
            'meaning': 'adjective: Lasting for a very short time',
            'usage': 'The beauty of cherry blossoms is ephemeral.',
            'etymology': 'From Greek ephemeros, lasting only a day'
        },
        'quixotic': {
            'url': 'https://wordsmith.org/words/quixotic.html',
            'meaning': 'adjective: Extremely idealistic and unrealistic',
            'usage': 'His quixotic quest for perfection was admirable but impractical.',
            'etymology': 'From Don Quixote, the idealistic hero of Cervantes novel'
        }
    }


@pytest.fixture(autouse=True)
def reset_app_data():
    """
    Fixture to reset the Flask app's global data before each test.
    This prevents data pollution between tests.
    """
    from web.app import WORD_DATA, WORD_DICT
    
    # Store original data
    original_word_data = WORD_DATA.copy()
    original_word_dict = WORD_DICT.copy()
    
    # Run the test
    yield
    
    # Restore original data
    WORD_DATA.clear()
    WORD_DATA.extend(original_word_data)
    WORD_DICT.clear()
    WORD_DICT.update(original_word_dict)
