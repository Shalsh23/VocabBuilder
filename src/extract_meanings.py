import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import logging
import html

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='../resources/wordsmith_extraction.log',
    filemode='w'
)

# Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def clean_html_text(text):
    """Clean HTML entities, normalize whitespace, and escape special characters"""
    # Decode HTML entities
    text = html.unescape(text)

    # Replace HTML line breaks with newlines
    text = text.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')

    # Replace multiple spaces/tabs with single space
    text = re.sub(r'\s+', ' ', text)

    # Replace special quotes with regular quotes first
    text = text.replace('&#8220;', '"').replace('&#8221;', '"')
    text = text.replace('&#8216;', "'").replace('&#8217;', "'")

    # Trim whitespace
    text = text.strip()

    return text

def escape_and_format_text(text):
    """Escape special characters and replace double quotes with single quotes"""
    # Replace double quotes with single quotes
    text = text.replace('"', "'")

    # Handle other special characters by escaping backslashes
    text = text.replace('\\', '\\\\')

    # Handle unicode quotes and replace with simple quotes
    text = text.replace('"', "'").replace('"', "'")
    text = text.replace(''', "'").replace(''', "'")

    return text

def extract_word_info(url):
    """Extract word, meaning, and usage examples from a word page"""
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract word from h3 tag
        word_h3 = soup.find('h3')
        word = word_h3.get_text(strip=True) if word_h3 else ""

        # Extract meaning
        meaning_text = ""
        meaning_div = soup.find('div', string='MEANING:')

        if meaning_div and meaning_div.find_next('div'):
            meaning_content = meaning_div.find_next('div')

            # Check if there's a table structure
            table = meaning_content.find('table')
            if table:
                # Extract from table structure
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        # First cell might have part of speech
                        first_cell = cells[0].get_text(strip=True)
                        second_cell = cells[1].get_text(strip=True)
                        meaning_text += f"{first_cell}\t{second_cell}\n"
            else:
                # Extract as plain text, preserving structure
                meaning_text = meaning_content.get_text().strip()
                # Normalize newlines
                meaning_text = re.sub(r'\n+', '\n', meaning_text)

        # Extract usage examples
        usage_text = ""
        usage_div = soup.find('div', string='USAGE:')

        if usage_div and usage_div.find_next('div'):
            usage_content = usage_div.find_next('div')

            # Get raw HTML content to preserve structure
            usage_html = str(usage_content)

            # Replace <br><br> with paragraph markers
            usage_html = re.sub(r'<br\s*/?><br\s*/?>|<br\s*/><br\s*/?>', '\n\n', usage_html)

            # Create a new soup to parse the modified HTML
            usage_soup = BeautifulSoup(usage_html, 'html.parser')

            # Extract text, preserving paragraph breaks
            usage_text = usage_soup.get_text()

            # Clean up the text
            usage_text = clean_html_text(usage_text)

            # Remove "See more usage examples..." and anything after
            usage_text = re.split(r'See more usage examples', usage_text)[0].strip()

        # Escape special characters and format quotes
        meaning_text = escape_and_format_text(meaning_text)
        usage_text = escape_and_format_text(usage_text)

        return word, meaning_text, usage_text

    except Exception as e:
        logging.error(f"Error extracting info from {url}: {e}")
        return "", "", ""

def process_words_csv(input_file="../resources/wordsmith_words.csv", output_file="../resources/wordsmith_complete.csv"):
    """Process the CSV file of words and URLs to extract word info"""
    words_processed = 0

    try:
        # Read the input CSV
        with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            # Skip header row if it exists
            header = next(reader, None)

            # Prepare output CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.writer(outfile, quoting=csv.QUOTE_ALL)
                writer.writerow(["Word", "Meaning", "Usage"])

                # Process each word
                for row in reader:
                    if len(row) >= 2:
                        url = row[1]

                        logging.info(f"Processing URL: {url}")
                        print(f"Processing: {url}")

                        # Extract word information
                        word, meaning, usage = extract_word_info(url)

                        # Output to CSV
                        writer.writerow([word, meaning, usage])

                        words_processed += 1

                        # Be nice to the server - add a small delay
                        time.sleep(1)

        print(f"Processed {words_processed} words.")
        logging.info(f"Processed {words_processed} words.")

    except Exception as e:
        logging.error(f"Error processing CSV: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Starting to extract word information...")
    process_words_csv()
    print("Done! Check wordsmith_complete.csv for results.")