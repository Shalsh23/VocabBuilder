#!/usr/bin/env python3
"""
Utility script to check the status of word processing
"""

import csv
import os

def check_processing_status():
    """Check the status of word scraping and processing"""
    
    words_file = "../resources/wordsmith_words.csv"
    complete_file = "../resources/wordsmith_complete.csv"
    
    # Check scraped words
    scraped_words = set()
    if os.path.exists(words_file):
        with open(words_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            for row in reader:
                if len(row) >= 1:
                    scraped_words.add(row[0])
        print(f"✓ Scraped words: {len(scraped_words)}")
    else:
        print("✗ No scraped words file found")
        return
    
    # Check processed words
    processed_words = set()
    if os.path.exists(complete_file):
        with open(complete_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            for row in reader:
                if len(row) >= 1:
                    processed_words.add(row[0])
        print(f"✓ Processed words: {len(processed_words)}")
    else:
        print("✗ No processed words file found")
        processed_words = set()
    
    # Calculate remaining
    remaining = scraped_words - processed_words
    
    print(f"\n📊 Status Summary:")
    print(f"  Total scraped: {len(scraped_words)}")
    print(f"  Already processed: {len(processed_words)}")
    print(f"  Remaining to process: {len(remaining)}")
    
    if len(processed_words) > 0:
        percentage = (len(processed_words) / len(scraped_words)) * 100
        print(f"  Progress: {percentage:.1f}%")
    
    if len(remaining) > 0 and len(remaining) <= 10:
        print(f"\n📝 Words remaining to process:")
        for word in sorted(list(remaining))[:10]:
            print(f"  - {word}")

if __name__ == "__main__":
    print("🔍 Checking VocabBuilder Processing Status\n")
    print("=" * 40)
    check_processing_status()
    print("=" * 40)
