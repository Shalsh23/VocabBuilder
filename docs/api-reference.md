# VocabBuilder API Reference

## Current Modules

### `scrape_words.py`

Module for scraping word URLs from Wordsmith.org archives.

#### Functions

##### `get_word_urls(skip_existing=True)`

Scrapes the archives page and extracts all word URLs.

**Parameters:**
- `skip_existing` (bool): If True, check for existing words and report new ones. Default: True

**Returns:**
- `dict`: Dictionary mapping words to their URLs

**Example:**
```python
word_dict = get_word_urls(skip_existing=True)
# Output: {'ephemeral': 'https://wordsmith.org/words/ephemeral.html', ...}
```

##### `load_existing_words(filename="../resources/wordsmith_words.csv")`

Loads existing words from CSV file if it exists.

**Parameters:**
- `filename` (str): Path to the CSV file. Default: "../resources/wordsmith_words.csv"

**Returns:**
- `dict`: Dictionary of existing words and URLs

**Example:**
```python
existing = load_existing_words()
print(f"Found {len(existing)} existing words")
```

##### `save_to_csv(word_dict, filename="../resources/wordsmith_words.csv", append=False)`

Saves the word dictionary to a CSV file.

**Parameters:**
- `word_dict` (dict): Dictionary of words and URLs
- `filename` (str): Output CSV filename
- `append` (bool): If True, merge with existing data; if False, overwrite

**Returns:**
- None

**Example:**
```python
save_to_csv(word_dict, append=True)
```

### `extract_meanings.py`

Module for extracting detailed word information from individual word pages.

#### Functions

##### `extract_word_info(url)`

Extracts word, meaning, and usage examples from a word page.

**Parameters:**
- `url` (str): URL of the word page

**Returns:**
- `tuple`: (word, meaning_text, usage_text)

**Example:**
```python
word, meaning, usage = extract_word_info("https://wordsmith.org/words/ephemeral.html")
```

##### `load_processed_words(output_file)`

Loads already processed words from the output file.

**Parameters:**
- `output_file` (str): Path to the processed words CSV

**Returns:**
- `dict`: Dictionary with words as keys and full rows as values

**Example:**
```python
processed = load_processed_words("../resources/wordsmith_complete.csv")
```

##### `process_words_csv(input_file, output_file, resume=True)`

Processes the CSV file of words and URLs to extract word info.

**Parameters:**
- `input_file` (str): Path to input CSV with words and URLs
- `output_file` (str): Path to output CSV with complete word information
- `resume` (bool): If True, skip already processed words; if False, reprocess all

**Returns:**
- None

**Example:**
```python
process_words_csv(
    input_file="../resources/wordsmith_words.csv",
    output_file="../resources/wordsmith_complete.csv",
    resume=True
)
```

##### `clean_html_text(text)`

Cleans HTML entities, normalizes whitespace, and escapes special characters.

**Parameters:**
- `text` (str): Raw text with HTML entities

**Returns:**
- `str`: Cleaned text

**Example:**
```python
clean_text = clean_html_text("This &amp; that")
# Output: "This & that"
```

##### `escape_and_format_text(text)`

Escapes special characters and replaces double quotes with single quotes.

**Parameters:**
- `text` (str): Text to escape

**Returns:**
- `str`: Escaped text safe for CSV storage

### `check_status.py`

Utility module for checking processing status.

#### Functions

##### `check_processing_status()`

Checks the status of word scraping and processing.

**Parameters:**
- None

**Returns:**
- None (prints status to console)

**Example:**
```python
check_processing_status()
# Output: Status summary with progress percentage
```

## Data Structures

### Word Dictionary Format

```python
{
    "word": "url",
    "ephemeral": "https://wordsmith.org/words/ephemeral.html",
    "serendipity": "https://wordsmith.org/words/serendipity.html"
}
```

### Processed Word Format

```python
{
    "word": ["word", "meaning", "usage"],
    "ephemeral": [
        "ephemeral",
        "adjective: Lasting for a very short time",
        "The beauty of cherry blossoms is ephemeral..."
    ]
}
```

## Constants

### Configuration Constants

```python
# URL constants
ARCHIVES_URL = "https://wordsmith.org/awad/archives.html"
BASE_URL = "https://wordsmith.org"

# Headers for web requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# File paths
DEFAULT_WORDS_FILE = "../resources/wordsmith_words.csv"
DEFAULT_COMPLETE_FILE = "../resources/wordsmith_complete.csv"
DEFAULT_LOG_FILE = "../resources/wordsmith_extraction.log"

# Processing parameters
DELAY_BETWEEN_REQUESTS = 1  # seconds
MAX_RETRIES = 3
TIMEOUT = 30  # seconds
```

## Error Handling

### Exception Types

#### Network Errors

```python
try:
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    logging.error(f"Network error: {e}")
    return None
```

#### Parsing Errors

```python
try:
    soup = BeautifulSoup(response.text, "html.parser")
    word = soup.find('h3').get_text()
except AttributeError as e:
    logging.error(f"Parsing error: {e}")
    return default_value
```

#### File I/O Errors

```python
try:
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(data)
except IOError as e:
    logging.error(f"File I/O error: {e}")
    raise
```

## Logging

### Log Configuration

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='../resources/wordsmith_extraction.log',
    filemode='w'  # 'a' for append
)
```

### Log Levels

- `DEBUG`: Detailed information for debugging
- `INFO`: General information about progress
- `WARNING`: Warning messages for non-critical issues
- `ERROR`: Error messages for failures

## Planned API (Future)

### RESTful API Endpoints

#### Words Resource

##### `GET /api/words`

Get a list of all words.

**Query Parameters:**
- `limit` (int): Number of words to return
- `offset` (int): Pagination offset
- `source` (str): Filter by source
- `difficulty` (str): Filter by difficulty level

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "word": "ephemeral",
      "difficulty": "advanced",
      "source": "wordsmith"
    }
  ],
  "pagination": {
    "total": 6565,
    "limit": 20,
    "offset": 0
  }
}
```

##### `GET /api/words/{word_id}`

Get detailed information about a specific word.

**Response:**
```json
{
  "id": 1,
  "word": "ephemeral",
  "pronunciation": "/ɪˈfɛmərəl/",
  "definitions": [
    {
      "part_of_speech": "adjective",
      "meaning": "Lasting for a very short time",
      "examples": [
        "The beauty of cherry blossoms is ephemeral"
      ]
    }
  ],
  "etymology": "From Greek ephēmeros",
  "difficulty": "advanced",
  "source": "wordsmith",
  "added_date": "2024-08-08"
}
```

##### `POST /api/words`

Add a new word to the database.

**Request Body:**
```json
{
  "word": "serendipity",
  "definitions": [...],
  "source": "manual"
}
```

##### `PUT /api/words/{word_id}`

Update word information.

##### `DELETE /api/words/{word_id}`

Remove a word from the database.

#### Search Endpoints

##### `GET /api/search`

Search for words.

**Query Parameters:**
- `q` (str): Search query
- `type` (str): Search type (exact, fuzzy, semantic)

**Response:**
```json
{
  "results": [
    {
      "word": "ephemeral",
      "score": 0.95,
      "snippet": "...lasting for a very short time..."
    }
  ]
}
```

#### Learning Endpoints

##### `GET /api/learn/random`

Get a random word for learning.

##### `POST /api/learn/progress`

Track learning progress for a word.

**Request Body:**
```json
{
  "word_id": 1,
  "performance": "easy",
  "time_spent": 30
}
```

##### `GET /api/learn/stats`

Get learning statistics.

**Response:**
```json
{
  "words_learned": 523,
  "total_time": 3600,
  "streak": 15,
  "level": "intermediate"
}
```

## WebSocket API (Planned)

### Real-time Updates

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

// Subscribe to word updates
ws.send(JSON.stringify({
  action: 'subscribe',
  channel: 'words'
}));

// Receive updates
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('New word added:', data.word);
};
```

## GraphQL API (Planned)

### Schema

```graphql
type Word {
  id: ID!
  term: String!
  pronunciation: String
  definitions: [Definition!]!
  etymology: String
  difficulty: Difficulty!
  source: Source!
  addedDate: DateTime!
}

type Definition {
  partOfSpeech: PartOfSpeech!
  meaning: String!
  examples: [String!]!
}

enum Difficulty {
  BEGINNER
  INTERMEDIATE
  ADVANCED
  EXPERT
}

enum PartOfSpeech {
  NOUN
  VERB
  ADJECTIVE
  ADVERB
  OTHER
}

type Query {
  word(id: ID!): Word
  words(limit: Int, offset: Int): [Word!]!
  search(query: String!): [Word!]!
  randomWord(difficulty: Difficulty): Word!
}

type Mutation {
  addWord(input: WordInput!): Word!
  updateWord(id: ID!, input: WordInput!): Word!
  deleteWord(id: ID!): Boolean!
  trackProgress(wordId: ID!, performance: Performance!): Progress!
}
```

## Rate Limiting

### Current Implementation

```python
import time

RATE_LIMIT = 1  # seconds between requests

def rate_limited_request(url):
    time.sleep(RATE_LIMIT)
    return requests.get(url)
```

### Planned API Rate Limiting

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour", "1000 per day"]
)

@app.route("/api/words")
@limiter.limit("10 per minute")
def get_words():
    # API logic here
    pass
```

## Testing

### Unit Test Example

```python
import unittest
from scrape_words import get_word_urls

class TestScraper(unittest.TestCase):
    def test_get_word_urls(self):
        urls = get_word_urls(skip_existing=False)
        self.assertIsInstance(urls, dict)
        self.assertGreater(len(urls), 0)
    
    def test_load_existing_words(self):
        # Test with non-existent file
        words = load_existing_words("non_existent.csv")
        self.assertEqual(len(words), 0)
```

### Integration Test Example

```python
def test_full_pipeline():
    # Scrape words
    words = get_word_urls()
    save_to_csv(words, "test_words.csv")
    
    # Extract meanings
    process_words_csv(
        input_file="test_words.csv",
        output_file="test_complete.csv",
        resume=False
    )
    
    # Verify output
    assert os.path.exists("test_complete.csv")
```

---

*Last updated: August 2024*
