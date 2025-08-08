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

def load_processed_words(output_file):
    """Load already processed words from the output file"""
    processed_words = {}
    
    try:
        with open(output_file, 'r', newline='', encoding='utf-8') as existing_file:
            existing_reader = csv.reader(existing_file)
            header = next(existing_reader, None)
            
            for row in existing_reader:
                if len(row) >= 3:
                    # Store word as key and full row as value
                    processed_words[row[0]] = row
            
            print(f"Found {len(processed_words)} already processed words.")
            logging.info(f"Found {len(processed_words)} already processed words.")
    except FileNotFoundError:
        print("No existing output file found. Starting fresh.")
        logging.info("No existing output file found. Starting fresh.")
    
    return processed_words

def process_words_csv(input_file="../resources/wordsmith_words.csv", output_file="../resources/wordsmith_complete.csv", resume=True):
    """Process the CSV file of words and URLs to extract word info
    
    Args:
        input_file: Path to input CSV with words and URLs
        output_file: Path to output CSV with complete word information
        resume: If True, skip already processed words; if False, reprocess all
    """
    words_processed = 0
    words_skipped = 0
    
    # Load existing processed words if resume is enabled
    processed_words = {}
    if resume:
        processed_words = load_processed_words(output_file)

    try:
        # Read the input CSV to get all words to process
        words_to_process = []
        with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            # Skip header row if it exists
            input_header = next(reader, None)
            
            for row in reader:
                if len(row) >= 2:
                    word = row[0]
                    url = row[1]
                    
                    # Check if word should be processed
                    if resume and word in processed_words:
                        words_skipped += 1
                        print(f"Skipping already processed word: {word}")
                        logging.info(f"Skipping already processed word: {word}")
                    else:
                        words_to_process.append((word, url))
        
        print(f"\nWords to process: {len(words_to_process)}")
        print(f"Words already processed: {words_skipped}")
        
        if len(words_to_process) == 0:
            print("All words have been processed!")
            return

        # Process words and append to output file
        mode = 'a' if resume and processed_words else 'w'
        with open(output_file, mode, newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile, quoting=csv.QUOTE_ALL)
            
            # Write header only if starting fresh
            if mode == 'w':
                writer.writerow(["Word", "Meaning", "Usage"])
            
            # Process each word
            for word_from_csv, url in words_to_process:
                try:
                    logging.info(f"Processing: {word_from_csv} - URL: {url}")
                    print(f"Processing: {word_from_csv} ({words_processed + 1}/{len(words_to_process)})")

                    # Extract word information
                    word, meaning, usage = extract_word_info(url)
                    
                    # If extraction failed, use the word from CSV
                    if not word:
                        word = word_from_csv

                    # Output to CSV
                    writer.writerow([word, meaning, usage])
                    outfile.flush()  # Flush after each write to prevent data loss

                    words_processed += 1

                    # Be nice to the server - add a small delay
                    time.sleep(1)
                    
                except KeyboardInterrupt:
                    print(f"\nProcessing interrupted by user. Processed {words_processed} words so far.")
                    logging.info(f"Processing interrupted by user. Processed {words_processed} words.")
                    break
                except Exception as e:
                    print(f"Error processing {word_from_csv}: {e}")
                    logging.error(f"Error processing {word_from_csv}: {e}")
                    continue

        print(f"\nSummary:")
        print(f"- Processed {words_processed} new words")
        print(f"- Skipped {words_skipped} already processed words")
        print(f"- Total words in database: {words_skipped + words_processed}")
        logging.info(f"Processed {words_processed} new words, skipped {words_skipped} existing words")

    except Exception as e:
        logging.error(f"Error processing CSV: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Starting to extract word information...")
    process_words_csv()
    print("Done! Check wordsmith_complete.csv for results.")