"""
Test file to verify conftest fixtures are working correctly
"""

import pytest
import csv
from pathlib import Path


def test_sample_archives_html(sample_archives_html):
    """Test that sample_archives_html fixture provides valid HTML"""
    assert sample_archives_html is not None
    assert "A.Word.A.Day Archives" in sample_archives_html
    assert "/words/serendipity.html" in sample_archives_html
    assert "/words/ephemeral.html" in sample_archives_html
    assert len(sample_archives_html) > 100  # Should be substantial HTML


def test_sample_word_html(sample_word_html):
    """Test that sample_word_html fixture provides valid word page HTML"""
    assert sample_word_html is not None
    assert "serendipity" in sample_word_html
    assert "MEANING:" in sample_word_html
    assert "USAGE:" in sample_word_html
    assert "ETYMOLOGY:" in sample_word_html
    assert "noun:" in sample_word_html


def test_tmp_csv(tmp_csv):
    """Test that tmp_csv fixture creates temporary CSV files correctly"""
    # Test creating empty CSV
    empty_csv = tmp_csv("empty.csv")
    assert empty_csv.exists()
    assert empty_csv.suffix == ".csv"
    
    # Test creating CSV with string content
    string_csv = tmp_csv("string.csv", "header1,header2\nvalue1,value2")
    assert string_csv.exists()
    content = string_csv.read_text()
    assert "header1,header2" in content
    assert "value1,value2" in content
    
    # Test creating CSV with list content
    list_data = [
        ['Word', 'Meaning'],
        ['test', 'a procedure to establish quality'],
        ['example', 'a thing characteristic of its kind']
    ]
    list_csv = tmp_csv("list.csv", list_data)
    assert list_csv.exists()
    
    # Verify CSV content
    with open(list_csv, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert rows[0] == ['Word', 'Meaning']
        assert rows[1] == ['test', 'a procedure to establish quality']
        assert len(rows) == 3


def test_app_client(app_client):
    """Test that app_client fixture provides a working Flask test client"""
    # Test that the client is configured for testing
    assert app_client is not None
    
    # Test a simple GET request to home page
    response = app_client.get('/')
    assert response.status_code in [200, 404]  # May be 404 if templates not set up
    
    # Test that testing mode is enabled
    from web.app import app
    assert app.config['TESTING'] == True
    assert app.config['SECRET_KEY'] == 'test-secret-key'


def test_monkeypatch_requests_get(monkeypatch_requests_get, sample_archives_html):
    """Test that monkeypatch_requests_get fixture mocks requests.get correctly"""
    import requests
    
    # Set up mock responses
    mock_get = monkeypatch_requests_get({
        'https://wordsmith.org/awad/archives.html': sample_archives_html,
        'https://api.example.com/data': {'text': 'api response', 'status_code': 200},
        'https://error.example.com': {'text': '', 'status_code': 500, 'raise_for_status': True}
    })
    
    # Test simple text response
    response = requests.get('https://wordsmith.org/awad/archives.html')
    assert response.text == sample_archives_html
    assert response.status_code == 200
    
    # Test dict response configuration
    response = requests.get('https://api.example.com/data')
    assert response.text == 'api response'
    assert response.status_code == 200
    
    # Test error response
    response = requests.get('https://error.example.com')
    assert response.status_code == 500
    with pytest.raises(requests.exceptions.HTTPError):
        response.raise_for_status()
    
    # Test default 404 for unknown URLs
    response = requests.get('https://unknown.example.com')
    assert response.status_code == 404
    with pytest.raises(requests.exceptions.HTTPError):
        response.raise_for_status()


def test_sample_csv_data(sample_csv_data):
    """Test that sample_csv_data fixture provides correct data structure"""
    assert sample_csv_data is not None
    assert isinstance(sample_csv_data, list)
    assert len(sample_csv_data) == 4  # Header + 3 data rows
    
    # Check header
    assert sample_csv_data[0] == ['Word', 'URL', 'Meaning', 'Usage']
    
    # Check first data row
    assert sample_csv_data[1][0] == 'serendipity'
    assert 'wordsmith.org' in sample_csv_data[1][1]
    assert 'noun:' in sample_csv_data[1][2]


def test_mock_wordsmith_data(mock_wordsmith_data):
    """Test that mock_wordsmith_data fixture provides correct dictionary structure"""
    assert mock_wordsmith_data is not None
    assert isinstance(mock_wordsmith_data, dict)
    assert len(mock_wordsmith_data) == 3
    
    # Check keys
    assert 'serendipity' in mock_wordsmith_data
    assert 'ephemeral' in mock_wordsmith_data
    assert 'quixotic' in mock_wordsmith_data
    
    # Check structure of one entry
    serendipity = mock_wordsmith_data['serendipity']
    assert 'url' in serendipity
    assert 'meaning' in serendipity
    assert 'usage' in serendipity
    assert 'etymology' in serendipity
    assert 'wordsmith.org' in serendipity['url']


def test_fixtures_integration(tmp_csv, sample_csv_data, monkeypatch_requests_get, sample_archives_html):
    """Test that multiple fixtures can work together"""
    # Create a CSV with sample data
    csv_path = tmp_csv("integration.csv", sample_csv_data)
    assert csv_path.exists()
    
    # Mock requests to return sample HTML
    import requests
    mock_get = monkeypatch_requests_get({
        'https://wordsmith.org/awad/archives.html': sample_archives_html
    })
    
    # Verify mocked request works
    response = requests.get('https://wordsmith.org/awad/archives.html')
    assert response.text == sample_archives_html
    
    # Verify CSV was created with correct data
    with open(csv_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 3
        assert rows[0]['Word'] == 'serendipity'
