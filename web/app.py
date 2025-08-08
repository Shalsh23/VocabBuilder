#!/usr/bin/env python3
"""
VocabBuilder Web Application
A Flask-based web interface for browsing and studying vocabulary words
"""

import csv
import os
import random
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask import session
from datetime import datetime
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Configuration
CSV_FILE = os.path.join(os.path.dirname(__file__), '..', 'resources', 'wordsmith_complete.csv')
WORDS_PER_PAGE = 50

# Global word data cache
WORD_DATA = []
WORD_DICT = {}

def load_word_data():
    """Load word data from CSV file into memory"""
    global WORD_DATA, WORD_DICT
    
    if not os.path.exists(CSV_FILE):
        print(f"Warning: CSV file not found at {CSV_FILE}")
        return
    
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            word_entry = {
                'word': row['Word'],
                'meaning': row['Meaning'],
                'usage': row['Usage']
            }
            WORD_DATA.append(word_entry)
            WORD_DICT[row['Word'].lower()] = word_entry
    
    print(f"Loaded {len(WORD_DATA)} words")

def parse_meaning(meaning_text):
    """Parse meaning text to extract parts of speech and definitions"""
    if not meaning_text:
        return []
    
    parts = []
    lines = meaning_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for part of speech pattern (e.g., "adjective: Definition")
        if ':' in line:
            pos, definition = line.split(':', 1)
            parts.append({
                'part_of_speech': pos.strip(),
                'definition': definition.strip()
            })
        else:
            # Handle cases where there's just a definition
            parts.append({
                'part_of_speech': '',
                'definition': line
            })
    
    return parts

def parse_usage(usage_text):
    """Parse usage text to extract examples and citations"""
    if not usage_text:
        return []
    
    examples = []
    
    # Split by sentence endings followed by attribution patterns
    # This is a simple approach - can be refined based on actual data patterns
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', usage_text)
    
    current_example = ''
    for sentence in sentences:
        current_example += sentence + ' '
        # Check if this looks like the end of a citation
        if ';' in sentence and any(year in sentence for year in ['19', '20']):
            examples.append(current_example.strip())
            current_example = ''
    
    # Add any remaining text
    if current_example.strip():
        examples.append(current_example.strip())
    
    # If no clear separation, just return the whole text as one example
    if not examples:
        examples = [usage_text]
    
    return examples

@app.route('/')
def index():
    """Home page with dashboard"""
    total_words = len(WORD_DATA)
    
    # Get a random word for "Word of the Day"
    word_of_day = None
    if WORD_DATA:
        word_of_day = random.choice(WORD_DATA)
    
    return render_template('index.html', 
                         total_words=total_words,
                         word_of_day=word_of_day)

@app.route('/words')
def word_list():
    """Display paginated list of all words"""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '').strip().lower()
    sort_by = request.args.get('sort', 'alphabetical')
    
    # Filter words based on search
    filtered_words = WORD_DATA
    if search_query:
        filtered_words = [
            w for w in WORD_DATA 
            if search_query in w['word'].lower() or 
               search_query in w['meaning'].lower()
        ]
    
    # Sort words
    if sort_by == 'alphabetical':
        filtered_words = sorted(filtered_words, key=lambda x: x['word'].lower())
    elif sort_by == 'reverse':
        filtered_words = sorted(filtered_words, key=lambda x: x['word'].lower(), reverse=True)
    # Add more sort options as needed
    
    # Pagination
    total_pages = (len(filtered_words) + WORDS_PER_PAGE - 1) // WORDS_PER_PAGE
    start_idx = (page - 1) * WORDS_PER_PAGE
    end_idx = start_idx + WORDS_PER_PAGE
    paginated_words = filtered_words[start_idx:end_idx]
    
    # Process words for display (truncate meanings)
    for word in paginated_words:
        # Get first definition only for list view
        meanings = parse_meaning(word['meaning'])
        if meanings:
            first_def = meanings[0]['definition']
            word['brief_meaning'] = first_def[:100] + '...' if len(first_def) > 100 else first_def
        else:
            word['brief_meaning'] = word['meaning'][:100] + '...' if len(word['meaning']) > 100 else word['meaning']
    
    return render_template('word_list.html',
                         words=paginated_words,
                         page=page,
                         total_pages=total_pages,
                         search_query=search_query,
                         sort_by=sort_by,
                         total_results=len(filtered_words))

@app.route('/word/<word_name>')
def word_detail(word_name):
    """Display detailed view of a single word"""
    word_entry = WORD_DICT.get(word_name.lower())
    
    if not word_entry:
        return render_template('404.html', word=word_name), 404
    
    # Parse the meaning and usage for better display
    word_data = {
        'word': word_entry['word'],
        'meanings': parse_meaning(word_entry['meaning']),
        'examples': parse_usage(word_entry['usage']),
        'raw_meaning': word_entry['meaning'],
        'raw_usage': word_entry['usage']
    }
    
    # Get previous and next words for navigation
    word_index = next((i for i, w in enumerate(WORD_DATA) if w['word'].lower() == word_name.lower()), -1)
    prev_word = WORD_DATA[word_index - 1]['word'] if word_index > 0 else None
    next_word = WORD_DATA[word_index + 1]['word'] if word_index < len(WORD_DATA) - 1 else None
    
    return render_template('word_detail.html',
                         word=word_data,
                         prev_word=prev_word,
                         next_word=next_word)

@app.route('/search')
def search():
    """Advanced search page"""
    return render_template('search.html')

@app.route('/api/search')
def api_search():
    """API endpoint for search functionality"""
    query = request.args.get('q', '').strip().lower()
    limit = request.args.get('limit', 10, type=int)
    
    if not query:
        return jsonify({'results': []})
    
    results = []
    for word_entry in WORD_DATA:
        if query in word_entry['word'].lower():
            results.append({
                'word': word_entry['word'],
                'meaning': word_entry['meaning'][:100] + '...'
            })
        elif query in word_entry['meaning'].lower():
            results.append({
                'word': word_entry['word'],
                'meaning': word_entry['meaning'][:100] + '...'
            })
        
        if len(results) >= limit:
            break
    
    return jsonify({'results': results})

@app.route('/study')
def study():
    """Study mode with flashcards"""
    # Get or set current word index in session
    if 'study_index' not in session:
        session['study_index'] = 0
    
    # Handle navigation
    action = request.args.get('action')
    if action == 'next':
        session['study_index'] = (session['study_index'] + 1) % len(WORD_DATA)
    elif action == 'prev':
        session['study_index'] = (session['study_index'] - 1) % len(WORD_DATA)
    elif action == 'random':
        session['study_index'] = random.randint(0, len(WORD_DATA) - 1)
    
    current_word = WORD_DATA[session['study_index']]
    
    # Parse word data for display
    word_data = {
        'word': current_word['word'],
        'meanings': parse_meaning(current_word['meaning']),
        'examples': parse_usage(current_word['usage']),
        'index': session['study_index'] + 1,
        'total': len(WORD_DATA)
    }
    
    return render_template('study.html', word=word_data)

@app.route('/api/random-word')
def api_random_word():
    """API endpoint to get a random word"""
    if not WORD_DATA:
        return jsonify({'error': 'No words available'}), 404
    
    word = random.choice(WORD_DATA)
    return jsonify({
        'word': word['word'],
        'meaning': word['meaning'],
        'usage': word['usage']
    })

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html', total_words=len(WORD_DATA))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    load_word_data()
    app.run(debug=False, host='127.0.0.1', port=8080)
