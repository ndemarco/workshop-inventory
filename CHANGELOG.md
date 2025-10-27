# Changelog

All notable changes to the Homelab Inventory System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Phase 2: Smart location management with constraints
- Phase 3: Duplicate detection with fuzzy matching
- Phase 4: AI semantic search with transformers
- Phase 5: CLI interface
- Phase 6: Voice interface with wake word

## [1.1.0] - 2024-10-27

### Added
- **Enhanced UI with Alpine.js**
  - Expandable modules and levels with inline display
  - Grid preview without page navigation
  - Hover-activated sidebar with item details
  - Smooth animations and transitions
  - Responsive mobile-first design

- **Data Model Simplification**
  - Changed from many-to-many (Item ↔ ItemLocation ↔ Location) to one-to-many (Item → Location)
  - Direct `location_id` foreign key on Item table
  - Moved `quantity` and `unit` from ItemLocation to Item
  - One item per location constraint

- **Validation & Safety**
  - Prevent multiple items in same location
  - Location occupancy checks on item creation/move
  - Clear error messages for conflicts

- **Migration Tools**
  - `migrate_to_simple_location.py` script for upgrading from v1.0
  - Automatic data migration with conflict handling
  - Logging and rollback capability

- **Documentation**
  - Comprehensive README with migration guide
  - API documentation updates
  - Troubleshooting guide
  - UI/UX feature documentation

### Changed
- Item-Location relationship simplified for voice interface readiness
- Faster queries without join table
- Clearer semantics: "Where is this item?" vs "Where can this item be?"

### Improved
- Performance: Eliminated join table overhead
- UX: Faster navigation with expandable UI
- Code clarity: Simpler models and relationships

### Fixed
- Location conflicts now properly prevented
- Grid display performance for large layouts

## [1.0.0] - 2024-10-15

### Added
- **Core Data Model**
  - Module, Level, Location, Item entities
  - Hierarchical storage organization (Module → Level → Location)
  - Row/column grid addressing for locations
  - Location characteristics (type, dimensions)

- **Web Interface**
  - Flask-based web application
  - CRUD operations for all entities
  - Module and level management
  - Item management with locations
  - Search functionality

- **Storage Features**
  - Flexible storage hierarchy
  - Custom module/level names
  - Grid-based location addressing
  - Location metadata (size, type)

- **API Endpoints**
  - RESTful API for all operations
  - JSON responses
  - Relationship navigation

- **Deployment**
  - Docker Compose setup
  - PostgreSQL database
  - Nginx reverse proxy
  - Environment configuration

- **Documentation**
  - Initial README
  - Setup instructions
  - Basic usage guide

### Technical Details
- Python 3.11+ with Flask
- PostgreSQL 14+ database
- Alpine-based Docker images
- Bootstrap 5 UI framework

## Version History Summary

| Version | Release Date | Key Features |
|---------|-------------|--------------|
| 1.1.0 | 2024-10-27 | Enhanced UI, Simplified Model, Alpine.js |
| 1.0.0 | 2024-10-15 | Initial Release, Core Features |

## Upgrade Guides

### From 1.0.0 to 1.1.0
See [Migration Guide](README.md#for-existing-installations) for detailed upgrade instructions.

**Key Steps:**
1. Backup database
2. Update code
3. Run migration script
4. Verify data

**Breaking Changes:**
- ItemLocation table removed
- Many-to-many relationship changed to one-to-many
- Items can only be in one location (was: multiple locations possible)

## Future Roadmap

### Version 1.2.0 (Phase 2) - Q1 2025
- Location type constraints and validation
- Size/geometry compatibility checks
- Smart location suggestions
- Visual capacity indicators

### Version 1.3.0 (Phase 3) - Q2 2025
- Natural language parsing
- Fuzzy matching for duplicates
- Specification extraction
- Consolidation suggestions

### Version 2.0.0 (Phase 4) - Q3 2025
- Sentence transformer integration
- Semantic search engine
- AI-powered duplicate detection
- Embedding-based similarity

### Version 2.1.0 (Phase 5) - Q4 2025
- CLI interface (`invctl` command)
- Batch operations
- Import/export tools
- Interactive shell mode

### Version 3.0.0 (Phase 6) - Q1 2026
- Voice interface with wake word
- Speech-to-text processing
- Natural language commands
- Voice feedback

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines and how to propose changes.

## Support

For bugs, feature requests, or questions:
- GitHub Issues: [Link to your repo]
- Documentation: See README.md and DEPLOYMENT.md
- Email: [Your contact]

---

**Legend:**
- `Added` - New features
- `Changed` - Changes in existing functionality
- `Deprecated` - Soon-to-be removed features
- `Removed` - Removed features
- `Fixed` - Bug fixes
- `Security` - Vulnerability fixes
- `Improved` - Enhancements and optimizations
