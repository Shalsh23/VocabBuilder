# WordADay - Vocabulary Web Scraper

A Python web scraping project that collects and extracts vocabulary information from the "A Word A Day" (AWAD) website at wordsmith.org.

## Overview

This project scrapes interesting English vocabulary words along with their definitions and usage examples from the Wordsmith.org archives, creating a comprehensive database for vocabulary learning and language enrichment.

## Features

- Scrapes word archives from wordsmith.org
- Extracts detailed word information including:
  - Word definitions
  - Parts of speech
  - Real-world usage examples from literature and media
- Saves data in CSV format for easy access and analysis
- Implements polite scraping with delays to respect server resources

## Project Structure

```
WordADay/
├── scrape_words.py           # Scrapes word URLs from archives
├── extract_meanings.py        # Extracts detailed word information
├── wordsmith_words.csv       # List of words and their URLs
├── wordsmith_complete.csv    # Complete dataset with meanings and usage
└── wordsmith_extraction.log  # Processing logs
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

1. First, scrape the word URLs from the archives:
```bash
python scrape_words.py
```

2. Then extract detailed information for each word:
```bash
python extract_meanings.py
```

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
