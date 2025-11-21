 # WordOtter Browser Extension - Technical Specification

  **Version:** 1.0.0
  **Last Updated:** November 21, 2024
  **Status:** Planning Phase

  ---

  ## 1. Overview

  ### 1.1 Purpose
  The WordOtter Browser Extension enables users to build their vocabulary collection while browsing the web by:
  - Selecting any word on any webpage
  - Right-clicking to add it to their WordOtter vocabulary database
  - Instantly fetching definitions from a dictionary API
  - Managing their word collection through an extension popup

  ### 1.2 User Flow
  1. User highlights a word on any webpage
  2. User right-clicks and selects "Add to WordOtter" from context menu
  3. Extension fetches definition from Merriam-Webster API
  4. Extension saves word to WordOtter database via Flask API
  5. User receives instant success notification
  6. User can view/manage words by clicking the extension icon

  ### 1.3 Target Browsers
  - **Primary:** Chrome/Chromium (versions 88+)
  - **Compatible:** Edge, Brave, Arc, Opera (Chromium-based)
  - **Future:** Firefox (requires manifest v2 adaptation)

  ---

  ## 2. Architecture

  ### 2.1 System Components

  ┌─────────────────────────────────────────────────────────────┐
  │                     Browser Extension                        │
  ├─────────────────────────────────────────────────────────────┤
  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
  │  │  Content    │  │  Background  │  │  Popup UI       │   │
  │  │  Script     │→→│  Service     │→→│  (Word List)    │   │
  │  │             │  │  Worker      │  │                 │   │
  │  └─────────────┘  └──────────────┘  └─────────────────┘   │
  │         ↓                ↓                                  │
  └─────────│────────────────│──────────────────────────────────┘
            │                │
            │                ↓
            │      ┌──────────────────┐
            │      │ Merriam-Webster  │
            │      │ Dictionary API   │
            │      │ (dictionaryapi   │
            │      │  .com)           │
            │      └──────────────────┘
            │                │
            │                ↓
            │      ┌──────────────────────────────────┐
            └─────→│  Flask Backend API               │
                   │  (localhost:8080)                │
                   ├──────────────────────────────────┤
                   │  • POST /api/words               │
                   │  • PUT /api/words/<word>         │
                   │  • GET /api/words                │
                   │  • GET /api/words/<word>/exists  │
                   │  • DELETE /api/words/<word>      │
                   │  • GET /api/health               │
                   └──────────────────────────────────┘
                                ↓
                   ┌──────────────────────────────────┐
                   │  Data Storage                    │
                   │  wordsmith_complete.csv          │
                   └──────────────────────────────────┘

  ### 2.2 Data Flow

  #### Adding a Word
  [1] User Selection
      └→ Content Script captures selection

  [2] Context Menu Click
      └→ Background Script receives event

  [3] Dictionary Lookup
      └→ GET https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={API_KEY}
      └→ Parse response (definition, part of speech, examples)

  [4] Save to Database
      └→ POST http://localhost:8080/api/words
      └→ Body: {word, meaning, usage, source: "browser_extension"}

  [5] Update UI
      └→ Show notification
      └→ Update badge counter
      └→ Refresh popup if open

  #### Viewing Words
  [1] User Clicks Extension Icon
      └→ Popup opens (popup.html)

  [2] Load Words
      └→ GET http://localhost:8080/api/words?limit=100

  [3] Display & Interaction
      └→ Render word list
      └→ Enable search/filter
      └→ Enable delete functionality

  ---

  ## 3. Data Model

  ### 3.1 Word Schema

  The vocabulary database uses the following schema for storing word entries:

  | Field       | Type      | Required | Constraints                    | Default              | Description                          |
  |-------------|-----------|----------|--------------------------------|----------------------|--------------------------------------|
  | word        | string    | Yes      | Max 100 chars, lowercase, PK   | -                    | The vocabulary word (primary key)    |
  | meaning     | string    | Yes      | Max 1000 chars                 | -                    | Definition and part of speech        |
  | usage       | string    | No       | Max 500 chars                  | null                 | Example sentence or usage context    |
  | source      | string    | No       | Max 50 chars                   | "browser_extension"  | Origin of the word entry             |
  | context     | string    | No       | URL format                     | null                 | URL where word was encountered       |
  | created_at  | timestamp | Yes      | ISO 8601 format                | Current timestamp    | When the word was added              |
  | updated_at  | timestamp | Yes      | ISO 8601 format                | Current timestamp    | When the word was last modified      |

  **Schema Notes:**
  - `word` is the primary key and must be unique (case-insensitive)
  - All words are stored in lowercase for consistency
  - `meaning` should include part of speech (e.g., "noun: A large animal...")
  - `source` indicates how the word was added (browser_extension, manual_entry, import, etc.)
  - Timestamps follow ISO 8601 format (e.g., "2024-11-21T10:30:00Z")

  ### 3.2 CSV Format Specification

  The vocabulary data is stored in CSV format with the following specifications:

  **File Format:**
  - **Encoding:** UTF-8
  - **Header Row:** Required (must be first line)
  - **Column Order:** word,meaning,usage,source,context,created_at,updated_at
  - **Escaping:** Standard CSV escaping rules apply
    - Fields containing commas must be enclosed in double quotes
    - Fields containing double quotes must escape them with another double quote ("")
    - Fields containing newlines must be enclosed in double quotes

  **Example CSV:**
  ```csv
  word,meaning,usage,source,context,created_at,updated_at
  ephemeral,"adjective: Lasting for a very short time; transient.","The beauty of cherry blossoms is ephemeral, lasting only a few weeks each spring.",browser_extension,https://example.com/article,2024-11-21T10:30:00Z,2024-11-21T10:30:00Z
  serendipity,"noun: The occurrence of events by chance in a happy or beneficial way.",Finding that book was pure serendipity.,manual_entry,,2024-11-20T14:22:00Z,2024-11-20T14:22:00Z
  ```

  **Validation Rules:**
  - Header row must match exactly: word,meaning,usage,source,context,created_at,updated_at
  - Empty optional fields (usage, source, context) should be represented as empty strings between commas
  - Timestamps must be valid ISO 8601 format
  - Word field cannot be empty

  ---

  ## 4. Backend API Specification

  ### 3.1 New Endpoints

  #### `POST /api/words`
  **Purpose:** Add a new word to the vocabulary database

  **Request Body Fields:**
  - `word` (string, required): The vocabulary word to add
  - `meaning` (string, required): Definition and part of speech
  - `usage` (string, optional): Example sentence or usage context
  - `source` (string, optional): Origin of the word entry (default: "browser_extension")
  - `context` (string, optional): URL where word was encountered

  **Request Example:**
  ```json
  {
    "word": "ephemeral",
    "meaning": "adjective: Lasting for a very short time; transient.",
    "usage": "The beauty of cherry blossoms is ephemeral, lasting only a few weeks each spring.",
    "source": "browser_extension",
    "context": "Selected from: https://example.com/article"
  }

  Response (Success - 201):
  {
    "success": true,
    "message": "Word added successfully",
    "word": "ephemeral",
    "total_words": 3317
  }

  Response (Already Exists - 409):
  {
    "success": false,
    "error": "Word already exists",
    "existing_data": {
      "word": "ephemeral",
      "meaning": "...",
      "usage": "..."
    }
  }

  Response (Error - 400):
  {
    "success": false,
    "error": "Missing required field: word"
  }

  #### `PUT /api/words/<word>`
  **Purpose:** Update an existing word in the vocabulary database

  **URL Parameters:**
  - `word` (string, required): The word to update

  **Request Body Fields:**
  - `meaning` (string, optional): Updated definition and part of speech
  - `usage` (string, optional): Updated example sentence or usage context

  **Request Example:**
  ```json
  {
    "meaning": "adjective: Lasting for a very short time; transient; fleeting.",
    "usage": "The ephemeral nature of life makes every moment precious."
  }
  ```

  **Response (Success - 200):**
  ```json
  {
    "success": true,
    "message": "Word updated successfully",
    "word": {
      "word": "ephemeral",
      "meaning": "adjective: Lasting for a very short time; transient; fleeting.",
      "usage": "The ephemeral nature of life makes every moment precious.",
      "source": "browser_extension",
      "context": "https://example.com/article",
      "created_at": "2024-11-20T10:30:00Z",
      "updated_at": "2024-11-21T14:22:00Z"
    }
  }
  ```

  **Response (Not Found - 404):**
  ```json
  {
    "success": false,
    "error": "Word not found"
  }
  ```

  **Response (Validation Error - 400):**
  ```json
  {
    "success": false,
    "error": "At least one field (meaning or usage) must be provided"
  }
  ```

  #### `GET /api/words/<word>/exists`

  Purpose: Check if a word exists in the database

  Response (Exists - 200):
  {
    "exists": true,
    "data": {
      "word": "ephemeral",
      "meaning": "adjective: Lasting for a very short time",
      "usage": "The beauty of cherry blossoms..."
    }
  }

  Response (Not Found - 200):
  {
    "exists": false
  }

  GET /api/words

  Purpose: Retrieve list of all words (paginated)

  Query Parameters:
  - page (int, default: 1)
  - limit (int, default: 50, max: 500)
  - search (string, optional)
  - sort (string: "alpha" | "recent", default: "alpha")

  Response (200):
  {
    "words": [
      {
        "word": "aardvark",
        "meaning": "noun: A nocturnal burrowing mammal...",
        "usage": "The aardvark is native to Africa."
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 3316,
      "total_pages": 67
    }
  }

  DELETE /api/words/<word>

  Purpose: Remove a word from the database

  Response (Success - 200):
  {
    "success": true,
    "message": "Word deleted successfully",
    "word": "ephemeral"
  }

  Response (Not Found - 404):
  {
    "success": false,
    "error": "Word not found"
  }

  #### `GET /api/health`
  **Purpose:** Health check endpoint for monitoring service availability

  **Response (Success - 200):**
  ```json
  {
    "status": "ok",
    "timestamp": "2024-11-21T14:30:00Z"
  }
  ```

  **Usage:**
  - Used by monitoring tools to verify API is running
  - Returns current server timestamp in ISO 8601 format
  - Always returns 200 OK if service is operational
  - No authentication required

  ---

  ### 4.2 CORS Configuration

  **Required Headers:**
  - Access-Control-Allow-Origin: chrome-extension://{EXTENSION_ID}
  - Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
  - Access-Control-Allow-Headers: Content-Type
  - Access-Control-Max-Age: 3600

  **Configuration Requirements:**
  - Development: Allow all Chrome extension origins (chrome-extension://*)
  - Production: Restrict to specific extension ID and localhost
  - Use flask-cors library for implementation

  3.3 Dictionary API Integration

  Service: Merriam-Webster Collegiate Dictionary API
  Endpoint: https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={API_KEY}
  Authentication: API key required (obtained from developer.dictionaryapi.com)
  Rate Limit: 1000 requests per day (free tier)

  Response Format:
  The API returns a JSON array containing dictionary entries with:
  - Word headword and pronunciation (IPA)
  - Functional label (part of speech)
  - Definitions organized by sense
  - Usage examples
  - Synonyms and related words

  **Example API Response:**
  ```json
  [
    {
      "meta": {
        "id": "ephemeral",
        "uuid": "...",
        "sort": "030470000",
        "src": "collegiate",
        "section": "alpha",
        "stems": ["ephemeral", "ephemerally", "ephemeralness"],
        "offensive": false
      },
      "hwi": {
        "hw": "ephem*er*al",
        "prs": [
          {
            "mw": "i-ˈfem-rəl",
            "sound": {
              "audio": "epheme01"
            }
          }
        ]
      },
      "fl": "adjective",
      "def": [
        {
          "sseq": [
            [
              [
                "sense",
                {
                  "dt": [
                    ["text", "lasting a very short time"]
                  ]
                }
              ]
            ]
          ]
        }
      ],
      "shortdef": [
        "lasting a very short time",
        "lasting one day only",
        "lasting a very short time"
      ],
      "date": "1576"
    }
  ]
  ```

  **Key Fields for Extraction:**
  - `shortdef`: Array of short definitions (use first element)
  - `fl`: Functional label/part of speech (e.g., "adjective", "noun", "verb")
  - `hwi.hw`: Headword with pronunciation markers

  Error Handling:
  - 404: Word not found → Save word with placeholder meaning
  - 429: Rate limit exceeded → Queue for later or show error
  - 403: Invalid API key → Show configuration error
  - 500: API error → Fallback to user-provided definition

  3.4 File Locking for CSV

  **Purpose:** Prevent data corruption from concurrent writes

  **Requirements:**
  - Implement exclusive file locking when writing to CSV
  - Use fcntl.flock on Unix systems
  - Use filelock library for cross-platform compatibility (Windows)
  - Ensure proper lock release in finally blocks
  - Flush and fsync after writes to guarantee data persistence

  ---
  4. Browser Extension Specification

  4.1 Manifest Requirements

  The extension must use Manifest V3 with the following specifications:

  **Required Permissions:**
  - contextMenus: For right-click menu integration
  - storage: For saving extension settings
  - notifications: For displaying success/error messages
  - activeTab: For accessing the current page content

  **Required Host Permissions:**
  - http://localhost:8080/*: For local Flask API access
  - https://www.dictionaryapi.com/*: For Merriam-Webster API access

  **Components:**
  - Service worker (background.js): Handles API calls and business logic
  - Content script (content.js): Captures text selection from webpages
  - Popup UI (popup.html): Displays user's word collection
  - Options page (options.html): Configures extension settings
  - Extension icons: 16x16, 48x48, and 128x128 pixel sizes

  4.2 Content Script Specification

  **Purpose:** Runs on every webpage to capture text selection and page context

  **Responsibilities:**
  - Detect text selection on the current webpage
  - Listen for messages from background script
  - Provide selected text and page context (URL, title) when requested
  - Run on all URLs at document idle state

  **Message Protocol:**
  - Receive request for selection from background script
  - Respond with page context including: URL, page title, and selected text

  4.3 Background Script Specification

  **Purpose:** Service worker handling API calls, context menu, and extension state

  **Responsibilities:**
  - Create and manage context menu with "Add [word] to WordOtter" option
  - Handle context menu click events
  - Fetch definitions from Merriam-Webster Dictionary API
  - Save words to Flask backend API
  - Display notifications for success/error states
  - Update extension badge with word count
  - Manage extension state and settings

  **Add Word Workflow:**
  1. Receive context menu click event with selected text
  2. Normalize word (trim, lowercase)
  3. Check if word already exists in database
  4. If new: Fetch definition from Merriam-Webster API
  5. Save word data to Flask API (word, meaning, usage, source, context)
  6. Update UI: Show notification and refresh badge counter
  7. Handle errors gracefully with appropriate user feedback

  **API Integration Requirements:**
  - Retrieve API URL from chrome.storage (configurable by user)
  - Use Merriam-Webster API with API key for definition lookup
  - Parse API response to extract: part of speech, definition, example usage, phonetic
  - Implement fallback behavior for API failures
  - Handle CORS properly with required headers

  **Badge Management:**
  - Display total word count on extension icon
  - Update badge after adding/deleting words
  - Show error indicator (!) if backend is unreachable
  - Use green color (#4CAF50) for success state

  **Notification System:**
  - Show success notification when word is added
  - Show info notification if word already exists
  - Show error notification for failures (network, API, etc.)

  4.4 Popup UI Specification

  **Purpose:** Display and manage user's word collection in a popup interface

  **Dimensions:** 400px width × 600px height

  **Layout Components:**
  1. **Header Section:**
     - WordOtter logo and branding
     - Total word count display
     - Gradient background (#667eea to #764ba2)

  2. **Search Section:**
     - Search input field for filtering words
     - Real-time search with debounce (300ms)
     - Placeholder: "Search your words..."

  3. **Word List Section:**
     - Scrollable list (450px height) displaying up to 100 words
     - Each word item shows:
       - Word title (16px, bold)
       - Truncated meaning (80 characters max, 13px)
       - Delete button (× icon)
     - Hover effects on word items
     - Empty state message when no words exist

  4. **Footer Section:**
     - "Open Web App" button to launch full WordOtter application
     - Primary action button style

  **Functionality:**
  - Load words from Flask API on popup open
  - Support search/filter functionality
  - Allow word deletion with confirmation
  - Refresh badge count after deletion
  - Handle error states (API unreachable, no data)
  - Display empty state with instructions for new users

  **Styling Requirements:**
  - Modern, clean design with system fonts
  - Card-based layout with subtle shadows
  - Smooth transitions and hover effects
  - Responsive scrolling for long word lists
  - Color scheme: Purple gradient header, white cards, light gray background

  4.5 Options Page Specification

  **Purpose:** Configure extension settings and API connection

  **Settings Categories:**

  1. **API Configuration:**
     - Flask API URL input field
       - Default value: http://localhost:8080
       - Help text explaining what this URL is for
     - Test Connection button
       - Verifies API is reachable
       - Shows success/error status with visual feedback
     - Merriam-Webster API key input field
       - Securely stored in chrome.storage
       - Required for dictionary lookups

  2. **User Preferences:**
     - Auto-fetch definitions toggle (default: enabled)
       - When enabled, automatically fetches definitions for selected words
     - Show notifications toggle (default: enabled)
       - Controls whether to display browser notifications

  **Functionality:**
  - Load saved settings from chrome.storage.sync on page load
  - Save settings to chrome.storage.sync when "Save Settings" button is clicked
  - Display save confirmation message (3-second timeout)
  - Test API connection by making test request to /api/words endpoint
  - Validate API URL format before saving
  - Persist settings across devices (Chrome Sync)

  **Layout:**
  - Clean, centered container design
  - Grouped settings by category with headers
  - Clear labels and help text for each setting
  - Primary action button for saving
  - Status indicators for connection test
  - Consistent spacing and typography

  ---
  5. File Structure

  VocabBuilder/
  ├── browser-extension/              # NEW: Browser extension
  │   ├── manifest.json               # Extension manifest (v3)
  │   ├── background.js               # Service worker (~200 lines)
  │   ├── content.js                  # Content script (~50 lines)
  │   │
  │   ├── popup/
  │   │   ├── popup.html              # Popup UI structure
  │   │   ├── popup.js                # Popup logic (~150 lines)
  │   │   └── popup.css               # Popup styles (~200 lines)
  │   │
  │   ├── options/
  │   │   ├── options.html            # Settings page
  │   │   ├── options.js              # Settings logic (~100 lines)
  │   │   └── options.css             # Settings styles
  │   │
  │   ├── icons/
  │   │   ├── icon16.png              # Extension icon (16x16)
  │   │   ├── icon48.png              # Extension icon (48x48)
  │   │   └── icon128.png             # Extension icon (128x128)
  │   │
  │   └── README.md                   # Extension documentation
  │
  ├── src/
  │   ├── scrape_words.py
  │   ├── extract_meanings.py
  │   ├── check_status.py
  │   └── dictionary_api.py           # NEW: Dictionary API module
  │
  ├── web/
  │   ├── app.py                      # MODIFIED: Add new API endpoints
  │   ├── templates/
  │   ├── static/
  │   └── README.md
  │
  ├── resources/
  │   ├── wordsmith_words.csv
  │   ├── wordsmith_complete.csv      # MODIFIED: Extension will append here
  │   └── wordsmith_extraction.log
  │
  ├── requirements.txt                # MODIFIED: Add flask-cors, filelock
  └── README.md                       # MODIFIED: Document extension

  ---
  6. Implementation Checklist

  Phase 1: Backend API (Estimated: 2-3 hours)

  - Install dependencies (flask-cors, filelock)
  - Create src/dictionary_api.py module
    - fetch_definition(word) function
    - format_for_wordotter(api_response) function
    - Error handling and fallbacks
  - Add CORS to web/app.py
  - Implement POST /api/words endpoint
    - Validate request data
    - Check for duplicates
    - Fetch definition from Dictionary API
    - Write to CSV with file locking
    - Reload in-memory cache
  - Implement GET /api/words/<word>/exists endpoint
  - Implement GET /api/words endpoint (paginated list)
  - Implement DELETE /api/words/<word> endpoint
  - Test all endpoints with curl/Postman
  - Write pytest tests for new endpoints

  Phase 2: Extension Core (Estimated: 3-4 hours)

  - Create browser-extension/ directory
  - Create manifest.json
  - Create placeholder icons (or design custom icons)
  - Implement content.js
    - Text selection detection
    - Message listener
  - Implement background.js
    - Context menu creation
    - Context menu click handler
    - Dictionary API integration
    - Flask API integration
    - Notification system
    - Badge management
  - Test basic functionality: select text → right-click → add word

  Phase 3: Popup UI (Estimated: 2-3 hours)

  - Create popup/popup.html structure
  - Create popup/popup.css styles
  - Implement popup/popup.js
    - Load words from API
    - Display word list
    - Search functionality
    - Delete functionality
    - "Open Web App" button
  - Test popup interactions

  Phase 4: Options Page (Estimated: 1-2 hours)

  - Create options/options.html
  - Create options/options.css
  - Implement options/options.js
    - Load/save settings
    - API URL configuration
    - Connection test
  - Test settings persistence

  Phase 5: Testing & Polish (Estimated: 2-3 hours)

  - Test full user flow end-to-end
  - Test error scenarios
    - Flask app offline
    - Dictionary API failure
    - Network errors
    - Invalid words
  - Test edge cases
    - Multi-word selections
    - Special characters
    - Very long words
    - Duplicate adds
  - Performance testing
    - Large word lists (1000+ words)
    - Popup load time
  - Browser testing
    - Chrome
    - Edge
    - Brave
  - Write documentation
    - browser-extension/README.md
    - Update main README.md
    - Add screenshots

  Phase 6: Documentation (Estimated: 1 hour)

  - Write extension installation guide
  - Create usage screenshots/GIFs
  - Document development setup
  - Update main README with extension info
  - Create troubleshooting guide

  ---
  7. Testing Strategy

  7.1 Backend API Tests

  **Test Coverage Requirements:**
  - Test POST /api/words endpoint with valid data (expect 201 Created)
  - Test POST /api/words with duplicate word (expect 409 Conflict)
  - Test GET /api/words/<word>/exists endpoint (verify existence check)
  - Test DELETE /api/words/<word> endpoint (verify deletion)
  - Test pagination and search parameters for GET /api/words
  - Test error handling for invalid input
  - Test CORS headers are properly set

  7.2 Extension Tests

  Manual Test Cases:

  | Test ID | Scenario                      | Expected Result                        |
  |---------|-------------------------------|----------------------------------------|
  | EXT-001 | Select text and right-click   | Context menu shows "Add to WordOtter"  |
  | EXT-002 | Click "Add to WordOtter"      | Word is added, notification shown      |
  | EXT-003 | Add duplicate word            | Notification: "Word already exists"    |
  | EXT-004 | Click extension icon          | Popup shows word list                  |
  | EXT-005 | Search in popup               | Results filter in real-time            |
  | EXT-006 | Delete word from popup        | Word removed, list refreshes           |
  | EXT-007 | Flask app offline             | Error notification shown               |
  | EXT-008 | Invalid word (Dictionary API) | Word saved with placeholder definition |
  | EXT-009 | Badge counter                 | Shows correct word count               |
  | EXT-010 | Options page                  | Settings save and persist              |

  **Browser Console Test Areas:**
  - Test message passing between content script and background script
  - Test chrome.storage operations for settings persistence
  - Test API connectivity to Flask backend
  - Verify extension permissions are properly granted

  ---
  8. Error Handling

  8.1 Backend Errors

  | Error                   | Scenario                | Response                                         |
  |-------------------------|-------------------------|--------------------------------------------------|
  | 400 Bad Request         | Missing required fields | {"error": "Missing field: word"}                 |
  | 409 Conflict            | Word already exists     | {"error": "Word exists", "existing_data": {...}} |
  | 500 Server Error        | CSV write failure       | {"error": "Database error"}                      |
  | 503 Service Unavailable | Dictionary API down     | {"error": "External API unavailable"}            |

  8.2 Extension Errors

  | Error              | Scenario                            | Handling                                         |
  |--------------------|-------------------------------------|--------------------------------------------------|
  | Network Error      | Flask app offline                   | Show notification: "Cannot connect to WordOtter" |
  | CORS Error         | Manifest misconfiguration           | Log error, show setup instructions               |
  | Dictionary API 404 | Word not found                      | Save word with placeholder definition            |
  | Dictionary API 429 | Rate limit exceeded                 | Queue word for later processing                  |
  | Selection Empty    | User right-clicks without selection | Disable context menu item                        |

  **Notification Message Examples:**
  - Success: "✓ Added: [word]"
  - Info/Warning: "Word already exists"
  - Error: "Failed to connect to WordOtter. Is the Flask app running?"

  ---
  9. Security Considerations

  9.1 CORS Security

  - Only allow specific origins (extension ID)
  - Validate Content-Type headers
  - Implement CSRF tokens for production

  9.2 Input Validation

  - Sanitize user input (word, meaning, usage)
  - Prevent CSV injection
  - Limit string lengths (word: 100 chars, meaning: 1000 chars, usage: 500 chars)
  - Block special characters in word field

  9.3 Rate Limiting

  - Limit API calls from extension (10 requests/minute)
  - Implement exponential backoff for retries
  - Monitor for abuse

  9.4 Data Privacy

  - No user authentication (phase 1)
  - All data stored locally
  - No telemetry or analytics
  - Future: Add user accounts with encryption

  ---
  10. Performance Targets

  10.1 Backend

  - API response time: < 200ms (95th percentile)
  - Dictionary API timeout: 5 seconds
  - CSV write time: < 50ms
  - File lock wait: < 100ms

  10.2 Extension

  - Context menu response: Instant (< 100ms)
  - Dictionary lookup: < 2 seconds
  - Popup load time: < 500ms
  - Word save operation: < 3 seconds (end-to-end)

  10.3 Data Limits

  - Popup word list: Max 100 words initially loaded
  - Search results: Max 50 results
  - Maximum word length: 100 characters
  - Maximum definition length: 1000 characters

  ---
  11. Dependencies

  11.1 Backend (requirements.txt)

  **Python Version:** Python 3.10+

  **Required Packages:**
  requests==2.31.0
  beautifulsoup4==4.12.2
  Flask==2.3.2
  Werkzeug==2.3.7
  gunicorn==21.2.0
  flask-cors==4.0.0        # NEW
  filelock==3.13.0         # NEW

  **Development Dependencies:**
  pytest==7.4.0
  pytest-flask==2.0.3
  black==23.7.0
  flake8==6.1.0
  mypy==1.5.0

  11.2 Extension

  - No external dependencies (vanilla JavaScript)
  - Chrome Extension API (built-in)
  - Uses browser's native fetch API

  ---
  12. Deployment Instructions

  12.1 Development Setup

  Backend:
  # Install dependencies
  pip install -r requirements.txt

  # Start Flask app
  cd web
  python app.py

  Extension:
  # 1. Open Chrome
  # 2. Navigate to chrome://extensions/
  # 3. Enable "Developer mode"
  # 4. Click "Load unpacked"
  # 5. Select VocabBuilder/browser-extension/ directory

  12.2 Production Deployment

  Backend:
  - Deploy Flask app to Render/Heroku/DigitalOcean
  - Update CORS to allow specific extension ID
  - Migrate CSV to PostgreSQL for scalability
  - Add authentication (API keys)

  Extension:
  - Package extension: zip -r wordotter-extension.zip browser-extension/
  - Submit to Chrome Web Store
  - Update manifest with production API URL
  - Implement auto-update mechanism

  ---
  13. Success Metrics

  13.1 Technical Metrics

  - API uptime: > 99.5%
  - Average word save time: < 3 seconds
  - Extension install size: < 1 MB
  - Memory usage: < 50 MB
  - Battery impact: Minimal

  13.2 User Metrics

  - Words added per user per week: Track
  - Popup engagement rate: > 20%
  - Extension retention (7-day): > 50%
  - Word deletion rate: < 5%

  ---
  14. Documentation Deliverables

  14.1 User Documentation

  - browser-extension/README.md - Installation & usage
  - Screenshots of key features
  - Video walkthrough (optional)
  - FAQ / Troubleshooting guide

  14.2 Developer Documentation

  - API endpoint documentation (this spec)
  - Extension architecture diagram
  - Development setup guide
  - Contributing guidelines

  14.3 Code Documentation

  - Inline comments for complex logic
  - JSDoc comments for functions
  - Python docstrings for new modules

  ---
  15. Timeline Estimate

  Total Estimated Time: 10-15 hours

  | Phase            | Estimated Time |
  |------------------|----------------|
  | Backend API      | 2-3 hours      |
  | Extension Core   | 3-4 hours      |
  | Popup UI         | 2-3 hours      |
  | Options Page     | 1-2 hours      |
  | Testing & Polish | 2-3 hours      |
  | Documentation    | 1 hour         |

  Milestones:
  - Day 1: Backend API complete, basic extension working
  - Day 2: Popup UI complete, full functionality tested
  - Day 3: Polish, documentation, ready for use

  ---
  Appendix A: API Usage Examples

  **Example 1: Add Word via Extension**
  - Endpoint: POST /api/words
  - Content-Type: application/json
  - Body fields: word, meaning, usage, source, context
  - Expected response: 201 Created with success message

  **Example 2: Check Word Exists**
  - Endpoint: GET /api/words/{word}/exists
  - Expected response: 200 OK with exists boolean and optional data

  **Example 3: Get All Words**
  - Endpoint: GET /api/words
  - Query parameters: limit, search
  - Expected response: 200 OK with words array and pagination info

  **Example 4: Delete Word**
  - Endpoint: DELETE /api/words/{word}
  - Expected response: 200 OK with success message


