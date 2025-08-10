# Test Fixtures Guide

This guide describes the reusable test fixtures available in `tests/conftest.py` for the WordADay project.

## Available Fixtures

### 1. `sample_archives_html`
**Purpose**: Provides static HTML content of the wordsmith archive page.

**Returns**: String containing sample HTML similar to https://wordsmith.org/awad/archives.html

**Usage Example**:
```python
def test_parse_archives(sample_archives_html):
    soup = BeautifulSoup(sample_archives_html, 'html.parser')
    links = soup.find_all('a', href=True)
    # Test parsing logic...
```

### 2. `sample_word_html`
**Purpose**: Provides static HTML for a single word definition page.

**Returns**: String containing sample HTML for a word page (serendipity)

**Usage Example**:
```python
def test_parse_word_page(sample_word_html):
    soup = BeautifulSoup(sample_word_html, 'html.parser')
    meaning = soup.find('div', class_='meaning')
    # Test word parsing logic...
```

### 3. `tmp_csv`
**Purpose**: Factory fixture for creating temporary CSV files for testing.

**Returns**: Function that creates temporary CSV files

**Usage Example**:
```python
def test_csv_operations(tmp_csv):
    # Create empty CSV
    empty_csv = tmp_csv("empty.csv")
    
    # Create CSV with string content
    csv_with_text = tmp_csv("data.csv", "header1,header2\nval1,val2")
    
    # Create CSV from list of lists
    csv_from_list = tmp_csv("list.csv", [
        ['Word', 'Meaning'],
        ['test', 'definition']
    ])
```

### 4. `app_client`
**Purpose**: Provides a Flask test client with testing mode enabled.

**Returns**: Flask test client instance

**Usage Example**:
```python
def test_flask_routes(app_client):
    response = app_client.get('/')
    assert response.status_code == 200
    
    response = app_client.get('/api/search?q=test')
    data = response.get_json()
    assert 'results' in data
```

### 5. `monkeypatch_requests_get`
**Purpose**: Helper to mock `requests.get` responses for testing HTTP requests.

**Returns**: Function to configure mocked responses

**Usage Example**:
```python
def test_http_requests(monkeypatch_requests_get):
    # Simple text response
    mock_get = monkeypatch_requests_get({
        'https://example.com/page': 'Response text'
    })
    
    # Detailed response configuration
    mock_get = monkeypatch_requests_get({
        'https://api.example.com/data': {
            'text': 'response body',
            'status_code': 200,
            'json': {'key': 'value'}
        },
        'https://error.example.com': {
            'status_code': 500,
            'raise_for_status': True
        }
    })
    
    # Use requests as normal
    response = requests.get('https://example.com/page')
    assert response.text == 'Response text'
```

## Additional Helper Fixtures

### `sample_csv_data`
Provides sample CSV data as a list of lists for testing CSV operations.

### `mock_wordsmith_data`
Provides a dictionary of mock word data with complete structure (url, meaning, usage, etymology).

### `reset_app_data` (autouse)
Automatically resets Flask app's global data between tests to prevent data pollution.

## Running Tests with Fixtures

### Run all tests:
```bash
pytest tests/
```

### Run specific test file:
```bash
pytest tests/test_conftest.py -v
```

### Run with coverage:
```bash
pytest tests/ --cov=src --cov=web
```

## Writing New Tests with Fixtures

1. Import the fixtures you need (they're automatically available from conftest.py)
2. Add fixture names as function parameters
3. Use the fixtures in your test logic

Example:
```python
def test_my_feature(tmp_csv, monkeypatch_requests_get, sample_archives_html):
    # Mock HTTP request
    mock_get = monkeypatch_requests_get({
        'https://wordsmith.org/awad/archives.html': sample_archives_html
    })
    
    # Create temporary CSV
    csv_path = tmp_csv("test.csv", [['Word'], ['test']])
    
    # Your test logic here...
```

## Dependencies

The fixtures use the following libraries (included in requirements-dev.txt):
- `pytest>=7.4`
- `pytest-mock>=3.12`
- `requests-mock>=1.11`
- `flask-testing>=0.8`

## Best Practices

1. **Use tmp_csv for file operations**: Always use the `tmp_csv` fixture for creating test CSV files. They're automatically cleaned up after tests.

2. **Mock external requests**: Use `monkeypatch_requests_get` to mock all external HTTP requests to avoid dependencies on external services.

3. **Leverage sample data**: Use the provided sample HTML and data fixtures for consistent test data.

4. **Test isolation**: The `reset_app_data` fixture ensures Flask app data is reset between tests automatically.

5. **Combine fixtures**: Multiple fixtures can be used together for integration testing scenarios.
