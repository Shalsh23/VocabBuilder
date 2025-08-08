# VocabBuilder Roadmap

## Project Vision

VocabBuilder aims to become a comprehensive vocabulary learning tool that aggregates interesting words from multiple sources, making vocabulary expansion accessible and enjoyable.

## Current Status (August 2024)

### ✅ Completed Features

- **Web Scraping Infrastructure**
  - Wordsmith.org integration
  - Robust error handling
  - Resume capability for interrupted sessions
  
- **Data Processing**
  - Word extraction with definitions and usage examples
  - Duplicate detection
  - Progress tracking
  - CSV storage format

- **Utility Tools**
  - Status checking script
  - Logging system
  - Basic CLI interface

## Near-term Goals

### Data Source Expansion
- Integrate additional vocabulary sources (specific sources TBD based on availability and licensing)
- Improve data normalization across different source formats
- Enhance extraction to capture more metadata (etymology, pronunciation where available)

### Technical Improvements
- Migrate from CSV to database storage for better performance
- Implement data validation and quality checks
- Add configuration file support for easier customization
- Improve error recovery mechanisms

### User Experience
- Create a simple web interface for browsing collected vocabulary
- Add search and filter capabilities
- Implement basic export options (PDF, Anki deck format)

## Potential Future Directions

*These are possibilities being explored, not commitments:*

- **Learning Features**: Spaced repetition, progress tracking
- **API Development**: RESTful API for programmatic access
- **Mobile Support**: Responsive web design or native apps
- **Community Features**: Sharing word lists, collaborative learning
- **Advanced Processing**: NLP for difficulty scoring, domain categorization

## Development Philosophy

### Principles
1. **Incremental Development**: Build features as needed, avoid over-engineering
2. **User Feedback Driven**: Let actual usage guide feature priorities
3. **Open Source First**: Maintain transparency and welcome contributions
4. **Respect Content Sources**: Always comply with terms of service and attribution

### Non-Goals
- Not trying to replace dedicated dictionary apps
- Not focused on real-time translation
- Not building a language learning course platform

## Contributing

VocabBuilder is open to contributions! Areas where help is particularly welcome:

- Adding new data source integrations
- Improving word extraction accuracy
- Creating export format converters
- Writing documentation and tutorials
- Testing and bug reports

## Technical Considerations

### Current Stack
- Python 3.x
- BeautifulSoup4 for web scraping
- CSV for data storage
- Basic logging

### Future Considerations
- Database (SQLite/PostgreSQL) for scalability
- Web framework (FastAPI/Flask) if web interface is added
- Docker for easier deployment
- GitHub Actions for CI/CD

## Versioning

Following semantic versioning (MAJOR.MINOR.PATCH):

- **v1.0.0** - Current: Basic Wordsmith.org scraper with resume capability
- **v1.1.0** - Planned: Additional data sources
- **v1.2.0** - Planned: Database migration
- **v2.0.0** - Potential: Web interface introduction

## Maintenance & Support

### Current Focus
- Bug fixes and stability improvements
- Documentation updates
- Performance optimizations

### Community
- GitHub Issues for bug reports and feature requests
- Pull requests welcome with prior discussion
- Documentation contributions always appreciated

## Metrics for Success

Rather than arbitrary user numbers or revenue targets, success will be measured by:

- Code quality and maintainability
- Community engagement and contributions
- User satisfaction with core features
- Learning outcomes for vocabulary expansion

## Notes

This roadmap is intentionally flexible and will evolve based on:
- User feedback and needs
- Available development time
- Community contributions
- Technical constraints and opportunities

The project maintains a "build what's needed" approach rather than speculating on features that may never be used.

---

*Last updated: August 2024*  
*This is a living document and will be updated as the project evolves.*
