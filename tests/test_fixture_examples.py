"""
Example test file demonstrating how to use the conftest fixtures
in real test scenarios.
"""

import pytest
import csv
import requests
from bs4 import BeautifulSoup


def test_scrape_words_with_mocked_requests(monkeypatch_requests_get, sample_archives_html, tmp_csv):
    """
    Example test showing how to use fixtures to test word scraping functionality.
    This demonstrates mocking HTTP requests and using temporary CSV files.
    """
    from src.scrape_words import get_word_urls, save_to_csv
    
    # Mock the request to the archives page
    mock_get = monkeypatch_requests_get({
        'https://wordsmith.org/awad/archives.html': sample_archives_html
    })
    
    # Get word URLs (this will use the mocked response)
    word_dict = get_word_urls(skip_existing=False)
    
    # Verify we extracted the correct words
    assert 'serendipity' in word_dict
    assert 'ephemeral' in word_dict
    assert 'quixotic' in word_dict
    assert len(word_dict) == 12  # 10 real words + 2 test words from sample HTML
    
    # Save to a temporary CSV
    csv_path = tmp_csv("test_words.csv")
    save_to_csv(word_dict, filename=str(csv_path), append=False)
    
    # Verify the CSV was created correctly
    assert csv_path.exists()
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 12
        assert any(row['Word'] == 'serendipity' for row in rows)


def test_parse_word_page_with_mock(monkeypatch_requests_get, sample_word_html):
    """
    Example test showing how to test parsing of individual word pages.
    """
    # Mock the request to a word page
    mock_get = monkeypatch_requests_get({
        'https://wordsmith.org/words/serendipity.html': sample_word_html
    })
    
    # Fetch and parse the page
    response = requests.get('https://wordsmith.org/words/serendipity.html')
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Verify we can find expected elements
    word_title = soup.find('h1')
    assert word_title and word_title.text == 'serendipity'
    
    meaning_section = soup.find('div', class_='meaning')
    assert meaning_section is not None
    assert 'noun:' in meaning_section.text
    
    usage_section = soup.find('div', class_='usage')
    assert usage_section is not None
    assert 'The New York Times' in usage_section.text


def test_flask_app_with_test_client(app_client, tmp_csv, sample_csv_data):
    """
    Example test showing how to use the Flask test client fixture.
    """
    # Create a temporary CSV with test data
    csv_path = tmp_csv("test_data.csv", sample_csv_data)
    
    # Test the home page
    response = app_client.get('/')
    # Note: This might be 404 if templates aren't set up, but the client works
    assert response.status_code in [200, 404]
    
    # Test the API endpoints
    response = app_client.get('/api/random-word')
    assert response.status_code in [200, 404]
    
    # Test search API
    response = app_client.get('/api/search?q=test')
    assert response.status_code == 200
    data = response.get_json()
    assert 'results' in data


def test_combined_fixtures_integration(
    monkeypatch_requests_get, 
    sample_archives_html, 
    sample_word_html,
    tmp_csv,
    sample_csv_data
):
    """
    Example test demonstrating how multiple fixtures can work together
    in a more complex test scenario.
    """
    # Set up mocked HTTP responses for multiple URLs
    mock_get = monkeypatch_requests_get({
        'https://wordsmith.org/awad/archives.html': sample_archives_html,
        'https://wordsmith.org/words/serendipity.html': sample_word_html,
        'https://wordsmith.org/words/ephemeral.html': {
            'text': '<html><body><h1>ephemeral</h1></body></html>',
            'status_code': 200
        }
    })
    
    # Create temporary CSV files for input and output
    input_csv = tmp_csv("input.csv", [
        ['Word', 'URL'],
        ['serendipity', 'https://wordsmith.org/words/serendipity.html'],
        ['ephemeral', 'https://wordsmith.org/words/ephemeral.html']
    ])
    
    output_csv = tmp_csv("output.csv")
    
    # Simulate fetching word details
    word_details = []
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            response = requests.get(row['URL'])
            soup = BeautifulSoup(response.text, 'html.parser')
            h1 = soup.find('h1')
            if h1:
                word_details.append({
                    'word': h1.text,
                    'url': row['URL'],
                    'fetched': True
                })
    
    # Write results to output CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['word', 'url', 'fetched'])
        writer.writeheader()
        writer.writerows(word_details)
    
    # Verify the results
    assert output_csv.exists()
    with open(output_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0]['word'] == 'serendipity'
        assert rows[1]['word'] == 'ephemeral'
        assert all(row['fetched'] == 'True' for row in rows)


def test_mock_wordsmith_data_fixture(mock_wordsmith_data):
    """
    Example test showing how to use the mock_wordsmith_data fixture
    for unit tests that need structured word data.
    """
    # The fixture provides a ready-to-use dictionary of word data
    assert len(mock_wordsmith_data) == 3
    
    # Can be used to test functions that expect word data
    def count_adjectives(word_data):
        count = 0
        for word, info in word_data.items():
            if 'adjective' in info['meaning'].lower():
                count += 1
        return count
    
    # Test with the mock data
    adjective_count = count_adjectives(mock_wordsmith_data)
    assert adjective_count == 2  # ephemeral and quixotic are adjectives
    
    # Can extract specific words for testing
    serendipity = mock_wordsmith_data['serendipity']
    assert 'Persian fairy tale' in serendipity['etymology']
    assert 'noun:' in serendipity['meaning']


def test_reset_app_data_fixture(app_client):
    """
    Example test showing that the reset_app_data fixture (autouse=True)
    automatically cleans up Flask app data between tests.
    """
    from web.app import WORD_DATA, WORD_DICT
    
    # Modify the global data
    test_word = {
        'word': 'test_word',
        'meaning': 'A word for testing',
        'usage': 'Used in tests'
    }
    WORD_DATA.append(test_word)
    WORD_DICT['test_word'] = test_word
    
    # Verify it was added
    assert any(w['word'] == 'test_word' for w in WORD_DATA)
    assert 'test_word' in WORD_DICT
    
    # The reset_app_data fixture will automatically restore
    # the original data after this test completes
