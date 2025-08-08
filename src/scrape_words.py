import requests
from bs4 import BeautifulSoup
import csv
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# URL constants
ARCHIVES_URL = "https://wordsmith.org/awad/archives.html"
BASE_URL = "https://wordsmith.org"

# Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_word_urls(skip_existing=True):
    """Scrape the archives page and extract all word URLs
    
    Args:
        skip_existing: If True, check for existing words and report new ones
    """
    word_dict = {}
    existing_words = {}
    
    # Load existing words if skip_existing is enabled
    if skip_existing:
        existing_words = load_existing_words()

    try:
        # Fetch the main archives page
        response = requests.get(ARCHIVES_URL, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all links to individual word pages
        links = soup.find_all("a", href=True)
        logging.debug(f"Found {len(links)} total links in the archives page")

        new_words = 0
        for link in links:
            href = link["href"]
            # Check if this is a word page link
            if href.startswith("/words/") and href.endswith(".html"):
                word = href.split("/")[-1].replace(".html", "")
                full_url = f"{BASE_URL}{href}"
                
                # Check if this is a new word
                if word not in existing_words:
                    new_words += 1
                    logging.debug(f"Found new word: {word} -> {full_url}")
                
                word_dict[word] = full_url

        print(f"Scraped {len(word_dict)} total words from the archives page")
        if skip_existing and existing_words:
            print(f"- {new_words} new words found")
            print(f"- {len(existing_words)} words already in database")
        
        return word_dict

    except requests.exceptions.RequestException as e:
        print(f"Error fetching archives page: {e}")
        logging.error(f"Error fetching archives page: {e}")
        return {}

def load_existing_words(filename="../resources/wordsmith_words.csv"):
    """Load existing words from CSV file if it exists."""
    existing_words = {}
    
    try:
        with open(filename, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader, None)  # Skip header
            
            for row in reader:
                if len(row) >= 2:
                    word = row[0]
                    url = row[1]
                    existing_words[word] = url
        
        print(f"Loaded {len(existing_words)} existing words from {filename}")
        logging.info(f"Loaded {len(existing_words)} existing words from {filename}")
    except FileNotFoundError:
        print("No existing file found. Starting fresh.")
        logging.info("No existing file found. Starting fresh.")
    
    return existing_words

def save_to_csv(word_dict, filename="../resources/wordsmith_words.csv", append=False):
    """Save the word dictionary to a CSV file.
    
    Args:
        word_dict: Dictionary of words and URLs
        filename: Output CSV filename
        append: If True, merge with existing data; if False, overwrite
    """
    # Load existing words if appending
    if append:
        existing_words = load_existing_words(filename)
        # Merge dictionaries, new words overwrite existing ones
        existing_words.update(word_dict)
        word_dict = existing_words
    
    # Sort words alphabetically for better organization
    sorted_words = sorted(word_dict.items())
    
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Word", "URL"])  # Write header
        for word, url in sorted_words:
            writer.writerow([word, url])
    
    print(f"Saved {len(word_dict)} total words to {filename}")

def main():
    print("Starting scraping process...")
    print("Checking for new words on wordsmith.org...\n")
    
    # Get words with existing check enabled
    word_dict = get_word_urls(skip_existing=True)
    
    if word_dict:
        # Save with append mode to merge with existing data
        save_to_csv(word_dict, append=True)
    else:
        print("No words were scraped.")

if __name__ == "__main__":
    main()