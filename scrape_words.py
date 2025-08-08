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

def get_word_urls():
    """Scrape the archives page and extract all word URLs"""
    word_dict = {}

    try:
        # Fetch the main archives page
        response = requests.get(ARCHIVES_URL, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all links to individual word pages
        links = soup.find_all("a", href=True)
        logging.debug(f"Found {len(links)} total links in the archives page")

        for link in links:
            href = link["href"]
            # Check if this is a word page link
            if href.startswith("/words/") and href.endswith(".html"):
                word = href.split("/")[-1].replace(".html", "")
                full_url = f"{BASE_URL}{href}"
                word_dict[word] = full_url
                logging.debug(f"Found word: {word} -> {full_url}")

        print(f"Scraped {len(word_dict)} words from the archives page")
        return word_dict

    except requests.exceptions.RequestException as e:
        print(f"Error fetching archives page: {e}")
        return {}

def save_to_csv(word_dict, filename="wordsmith_words.csv"):
    """Save the word dictionary to a CSV file."""
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Word", "URL"])  # Write header
        for word, url in word_dict.items():
            writer.writerow([word, url])
    print(f"Saved {len(word_dict)} words to {filename}")

def main():
    print("Starting scraping process...")
    word_dict = get_word_urls()
    if word_dict:
        save_to_csv(word_dict)
    else:
        print("No words were scraped.")

if __name__ == "__main__":
    main()