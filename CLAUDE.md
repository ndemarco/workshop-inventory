# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Homelab Inventory System - A Flask-based web application for managing workshop/lab inventory with hierarchical storage organization (Modules → Levels → Locations → Items). Uses Alpine.js for reactive UI and PostgreSQL for data persistence.

**Current Phase:** Phase 1 - Enhanced UI with simplified data model

## Development Commands

### Docker Development (Primary Method)

```bash
# Initial setup (creates .env, builds, starts services)
./setup.sh

# Manual Docker commands
docker-compose up -d              # Start all services
docker-compose down               # Stop all services
docker-compose down -v            # Stop and remove volumes (destroys data)
docker-compose logs -f [service]  # View logs (backend, postgres, nginx)
docker-compose restart [service]  # Restart specific service
docker-compose exec backend bash  # Shell into backend container
docker-compose exec postgres psql -U inventoryuser inventory  # Database shell

# Rebuild after dependency changes
docker-compose up --build
```

### Local Development (Without Docker)

```bash
# Requires PostgreSQL installed locally
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

export DATABASE_URL="postgresql://inventoryuser:inventorypass@localhost:5432/inventory"
export FLASK_ENV=development

python run.py  # Runs on http://localhost:5000
```

### Database Operations

```bash
# Database migrations (after model changes)
docker-compose exec backend flask db migrate -m "Description of changes"
docker-compose exec backend flask db upgrade

# Run migration script (old schema → new schema)
docker-compose exec backend python migrate_to_simple_location.py

# Backup database
docker-compose exec -T postgres pg_dump -U inventoryuser inventory > backup_$(date +%Y%m%d).sql

# Restore database
docker-compose exec -T postgres psql -U inventoryuser inventory < backup.sql

# Check database is ready
docker-compose exec -T postgres pg_isready -U inventoryuser
```

### Testing API Endpoints

```bash
# Test endpoints
curl http://localhost:5000/api/items
curl http://localhost:5000/api/items/1
curl http://localhost:5000/api/modules
curl http://localhost:5000/api/locations/1
```

## Architecture

### Data Model (Simplified - Phase 1)

The system uses a simplified one-to-many relationship where each item can only be stored in **one location**:

```
Module (storage unit: cabinet, shelving)
  └── Level (drawer, shelf) [1..n]
      └── Location (bin/cell in grid) [1..n]
          └── Item (physical item) [0..1]  # Max one item per location
```

**Key Models:**
- `Module`: Top-level storage units (e.g., "Zeus Electronics Cabinet")
- `Level`: Subdivisions within modules (drawers, shelves) with grid dimensions (rows × columns)
- `Location`: Individual storage cells identified by row/column (e.g., "A3", "B2")
- `Item`: Inventory items with direct `location_id` foreign key

**Critical Design Decision:** One item per location, one location per item. This simplifies the mental model and prepares for future voice interface.

### Project Structure

```
backend/
├── app/
│   ├── __init__.py          # Flask app factory, blueprint registration
│   ├── models.py            # SQLAlchemy models (Module, Level, Location, Item)
│   └── routes/              # Blueprint route handlers
│       ├── main.py          # Dashboard routes
│       ├── modules.py       # Module/Level CRUD + grid management
│       ├── items.py         # Item CRUD with location validation
│       ├── locations.py     # Location management
│       └── search.py        # Search functionality
├── migrate_to_simple_location.py  # One-time migration script
├── cli/                     # CLI tool (Phase 5, planned)
├── ml/                      # AI/ML features (Phase 4, planned)
├── voice/                   # Voice interface (Phase 6, planned)
├── run.py                   # Application entry point
└── requirements.txt

frontend/
├── templates/
│   ├── base.html           # Base template with Alpine.js CDN
│   └── modules/            # Module-specific templates
└── static/
    ├── css/style.css       # Application styles
    └── js/main.js          # Additional JavaScript

docker-compose.yml          # Defines postgres, backend, nginx services
nginx.conf                  # Reverse proxy configuration
setup.sh                    # Automated setup script
```

### Flask Application Structure

- **App Factory Pattern**: `create_app()` in `backend/app/__init__.py`
- **Blueprints**: Each route module is a Flask Blueprint with URL prefix
  - `main` → `/`
  - `items` → `/items`
  - `modules` → `/modules`
  - `locations` → `/locations`
  - `search` → `/search`
- **Templates**: Located in `frontend/templates/`, use Jinja2 with Alpine.js
- **Static Files**: Served from `frontend/static/`

### Frontend Technology

- **Alpine.js**: Lightweight reactive framework (15KB) loaded via CDN
- **Progressive Enhancement**: HTML-first, JavaScript enhances
- **Key Features**:
  - Expandable modules/levels (no page reload)
  - Inline grid previews
  - Hover interactions with sticky sidebar
  - Animated transitions

## Key Implementation Details

### Location Validation

**Critical:** Locations can only hold ONE item. All item create/edit/move operations must check:

```python
# Check if location is already occupied
existing_item = Item.query.filter_by(location_id=location_id).first()
if existing_item:
    flash('Location is already occupied', 'error')
```

See `backend/app/routes/items.py`:
- `new_item()` (line 56-61)
- `edit_item()` (line 113-117)
- `move_item()` (line 160-163)

### Location Addressing

Locations use hierarchical addressing: `Module:Level:RowColumn`

Example: `"Zeus:3:B4"` = Zeus cabinet, Level 3, Row B, Column 4

Generated by `Location.full_address()` method in `backend/app/models.py:110-114`

### Database Relationships

```python
# models.py relationships
Module.levels → Level (cascade delete)
Level.locations → Location (cascade delete)
Location.items → Item (no cascade - items remain if location deleted)
Item.location → Location (nullable FK)
```

### API Endpoints

All routes have both HTML and JSON API endpoints:

**Items API:**
- `GET /items/api/items` - List items (with search/category filters)
- `GET /items/api/items/<id>` - Get single item

**Modules API:**
- `GET /modules/api/modules` - List all modules
- `GET /modules/api/modules/<id>` - Get module details
- `GET /modules/api/levels/<id>` - Get level with grid data

**Locations API:**
- `GET /locations/api/locations/<id>` - Get location details

### Services & Ports

- **nginx**: Port 8080 → http://localhost:8080 (main access point)
- **backend**: Port 5000 (internal, proxied by nginx)
- **postgres**: Port 5432 (exposed for direct access if needed)

## Development Guidelines

### Adding New Features

1. **Model Changes**: Edit `backend/app/models.py`, create migration
2. **Routes**: Add to appropriate blueprint in `backend/app/routes/`
3. **Templates**: Create/update in `frontend/templates/`
4. **Styles**: Update `frontend/static/css/style.css`
5. **JavaScript**: Use Alpine.js directives in templates or add to `frontend/static/js/main.js`

### Database Migrations

After changing models in `backend/app/models.py`:

```bash
docker-compose exec backend flask db migrate -m "Brief description"
# Review generated migration in backend/migrations/versions/
docker-compose exec backend flask db upgrade
```

### Code Style

- **Python**: PEP 8, type hints encouraged
- **SQL**: Use SQLAlchemy ORM, avoid raw SQL unless necessary
- **Templates**: Semantic HTML5, Alpine.js for reactivity
- **Commits**: Conventional commits format (feat:, fix:, docs:, refactor:)

### Testing Changes

1. Start services: `docker-compose up -d`
2. Check logs: `docker-compose logs -f backend`
3. Test in browser: http://localhost:8080
4. Test API: `curl http://localhost:5000/api/items`

## Important Notes

### Migration Script

`backend/migrate_to_simple_location.py` is a **one-time migration** from the old many-to-many schema to the simplified one-to-many schema. Only run if upgrading from pre-Phase-1 version.

### Planned Future Phases

- **Phase 2**: Smart location management (size validation, suggestions)
- **Phase 3**: Duplicate detection (fuzzy matching, NLP parsing)
- **Phase 4**: AI semantic search (sentence transformers, BERT)
- **Phase 5**: CLI interface (`invctl` command-line tool)
- **Phase 6**: Voice interface (wake word, speech-to-text)

See `CONTRIBUTING.md` for detailed roadmap.

### Environment Variables

Set in `.env` file (created from `.env.example` by `setup.sh`):

```bash
DATABASE_URL=postgresql://inventoryuser:inventorypass@postgres:5432/inventory
FLASK_ENV=development
SECRET_KEY=<random-secret-key>
```

### Common Issues

**PostgreSQL not ready:** Wait for health check to pass. Check with:
```bash
docker-compose logs postgres
```

**Backend not starting:** Check for Python errors in logs:
```bash
docker-compose logs backend
```

**Alpine.js not working:** Check browser console. Ensure CDN is accessible and no ad blockers are interfering.

**Migration conflicts:** If item was in multiple locations before Phase 1, only the first location is kept.

## Accessing Documentation

- `README.md` - User guide, features, troubleshooting
- `CONTRIBUTING.md` - Development roadmap, contribution guidelines
- `docs/DEPLOYMENT.md` - Production deployment guide
- `docs/PROJECT_STATUS.md` - Current implementation status
- `docs/START_HERE.md` - Quick start for new contributors
