# VocabBuilder Data Formats

## Current Data Formats

### CSV Files

VocabBuilder currently uses CSV (Comma-Separated Values) format for data storage due to its simplicity, portability, and compatibility with spreadsheet applications.

#### 1. Word URLs File (`wordsmith_words.csv`)

Stores the mapping between words and their source URLs.

**Format:**
```csv
Word,URL
```

**Example:**
```csv
Word,URL
aardvark,https://wordsmith.org/words/aardvark.html
abacus,https://wordsmith.org/words/abacus.html
ephemeral,https://wordsmith.org/words/ephemeral.html
serendipity,https://wordsmith.org/words/serendipity.html
```

**Field Specifications:**
- **Word**: String, max 100 characters, unique identifier
- **URL**: String, valid URL format, max 500 characters

#### 2. Complete Word Data File (`wordsmith_complete.csv`)

Contains comprehensive word information including definitions and usage examples.

**Format:**
```csv
Word,Meaning,Usage
```

**Example:**
```csv
"Word","Meaning","Usage"
"central casting","adjective: Stereotypical.
noun: A company or department that provides actors for minor or background roles, often based on stereotypical appearances.","'Joey turned back, catching his own reflection in the mirror. He liked the way he was coming into his look. ... Closer to the central casting look of a man of authority. Someone not to be questioned.' Peter Blauner; Sunrise Highway; St. Martin's; 2018."
"ephemeral","adjective: Lasting for a very short time.","'The beauty of cherry blossoms is ephemeral, lasting only a few days before the petals fall.' Nature Magazine; 2023."
```

**Field Specifications:**
- **Word**: String, max 100 characters, primary key
- **Meaning**: Text, unlimited length, may contain:
  - Multiple parts of speech
  - Multiple definitions per part of speech
  - Tab-separated format for structure
- **Usage**: Text, unlimited length, contains:
  - Example sentences
  - Citations with author, source, year
  - Multiple examples separated by newlines

### Log Files

#### Extraction Log (`wordsmith_extraction.log`)

Records the processing history and any errors encountered.

**Format:**
```
TIMESTAMP - LEVEL - MESSAGE
```

**Example:**
```
2024-08-08 15:30:45,123 - INFO - Starting to extract word information...
2024-08-08 15:30:45,456 - INFO - Found 1548 already processed words.
2024-08-08 15:30:46,789 - INFO - Processing: ephemeral - URL: https://wordsmith.org/words/ephemeral.html
2024-08-08 15:30:47,012 - DEBUG - Extracted 2 definitions for word: ephemeral
2024-08-08 15:30:47,234 - INFO - Saved word 1549/6565
2024-08-08 15:30:48,567 - ERROR - Failed to extract info from https://wordsmith.org/words/broken.html: 404 Not Found
```

**Log Levels:**
- `DEBUG`: Detailed debugging information
- `INFO`: General progress information
- `WARNING`: Warning messages
- `ERROR`: Error messages with stack traces

## Planned Data Formats

### 1. JSON Format

For API responses and configuration files.

#### Word Object
```json
{
  "id": "ephemeral_001",
  "word": "ephemeral",
  "pronunciation": {
    "ipa": "/ɪˈfɛmərəl/",
    "audio_url": "https://api.example.com/audio/ephemeral.mp3"
  },
  "definitions": [
    {
      "part_of_speech": "adjective",
      "meaning": "Lasting for a very short time",
      "examples": [
        {
          "text": "The beauty of cherry blossoms is ephemeral",
          "source": "Nature Magazine",
          "year": 2023
        }
      ],
      "synonyms": ["transient", "fleeting", "momentary"],
      "antonyms": ["permanent", "lasting", "enduring"]
    }
  ],
  "etymology": {
    "origin": "Greek",
    "root": "ephēmeros",
    "meaning": "lasting only a day",
    "first_use": "1576"
  },
  "metadata": {
    "difficulty": "advanced",
    "frequency": 3.2,
    "domains": ["literature", "philosophy"],
    "source": "wordsmith",
    "date_added": "2024-08-08T15:30:45Z",
    "last_updated": "2024-08-08T15:30:45Z"
  }
}
```

### 2. Database Schema

#### SQLite/PostgreSQL Schema

```sql
-- Words table
CREATE TABLE words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word VARCHAR(100) UNIQUE NOT NULL,
    pronunciation_ipa VARCHAR(200),
    pronunciation_audio_url VARCHAR(500),
    etymology_origin VARCHAR(100),
    etymology_root VARCHAR(100),
    etymology_meaning TEXT,
    etymology_first_use VARCHAR(50),
    difficulty VARCHAR(20),
    frequency DECIMAL(3,1),
    source VARCHAR(50),
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Definitions table
CREATE TABLE definitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    part_of_speech VARCHAR(20),
    meaning TEXT NOT NULL,
    definition_order INTEGER DEFAULT 1,
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
);

-- Examples table
CREATE TABLE examples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    definition_id INTEGER NOT NULL,
    example_text TEXT NOT NULL,
    source VARCHAR(200),
    author VARCHAR(200),
    year INTEGER,
    FOREIGN KEY (definition_id) REFERENCES definitions(id) ON DELETE CASCADE
);

-- Synonyms table
CREATE TABLE synonyms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    synonym VARCHAR(100) NOT NULL,
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
);

-- Antonyms table
CREATE TABLE antonyms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    antonym VARCHAR(100) NOT NULL,
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
);

-- Domains table
CREATE TABLE domains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Word-Domain relationship
CREATE TABLE word_domains (
    word_id INTEGER NOT NULL,
    domain_id INTEGER NOT NULL,
    PRIMARY KEY (word_id, domain_id),
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE,
    FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE
);

-- User progress tracking
CREATE TABLE user_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    word_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'new',
    times_viewed INTEGER DEFAULT 0,
    times_correct INTEGER DEFAULT 0,
    times_incorrect INTEGER DEFAULT 0,
    last_reviewed TIMESTAMP,
    next_review TIMESTAMP,
    mastery_level INTEGER DEFAULT 0,
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_words_word ON words(word);
CREATE INDEX idx_words_difficulty ON words(difficulty);
CREATE INDEX idx_words_source ON words(source);
CREATE INDEX idx_definitions_word_id ON definitions(word_id);
CREATE INDEX idx_examples_definition_id ON examples(definition_id);
CREATE INDEX idx_user_progress_user_word ON user_progress(user_id, word_id);
```

### 3. XML Format

For data exchange and backup purposes.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<vocabulary>
    <word id="ephemeral_001">
        <term>ephemeral</term>
        <pronunciation>
            <ipa>/ɪˈfɛmərəl/</ipa>
            <audio>https://api.example.com/audio/ephemeral.mp3</audio>
        </pronunciation>
        <definitions>
            <definition>
                <partOfSpeech>adjective</partOfSpeech>
                <meaning>Lasting for a very short time</meaning>
                <examples>
                    <example>
                        <text>The beauty of cherry blossoms is ephemeral</text>
                        <source>Nature Magazine</source>
                        <year>2023</year>
                    </example>
                </examples>
                <synonyms>
                    <synonym>transient</synonym>
                    <synonym>fleeting</synonym>
                </synonyms>
            </definition>
        </definitions>
        <etymology>
            <origin>Greek</origin>
            <root>ephēmeros</root>
            <meaning>lasting only a day</meaning>
            <firstUse>1576</firstUse>
        </etymology>
        <metadata>
            <difficulty>advanced</difficulty>
            <frequency>3.2</frequency>
            <source>wordsmith</source>
            <dateAdded>2024-08-08T15:30:45Z</dateAdded>
        </metadata>
    </word>
</vocabulary>
```

### 4. YAML Configuration Format

For application configuration.

```yaml
# config.yaml
application:
  name: VocabBuilder
  version: 1.0.0
  environment: development

scraping:
  user_agent: "VocabBuilder/1.0"
  timeout: 30
  delay_between_requests: 1
  max_retries: 3
  
  sources:
    wordsmith:
      enabled: true
      base_url: "https://wordsmith.org"
      archives_url: "https://wordsmith.org/awad/archives.html"
    
    merriam_webster:
      enabled: false
      api_key: "${MERRIAM_API_KEY}"
      base_url: "https://api.merriam-webster.com/v1"

storage:
  type: csv  # csv, json, database
  csv:
    encoding: utf-8
    delimiter: ","
    quote_char: '"'
  
  database:
    type: sqlite  # sqlite, postgresql, mysql
    connection_string: "${DATABASE_URL}"
    pool_size: 5

logging:
  level: INFO
  format: "%(asctime)s - %(levelname)s - %(message)s"
  file: "logs/vocabbuilder.log"
  max_size: 10485760  # 10MB
  backup_count: 5

features:
  resume_capability: true
  duplicate_detection: true
  progress_tracking: true
  auto_backup: true
  
learning:
  spaced_repetition:
    enabled: true
    intervals: [1, 3, 7, 14, 30, 90]  # days
  
  difficulty_levels:
    - beginner
    - intermediate
    - advanced
    - expert
```

### 5. Binary Formats

#### Pickle Format (Python)

For fast serialization of Python objects.

```python
import pickle

# Save data
with open('words_cache.pkl', 'wb') as f:
    pickle.dump(word_dictionary, f)

# Load data
with open('words_cache.pkl', 'rb') as f:
    word_dictionary = pickle.load(f)
```

#### Protocol Buffers (Future)

For efficient, language-neutral serialization.

```protobuf
syntax = "proto3";

message Word {
    string id = 1;
    string term = 2;
    Pronunciation pronunciation = 3;
    repeated Definition definitions = 4;
    Etymology etymology = 5;
    Metadata metadata = 6;
}

message Definition {
    string part_of_speech = 1;
    string meaning = 2;
    repeated Example examples = 3;
    repeated string synonyms = 4;
    repeated string antonyms = 5;
}

message Example {
    string text = 1;
    string source = 2;
    string author = 3;
    int32 year = 4;
}
```

## Data Migration

### CSV to Database Migration

```python
import csv
import sqlite3

def migrate_csv_to_db(csv_file, db_file):
    """Migrate CSV data to SQLite database"""
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Insert word
            cursor.execute("""
                INSERT INTO words (word, source)
                VALUES (?, ?)
            """, (row['Word'], 'wordsmith'))
            
            word_id = cursor.lastrowid
            
            # Insert definition
            cursor.execute("""
                INSERT INTO definitions (word_id, meaning)
                VALUES (?, ?)
            """, (word_id, row['Meaning']))
            
            # Insert examples
            if row['Usage']:
                cursor.execute("""
                    INSERT INTO examples (definition_id, example_text)
                    VALUES (?, ?)
                """, (cursor.lastrowid, row['Usage']))
    
    conn.commit()
    conn.close()
```

## Data Validation

### Schema Validation

```python
from jsonschema import validate

word_schema = {
    "type": "object",
    "properties": {
        "word": {"type": "string", "maxLength": 100},
        "definitions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "part_of_speech": {"type": "string"},
                    "meaning": {"type": "string"}
                },
                "required": ["meaning"]
            }
        }
    },
    "required": ["word", "definitions"]
}

def validate_word_data(data):
    """Validate word data against schema"""
    try:
        validate(instance=data, schema=word_schema)
        return True
    except ValidationError as e:
        print(f"Validation error: {e}")
        return False
```

## Data Export Formats

### Anki Deck Format

```python
def export_to_anki(words, output_file):
    """Export words to Anki-compatible format"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for word in words:
            # Front: word
            # Back: definition + usage
            front = word['word']
            back = f"{word['meaning']}\n\n{word['usage']}"
            
            # Anki format: front[tab]back[tab]tags
            f.write(f"{front}\t{back}\tVocabBuilder\n")
```

### Markdown Format

```markdown
# Vocabulary List

## ephemeral
**Part of Speech:** adjective  
**Definition:** Lasting for a very short time  
**Example:** The beauty of cherry blossoms is ephemeral  
**Synonyms:** transient, fleeting, momentary  
**Etymology:** From Greek ephēmeros (lasting only a day)  

---
```

## Data Compression

### Gzip Compression

```python
import gzip
import json

def save_compressed(data, filename):
    """Save data with gzip compression"""
    
    with gzip.open(filename, 'wt', encoding='utf-8') as f:
        json.dump(data, f)

def load_compressed(filename):
    """Load gzip compressed data"""
    
    with gzip.open(filename, 'rt', encoding='utf-8') as f:
        return json.load(f)
```

---

*Last updated: August 2024*
