# VocabBuilder Web Interface

A Flask-based web application for browsing and studying vocabulary words.

## Features

### ✅ All 5 Phases Implemented

1. **Home Dashboard** (`/`)
   - Welcome page with statistics
   - Word of the Day feature
   - Quick navigation to all sections

2. **Word List View** (`/words`)
   - Paginated display (50 words per page)
   - Search functionality
   - Sort options (A-Z, Z-A)
   - Brief definitions with "View Details" links

3. **Word Detail View** (`/word/<word_name>`)
   - Complete word information
   - All definitions with parts of speech
   - Full usage examples with citations
   - Previous/Next navigation
   - Copy to clipboard functionality

4. **Advanced Search** (`/search`)
   - Real-time search as you type
   - Search in both words and definitions
   - Dynamic results display
   - Direct links to word details

5. **Study Mode** (`/study`)
   - Flashcard interface
   - Show/hide definitions
   - Navigate between words (Previous/Next/Random)
   - Keyboard shortcuts (Space to flip, Arrow keys to navigate)
   - Progress tracking bar

## Running the Application

1. Install Flask (if not already installed):
```bash
pip install Flask
```

2. Navigate to the web directory:
```bash
cd web
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and visit:
```
http://localhost:5000
```

## Project Structure

```
web/
├── app.py                 # Main Flask application
├── templates/            # HTML templates
│   ├── base.html        # Base template with navigation
│   ├── index.html       # Home page
│   ├── word_list.html   # Word list with pagination
│   ├── word_detail.html # Individual word details
│   ├── search.html      # Advanced search page
│   ├── study.html       # Flashcard study mode
│   ├── about.html       # About page
│   └── 404.html        # Error page
├── static/              # Static assets
│   ├── css/
│   │   └── style.css   # Main stylesheet
│   └── js/
│       └── main.js     # JavaScript functionality
└── README.md           # This file
```

## Features in Detail

### Data Display
- Shows only the actual data available from CSV:
  - Word
  - Meaning (with parts of speech when available)
  - Usage examples with citations

### User Experience
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Clean Interface**: Modern, professional design
- **Fast Navigation**: Quick access to any word
- **Keyboard Shortcuts**: In study mode for efficiency

### Performance
- **In-memory Caching**: All word data loaded once at startup
- **Efficient Search**: Fast substring matching
- **Pagination**: Handles large datasets smoothly

## Technologies Used

- **Backend**: Python 3, Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Design**: Custom CSS with modern gradients and shadows
- **Icons**: Emoji for visual elements

## API Endpoints

- `GET /` - Home page
- `GET /words` - Word list (supports pagination, search, sort)
- `GET /word/<word_name>` - Word details
- `GET /search` - Search page
- `GET /api/search?q=<query>` - Search API endpoint
- `GET /study` - Study mode
- `GET /api/random-word` - Random word API
- `GET /about` - About page

## Future Enhancements

While all 5 phases are implemented, potential improvements include:
- User accounts and progress tracking
- Export functionality (PDF, Anki decks)
- Favorite words list
- More sorting options
- Advanced filtering by definition length or complexity

## Notes

- The application loads all CSV data into memory on startup for fast access
- Search is case-insensitive
- Navigation between words maintains alphabetical order
- Study mode remembers your position in the session

---

*Part of the VocabBuilder project*
