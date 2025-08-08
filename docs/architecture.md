# VocabBuilder Architecture

## System Overview

VocabBuilder follows a modular, pipeline-based architecture designed for extensibility and maintainability. The system is composed of loosely coupled components that can operate independently while sharing common data formats.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      VocabBuilder System                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐     ┌──────────────┐    ┌──────────────┐ │
│  │ Data Sources │ ──> │   Scrapers   │ ──>│  Processing  │ │
│  └──────────────┘     └──────────────┘    └──────────────┘ │
│         │                     │                    │         │
│         v                     v                    v         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    Data Storage Layer                 │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │   │
│  │  │ Raw Data   │  │ Processed  │  │   Logs     │    │   │
│  │  │   (CSV)    │  │ Data (CSV) │  │   (.log)   │    │   │
│  │  └────────────┘  └────────────┘  └────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
│                              │                               │
│                              v                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  Application Layer                    │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │   │
│  │  │    CLI     │  │  Web API   │  │  Web UI    │    │   │
│  │  │ (Current)  │  │  (Planned) │  │ (Planned)  │    │   │
│  │  └────────────┘  └────────────┘  └────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Data Sources Layer

The foundation of the system, responsible for identifying vocabulary sources.

**Current Sources:**
- Wordsmith.org (A Word A Day archives)

**Planned Sources:**
- Dictionary APIs (Merriam-Webster, Oxford, Cambridge)
- Literature databases (Project Gutenberg)
- Academic word lists (SAT, GRE, TOEFL)
- Etymology databases
- Language learning platforms

### 2. Scraper Layer

Modular scrapers that extract data from various sources.

**Components:**

#### `scrape_words.py`
- **Purpose**: Harvest word URLs from source websites
- **Features**:
  - Duplicate detection
  - Incremental scraping
  - Resume capability
  - Merge with existing data
- **Output**: CSV with word-URL mappings

#### `extract_meanings.py`
- **Purpose**: Extract detailed word information
- **Features**:
  - Parallel processing capability
  - Progress tracking
  - Error recovery
  - Resume from interruption
- **Output**: Complete word data with meanings and usage

### 3. Data Storage Layer

Centralized storage for all vocabulary data.

**Current Implementation:**
- CSV files for portability and simplicity
- Separate files for raw and processed data
- Log files for debugging and auditing

**Future Implementation:**
- SQLite for local development
- PostgreSQL for production
- Redis for caching
- Elasticsearch for advanced search

### 4. Processing Pipeline

The data transformation and enrichment pipeline.

```python
# Pipeline stages (planned)
class VocabularyPipeline:
    stages = [
        'scrape',       # Get raw word list
        'extract',      # Extract definitions
        'enrich',       # Add etymology, pronunciation
        'categorize',   # Tag by difficulty, domain
        'deduplicate',  # Remove duplicates
        'validate',     # Ensure data quality
        'store'         # Save to database
    ]
```

### 5. Application Layer

User-facing interfaces for interacting with the vocabulary data.

**Current:**
- Command-line interface (CLI)
- Status checking utilities

**Planned:**
- RESTful API
- Web interface
- Mobile applications
- Browser extensions

## Data Flow

### 1. Scraping Flow

```
Website Archives
       │
       v
  [Scraper Module]
       │
       ├──> Check existing words
       │
       ├──> Identify new words
       │
       └──> Save to CSV
```

### 2. Extraction Flow

```
Word URLs (CSV)
       │
       v
  [Extractor Module]
       │
       ├──> Load processed words
       │
       ├──> Skip duplicates
       │
       ├──> Extract word data
       │         │
       │         ├──> Word
       │         ├──> Meaning
       │         └──> Usage examples
       │
       └──> Append to complete CSV
```

### 3. Resume Flow

```
Interruption Detected
       │
       v
  [Save Current State]
       │
       v
  [Next Run]
       │
       ├──> Load previous state
       │
       ├──> Identify remaining work
       │
       └──> Continue processing
```

## Design Patterns

### 1. **Pipeline Pattern**
Each component processes data and passes it to the next stage.

### 2. **Repository Pattern**
Abstract data storage behind interfaces for flexibility.

### 3. **Strategy Pattern**
Different scraping strategies for different sources.

### 4. **Observer Pattern**
Progress notifications and logging throughout the pipeline.

### 5. **Factory Pattern**
Create appropriate scrapers based on source type.

## Error Handling Strategy

### Levels of Error Handling

1. **Network Errors**
   - Retry with exponential backoff
   - Fallback to cached data
   - Log failures for manual review

2. **Parsing Errors**
   - Skip malformed entries
   - Log for debugging
   - Continue processing

3. **Storage Errors**
   - Write to temporary files
   - Atomic operations
   - Backup before modifications

4. **System Errors**
   - Graceful shutdown
   - State preservation
   - Clear error messages

## Performance Considerations

### Current Optimizations

1. **Duplicate Detection**
   - Set-based lookups (O(1) complexity)
   - Pre-load existing data into memory

2. **Progress Saving**
   - Flush after each word
   - Atomic writes

3. **Rate Limiting**
   - 1-second delay between requests
   - Respects robots.txt

### Future Optimizations

1. **Parallel Processing**
   - Multi-threaded extraction
   - Async I/O operations

2. **Caching**
   - Redis for frequently accessed words
   - CDN for static content

3. **Database Indexing**
   - Full-text search indexes
   - Composite indexes for queries

## Scalability Design

### Horizontal Scaling

```
Load Balancer
     │
     ├──> Scraper Instance 1
     ├──> Scraper Instance 2
     └──> Scraper Instance N
           │
           v
     Message Queue (RabbitMQ/Kafka)
           │
           v
     Processing Workers
           │
           v
     Database Cluster
```

### Vertical Scaling

- Increase memory for larger datasets
- SSD storage for faster I/O
- GPU acceleration for NLP tasks (future)

## Security Considerations

### Current Implementation

1. **Input Validation**
   - Sanitize scraped content
   - Escape special characters

2. **Rate Limiting**
   - Respect source website limits
   - Prevent denial of service

### Future Implementation

1. **API Security**
   - JWT authentication
   - Rate limiting per user
   - API key management

2. **Data Privacy**
   - Encryption at rest
   - Secure connections (HTTPS)
   - GDPR compliance

## Technology Stack

### Current Stack

- **Language**: Python 3.x
- **Web Scraping**: BeautifulSoup4, Requests
- **Data Storage**: CSV files
- **Logging**: Python logging module

### Planned Stack

- **Backend**: FastAPI/Django
- **Database**: PostgreSQL, Redis
- **Frontend**: React/Vue.js
- **Mobile**: React Native
- **Message Queue**: RabbitMQ/Kafka
- **Search**: Elasticsearch
- **Deployment**: Docker, Kubernetes
- **Monitoring**: Prometheus, Grafana

## Deployment Architecture

### Development Environment

```
Local Machine
     │
     ├──> Python Virtual Environment
     ├──> Local CSV Storage
     └──> Console Output
```

### Production Environment (Planned)

```
Docker Container
     │
     ├──> Application Server
     ├──> Database Container
     ├──> Redis Cache
     └──> Nginx Reverse Proxy
```

## Monitoring and Observability

### Current Monitoring

- Log files for debugging
- Progress indicators in CLI
- Status check utility

### Planned Monitoring

- Application metrics (Prometheus)
- Error tracking (Sentry)
- Performance monitoring (New Relic)
- Log aggregation (ELK stack)

## Conclusion

The VocabBuilder architecture is designed to be:

1. **Modular**: Easy to add new components
2. **Scalable**: Can handle growing data and users
3. **Reliable**: Robust error handling and recovery
4. **Maintainable**: Clean separation of concerns
5. **Extensible**: Simple to add new features

This architecture provides a solid foundation for growth from a simple scraping tool to a comprehensive vocabulary learning platform.

---

*Last updated: August 2024*
