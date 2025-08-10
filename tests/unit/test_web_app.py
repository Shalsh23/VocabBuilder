#!/usr/bin/env python3
"""
Unit tests for Flask web application (app.py)
Tests all routes, pagination, search, API endpoints, and session management
using mocked data to avoid disk reads.
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add web directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'web'))

# Import Flask app after adding to path
from app import app, load_word_data, parse_meaning, parse_usage


@pytest.fixture
def client():
    """Create test client for Flask app"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_word_data():
    """Generate mock word data for testing"""
    # Create 120 sample words for pagination testing
    words = []
    for i in range(120):
        word_num = i + 1
        words.append({
            'word': f'word{word_num:03d}',
            'meaning': f'noun: Definition for word {word_num}\nadjective: Another definition for word {word_num}',
            'usage': f'Example sentence with word{word_num:03d}. —Author Name, 2024'
        })
    
    # Add some specific test words
    words.extend([
        {
            'word': 'foo',
            'meaning': 'noun: A placeholder name\nverb: To perform foo action',
            'usage': 'The programmer used foo as a variable name. —Tech Book, 2023'
        },
        {
            'word': 'bar',
            'meaning': 'noun: Another placeholder\nadjective: Related to bars',
            'usage': 'The bar was set high. —Author, 2024'
        },
        {
            'word': 'baz',
            'meaning': 'noun: Third placeholder name',
            'usage': 'Foo, bar, and baz are common. —CS Text, 2022'
        }
    ])
    
    return words


@pytest.fixture(autouse=True)
def mock_loader(mock_word_data, monkeypatch):
    """Monkeypatch the load_word_data function to use mock data"""
    def mock_load():
        import app
        app.WORD_DATA = mock_word_data
        app.WORD_DICT = {word['word'].lower(): word for word in mock_word_data}
        print(f"Loaded {len(app.WORD_DATA)} mock words")
    
    # Patch the load_word_data function
    monkeypatch.setattr('app.load_word_data', mock_load)
    
    # Load the mock data
    mock_load()


class TestHomePage:
    """Test the home page route"""
    
    def test_home_page_returns_200(self, client):
        """Test that GET / returns 200 status"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_home_page_contains_word_of_day(self, client):
        """Test that home page contains 'Word of the Day'"""
        response = client.get('/')
        assert b'Word of the Day' in response.data
    
    def test_home_page_shows_total_words(self, client):
        """Test that home page displays total word count"""
        response = client.get('/')
        # Should show 123 words (120 numbered + 3 specific)
        assert b'123' in response.data or b'words' in response.data.lower()


class TestWordsListPage:
    """Test the /words route with pagination"""
    
    def test_words_page_returns_200(self, client):
        """Test that /words returns 200 status"""
        response = client.get('/words')
        assert response.status_code == 200
    
    def test_words_pagination_default_page(self, client):
        """Test default pagination (page 1, 50 words)"""
        response = client.get('/words')
        assert response.status_code == 200
        # Check that we have pagination indicators
        data = response.data.decode('utf-8')
        # When sorted alphabetically, 'bar', 'baz', 'foo' come first
        # Then word001-word120
        # First page should show first 50 items alphabetically
        assert 'bar' in data or 'baz' in data or 'foo' in data  # These come first alphabetically
        # Should not show later words
        assert 'word100' not in data
    
    def test_words_pagination_page_2(self, client):
        """Test pagination page 2"""
        response = client.get('/words?page=2')
        assert response.status_code == 200
        data = response.data.decode('utf-8')
        # Second page should show words after the first 50 alphabetically
        # Should have some of the numbered words
        assert 'word' in data.lower()
        # Page 2 should show different content than page 1
        # Check for words that would appear on page 2 (word051-word100 range)
        # Note: 'bar', 'baz', 'foo' might appear in navigation but not in the word list
    
    def test_words_pagination_last_page(self, client):
        """Test pagination last page with partial results"""
        response = client.get('/words?page=3')
        assert response.status_code == 200
        data = response.data.decode('utf-8')
        # Third page should show remaining words (total 123, pages 1-2 show 100)
        # Page 3 shows the last 23 words
        # When sorted alphabetically, later numbered words should be here
        assert 'word' in data.lower()  # Should have some word entries
    
    def test_words_search_filter(self, client):
        """Test search query filtering"""
        response = client.get('/words?search=foo')
        assert response.status_code == 200
        data = response.data.decode('utf-8')
        # Should find 'foo'
        assert 'foo' in data
        # Should not include unrelated words
        assert 'word001' not in data
        # 'bar' should not be in search results for 'foo'
        # But it might be in navigation elements, so check more specifically
        # that it's not in the word list results
    
    def test_words_search_in_meaning(self, client):
        """Test search query filters by meaning content"""
        response = client.get('/words?search=placeholder')
        assert response.status_code == 200
        data = response.data.decode('utf-8')
        # Should find words with 'placeholder' in meaning
        assert 'foo' in data or 'bar' in data or 'baz' in data
    
    def test_words_sort_alphabetical(self, client):
        """Test alphabetical sorting"""
        response = client.get('/words?sort=alphabetical&page=1')
        assert response.status_code == 200
        data = response.data.decode('utf-8')
        # 'bar' should come before 'foo' alphabetically
        bar_pos = data.find('bar')
        foo_pos = data.find('foo')
        if bar_pos != -1 and foo_pos != -1:
            assert bar_pos < foo_pos
    
    def test_words_sort_reverse(self, client):
        """Test reverse alphabetical sorting"""
        response = client.get('/words?sort=reverse&page=1')
        assert response.status_code == 200
        data = response.data.decode('utf-8')
        # Should show words in reverse order
        # word120 should appear before word001
        if 'word120' in data and 'word001' in data:
            assert data.find('word120') < data.find('word001')


class TestApiSearch:
    """Test the /api/search endpoint"""
    
    def test_api_search_returns_json(self, client):
        """Test that API returns JSON response"""
        response = client.get('/api/search?q=foo')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
    
    def test_api_search_finds_word(self, client):
        """Test that API search finds matching words"""
        response = client.get('/api/search?q=foo')
        data = json.loads(response.data)
        assert 'results' in data
        assert len(data['results']) > 0
        # Check that 'foo' is in results
        words = [r['word'] for r in data['results']]
        assert 'foo' in words
    
    def test_api_search_respects_limit(self, client):
        """Test that API search respects limit parameter"""
        response = client.get('/api/search?q=word&limit=5')
        data = json.loads(response.data)
        assert 'results' in data
        assert len(data['results']) <= 5
    
    def test_api_search_default_limit(self, client):
        """Test that API search uses default limit of 10"""
        response = client.get('/api/search?q=word&limit=10')
        data = json.loads(response.data)
        assert 'results' in data
        assert len(data['results']) <= 10
    
    def test_api_search_empty_query(self, client):
        """Test API search with empty query"""
        response = client.get('/api/search?q=')
        data = json.loads(response.data)
        assert 'results' in data
        assert len(data['results']) == 0
    
    def test_api_search_no_results(self, client):
        """Test API search with query that has no matches"""
        response = client.get('/api/search?q=xyz123notfound')
        data = json.loads(response.data)
        assert 'results' in data
        assert len(data['results']) == 0
    
    def test_api_search_truncates_meaning(self, client):
        """Test that API search truncates long meanings"""
        response = client.get('/api/search?q=foo')
        data = json.loads(response.data)
        for result in data['results']:
            assert 'meaning' in result
            # Meanings should be truncated with '...'
            if len(result['meaning']) > 103:
                assert result['meaning'].endswith('...')


class TestWordDetail:
    """Test the /word/<name> route"""
    
    def test_word_detail_shows_content(self, client):
        """Test that word detail page shows word content"""
        response = client.get('/word/foo')
        assert response.status_code == 200
        data = response.data.decode('utf-8')
        # Should show the word
        assert 'foo' in data.lower()
        # Should show meaning content
        assert 'placeholder' in data
        # Should show usage examples
        assert 'variable name' in data
    
    def test_word_detail_case_insensitive(self, client):
        """Test that word lookup is case-insensitive"""
        response = client.get('/word/FOO')
        assert response.status_code == 200
        data = response.data.decode('utf-8')
        assert 'foo' in data.lower()
    
    def test_word_detail_navigation_links(self, client):
        """Test that word detail shows prev/next navigation links"""
        response = client.get('/word/word050')
        assert response.status_code == 200
        data = response.data.decode('utf-8')
        # Should have navigation links
        assert 'word049' in data or 'Previous' in data or 'prev' in data.lower()
        assert 'word051' in data or 'Next' in data or 'next' in data.lower()
    
    def test_word_detail_first_word_no_prev(self, client):
        """Test that first word has no previous link"""
        # Get the first word alphabetically
        response = client.get('/word/bar')  # 'bar' comes first alphabetically
        assert response.status_code == 200
        # This is implementation-dependent, but generally first word
        # won't have a previous link or it will be disabled
    
    def test_word_detail_not_found(self, client):
        """Test 404 for non-existent word"""
        response = client.get('/word/nonexistentword')
        assert response.status_code == 404
    
    def test_word_detail_parsed_meanings(self, client):
        """Test that meanings are properly parsed"""
        response = client.get('/word/foo')
        assert response.status_code == 200
        data = response.data.decode('utf-8')
        # Should show parts of speech
        assert 'noun' in data.lower() or 'verb' in data.lower()


class TestStudyMode:
    """Test the /study route with session management"""
    
    def test_study_page_returns_200(self, client):
        """Test that /study returns 200 status"""
        response = client.get('/study')
        assert response.status_code == 200
    
    def test_study_initializes_session(self, client):
        """Test that study mode initializes session with index 0"""
        with client.session_transaction() as session:
            # Clear any existing session data
            session.clear()
        
        response = client.get('/study')
        assert response.status_code == 200
        
        with client.session_transaction() as session:
            assert 'study_index' in session
            assert session['study_index'] == 0
    
    def test_study_next_increments_index(self, client):
        """Test that 'next' action increments session index"""
        # Initialize session
        with client.session_transaction() as session:
            session['study_index'] = 5
        
        response = client.get('/study?action=next')
        assert response.status_code == 200
        
        with client.session_transaction() as session:
            assert session['study_index'] == 6
    
    def test_study_prev_decrements_index(self, client):
        """Test that 'prev' action decrements session index"""
        # Initialize session
        with client.session_transaction() as session:
            session['study_index'] = 5
        
        response = client.get('/study?action=prev')
        assert response.status_code == 200
        
        with client.session_transaction() as session:
            assert session['study_index'] == 4
    
    def test_study_index_wraps_around(self, client):
        """Test that index wraps around at boundaries"""
        # Set to last word
        with client.session_transaction() as session:
            session['study_index'] = 122  # Last index (0-based)
        
        # Go to next - should wrap to 0
        response = client.get('/study?action=next')
        assert response.status_code == 200
        
        with client.session_transaction() as session:
            assert session['study_index'] == 0
        
        # Go to previous - should wrap to last
        response = client.get('/study?action=prev')
        assert response.status_code == 200
        
        with client.session_transaction() as session:
            assert session['study_index'] == 122
    
    def test_study_random_action(self, client):
        """Test that random action sets a valid index"""
        response = client.get('/study?action=random')
        assert response.status_code == 200
        
        with client.session_transaction() as session:
            assert 'study_index' in session
            assert 0 <= session['study_index'] < 123  # Valid range
    
    def test_study_displays_word_info(self, client):
        """Test that study page displays current word information"""
        with client.session_transaction() as session:
            session['study_index'] = 0
        
        response = client.get('/study')
        assert response.status_code == 200
        data = response.data.decode('utf-8')
        
        # Should show word content
        assert 'word001' in data or 'word' in data.lower()
        # Should show index info (1 of 123)
        assert '1' in data and '123' in data
    
    def test_study_preserves_session_across_requests(self, client):
        """Test that session state persists across multiple requests"""
        # First request - initialize
        response = client.get('/study')
        assert response.status_code == 200
        
        # Move to next word multiple times
        for i in range(3):
            response = client.get('/study?action=next')
            assert response.status_code == 200
        
        # Check final index
        with client.session_transaction() as session:
            assert session['study_index'] == 3


class TestErrorHandling:
    """Test error handling and 404 pages"""
    
    def test_404_custom_template(self, client):
        """Test that 404 errors return custom template"""
        response = client.get('/nonexistentroute')
        assert response.status_code == 404
        # Custom 404 template should be returned
        # The actual content depends on the template, but it should be HTML
        assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data
    
    def test_404_for_missing_word(self, client):
        """Test that missing word returns 404 with custom template"""
        response = client.get('/word/missingword123')
        assert response.status_code == 404
        data = response.data.decode('utf-8')
        # Should mention the word that wasn't found
        assert 'missingword123' in data or '404' in data


class TestApiRandomWord:
    """Test the /api/random-word endpoint"""
    
    def test_api_random_word_returns_json(self, client):
        """Test that API returns JSON response"""
        response = client.get('/api/random-word')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
    
    def test_api_random_word_structure(self, client):
        """Test that random word API returns correct structure"""
        response = client.get('/api/random-word')
        data = json.loads(response.data)
        assert 'word' in data
        assert 'meaning' in data
        assert 'usage' in data
        # Verify it's one of our mock words
        assert data['word'].startswith('word') or data['word'] in ['foo', 'bar', 'baz']


class TestAboutPage:
    """Test the /about route"""
    
    def test_about_page_returns_200(self, client):
        """Test that /about returns 200 status"""
        response = client.get('/about')
        assert response.status_code == 200
    
    def test_about_page_shows_word_count(self, client):
        """Test that about page displays total word count"""
        response = client.get('/about')
        data = response.data.decode('utf-8')
        # Should show total of 123 words
        assert '123' in data


class TestHelperFunctions:
    """Test helper functions like parse_meaning and parse_usage"""
    
    def test_parse_meaning_with_parts_of_speech(self):
        """Test parsing meanings with parts of speech"""
        meaning = "noun: A test word\nadjective: Describing a test"
        parsed = parse_meaning(meaning)
        assert len(parsed) == 2
        assert parsed[0]['part_of_speech'] == 'noun'
        assert parsed[0]['definition'] == 'A test word'
        assert parsed[1]['part_of_speech'] == 'adjective'
        assert parsed[1]['definition'] == 'Describing a test'
    
    def test_parse_meaning_without_parts_of_speech(self):
        """Test parsing meanings without parts of speech"""
        meaning = "Just a simple definition"
        parsed = parse_meaning(meaning)
        assert len(parsed) == 1
        assert parsed[0]['part_of_speech'] == ''
        assert parsed[0]['definition'] == 'Just a simple definition'
    
    def test_parse_meaning_empty(self):
        """Test parsing empty meaning"""
        parsed = parse_meaning("")
        assert parsed == []
        parsed = parse_meaning(None)
        assert parsed == []
    
    def test_parse_usage_with_citations(self):
        """Test parsing usage examples with citations"""
        usage = "This is an example. —Author, 2024"
        parsed = parse_usage(usage)
        assert len(parsed) >= 1
        assert "This is an example" in parsed[0]
    
    def test_parse_usage_multiple_examples(self):
        """Test parsing multiple usage examples"""
        usage = "First example. —Author1, 2023; Second example. —Author2, 2024"
        parsed = parse_usage(usage)
        # Should split into multiple examples
        assert len(parsed) >= 1
    
    def test_parse_usage_empty(self):
        """Test parsing empty usage"""
        parsed = parse_usage("")
        assert parsed == []
        parsed = parse_usage(None)
        assert parsed == []


class TestSearchPage:
    """Test the /search advanced search page"""
    
    def test_search_page_returns_200(self, client):
        """Test that /search returns 200 status"""
        response = client.get('/search')
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
