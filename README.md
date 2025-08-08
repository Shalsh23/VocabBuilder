# VocabBuilder - Multi-Source Vocabulary Application

A comprehensive vocabulary learning application that aggregates interesting words, definitions, and usage examples from multiple sources to build a rich language learning database.

## Overview

VocabBuilder is designed to be an extensible vocabulary aggregation platform. Currently, it supports scraping from the "A Word A Day" (AWAD) website at wordsmith.org, with plans to integrate multiple vocabulary sources including dictionary APIs, literature databases, and other educational resources.

## Current Features

### Wordsmith.org Integration
- Scrapes word archives from wordsmith.org/awad
- Extracts detailed word information including:
  - Word definitions
  - Parts of speech
  - Real-world usage examples from literature and media
- Saves data in CSV format for easy access and analysis
- Implements polite scraping with delays to respect server resources

## Planned Features

### Additional Data Sources
- **Dictionary APIs**: Integration with Merriam-Webster, Oxford, Cambridge APIs
- **Literature Sources**: Project Gutenberg word frequency analysis
- **Academic Sources**: SAT/GRE vocabulary lists
- **Etymology Sources**: Word origin and history tracking
- **Language Learning Platforms**: Duolingo, Memrise vocabulary sets

### Application Features
- **Unified Database**: Centralized SQLite/PostgreSQL database for all vocabulary
- **Web Interface**: Flask/Django web app for browsing and learning
- **API Service**: RESTful API for vocabulary queries
- **Spaced Repetition**: Learning algorithm for vocabulary retention
- **Daily Digest**: Email/notification service for word of the day
- **Mobile App**: React Native app for on-the-go learning
- **Export Options**: Anki deck generation, PDF flashcards

## Project Structure

### Current Structure
```
VocabBuilder/
├── src/                     # Source code
│   ├── scrape_words.py      # Scrapes word URLs from archives
│   └── extract_meanings.py  # Extracts detailed word information
├── resources/               # Data and output files
│   ├── wordsmith_words.csv
│   ├── wordsmith_complete.csv
│   └── wordsmith_extraction.log
├── requirements.txt
├── README.md
└── .gitignore
```

### Planned Structure
```
VocabBuilder/
├── scrapers/                # Data source integrations
│   ├── wordsmith/
│   ├── dictionary_apis/
│   ├── literature/
│   └── academic/
├── database/               # Database models and migrations
├── api/                    # REST API service
├── web/                    # Web interface
├── mobile/                 # Mobile application
├── utils/                  # Shared utilities
├── tests/                  # Test suite
└── data/                   # Data storage
```

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd WordADay
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install required packages:
```bash
pip install requests beautifulsoup4
```

## Usage

### Basic Usage

1. First, scrape the word URLs from the archives:
```bash
cd src
python scrape_words.py
```
The scraper will automatically:
- Check for existing words in the database
- Report how many new words were found
- Merge new words with existing data

2. Then extract detailed information for each word:
```bash
python extract_meanings.py
```
The extractor will automatically:
- Skip words that have already been processed
- Resume from where it left off if interrupted
- Save progress after each word to prevent data loss

3. Check processing status:
```bash
python check_status.py
```

### Resume After Interruption

Both scripts support resuming after interruption:
- **Scraper**: Automatically merges new words with existing data
- **Extractor**: Skips already processed words and appends new ones
- Use `Ctrl+C` to safely interrupt processing at any time

## Output

The project generates:
- `wordsmith_words.csv`: Contains all scraped words and their URLs
- `wordsmith_complete.csv`: Complete dataset with words, meanings, and usage examples
- `wordsmith_extraction.log`: Detailed logs of the extraction process

## Example Data

The dataset includes interesting vocabulary such as:
- **"central casting"** - stereotypical
- **"bunny boiler"** - a dangerously obsessive person
- **"elsewhen"** - at another time
- **"towardly"** - compliant or pleasant

## Requirements

- Python 3.x
- requests
- beautifulsoup4

## License

This project is for educational purposes. Please respect the original content source at wordsmith.org.

## Author

Shalki Shrivastava
