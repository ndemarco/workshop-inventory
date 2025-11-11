# Technical Architecture - Phase 1

## System Overview

The Homelab Inventory System is a full-stack web application designed for managing thousands of inventory items across organized storage locations.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     Web Browser                         │
│                  (User Interface)                       │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/HTTPS
                     │ Port 8080
┌────────────────────▼────────────────────────────────────┐
│                   NGINX                                 │
│              (Reverse Proxy)                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Proxy Pass
                     │ Port 5000
┌────────────────────▼────────────────────────────────────┐
│                Flask Application                        │
│              (Python Backend)                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Routes Layer                                   │   │
│  │  - main.py (Dashboard)                          │   │
│  │  - items.py (Item CRUD)                         │   │
│  │  - modules.py (Storage CRUD)                    │   │
│  │  - locations.py (Location management)           │   │
│  │  - search.py (Search functionality)             │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     │                                   │
│  ┌──────────────────▼──────────────────────────────┐   │
│  │  SQLAlchemy ORM                                 │   │
│  │  - models.py (Database models)                  │   │
│  │  - Relationships & constraints                  │   │
│  └──────────────────┬──────────────────────────────┘   │
└────────────────────┬┴───────────────────────────────────┘
                     │
                     │ TCP/IP
                     │ Port 5432
┌────────────────────▼────────────────────────────────────┐
│              PostgreSQL Database                        │
│                                                         │
│  Tables:                                                │
│  - modules                                              │
│  - levels                                               │
│  - locations                                            │
│  - items                                                │
│  - item_locations (junction table)                     │
│                                                         │
│  Persistent Volume: ./data/postgres                    │
└─────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Custom styling with CSS variables
- **JavaScript (ES6+)**: Client-side interactivity
- **Jinja2**: Server-side templating

### Backend
- **Python 3.11+**: Programming language
- **Flask 3.0**: Web framework
- **SQLAlchemy 2.0**: ORM
- **Flask-Migrate 4.0**: Database migrations
- **psycopg2**: PostgreSQL adapter

### Database
- **PostgreSQL 15**: Primary data store
- **Relations**: Foreign keys with cascade
- **Constraints**: Unique, not null, check constraints
- **JSON fields**: For flexible metadata storage

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **nginx**: Reverse proxy and static file serving
- **Ubuntu 24**: Base OS for containers

## Database Schema

### Tables

#### modules
```sql
CREATE TABLE modules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    location_description VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### levels
```sql
CREATE TABLE levels (
    id SERIAL PRIMARY KEY,
    module_id INTEGER REFERENCES modules(id) ON DELETE CASCADE,
    level_number INTEGER NOT NULL,
    name VARCHAR(100),
    rows INTEGER DEFAULT 1,
    columns INTEGER DEFAULT 1,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(module_id, level_number)
);
```

#### locations
```sql
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    level_id INTEGER REFERENCES levels(id) ON DELETE CASCADE,
    row VARCHAR(10) NOT NULL,
    column VARCHAR(10) NOT NULL,
    location_type VARCHAR(50) DEFAULT 'general',
    width_mm FLOAT,
    height_mm FLOAT,
    depth_mm FLOAT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(level_id, row, column)
);
```

#### items
```sql
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100),
    metadata JSON,
    quantity INTEGER DEFAULT 1,
    unit VARCHAR(20),
    min_quantity INTEGER,
    item_type VARCHAR(50),
    notes TEXT,
    tags VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### item_locations
```sql
CREATE TABLE item_locations (
    id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES items(id) ON DELETE CASCADE,
    location_id INTEGER REFERENCES locations(id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 1,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(item_id, location_id)
);
```

### Relationships

```
modules (1) ──< (N) levels
levels (1) ──< (N) locations
items (N) >──< (N) locations  [via item_locations]
```

## API Endpoints

### Web UI Routes

#### Dashboard
- `GET /` - Main dashboard

#### Modules
- `GET /modules/` - List modules
- `GET /modules/new` - Module creation form
- `POST /modules/new` - Create module
- `GET /modules/<id>` - View module
- `GET /modules/<id>/edit` - Edit form
- `POST /modules/<id>/edit` - Update module
- `POST /modules/<id>/delete` - Delete module

#### Levels
- `GET /modules/<id>/levels/new` - Level creation form
- `POST /modules/<id>/levels/new` - Create level
- `GET /modules/levels/<id>` - View level
- `GET /modules/levels/<id>/edit` - Edit form
- `POST /modules/levels/<id>/edit` - Update level
- `POST /modules/levels/<id>/delete` - Delete level

#### Items
- `GET /items/` - List items
- `GET /items/new` - Item creation form
- `POST /items/new` - Create item
- `GET /items/<id>` - View item
- `GET /items/<id>/edit` - Edit form
- `POST /items/<id>/edit` - Update item
- `POST /items/<id>/delete` - Delete item
- `POST /items/<id>/locations/add` - Add location
- `POST /items/<id>/locations/<il_id>/remove` - Remove location

#### Locations
- `GET /locations/` - List locations (with filters)
- `GET /locations/<id>` - View location
- `GET /locations/<id>/edit` - Edit form
- `POST /locations/<id>/edit` - Update location

#### Search
- `GET /search/?q=<query>` - Search page

### REST API Routes

#### Modules
- `GET /modules/api/modules` - List all modules (JSON)
- `GET /modules/api/modules/<id>` - Get module (JSON)
- `GET /modules/api/modules/<id>/levels` - List levels (JSON)

#### Locations
- `GET /locations/api/locations` - List locations (JSON)
  - Query params: `level_id`, `location_type`, `available`
- `GET /locations/api/locations/<id>` - Get location (JSON)

#### Items
- `GET /items/api/items` - List items (JSON)
  - Query params: `search`, `category`
- `GET /items/api/items/<id>` - Get item (JSON)

#### Search
- `GET /search/api?q=<query>` - Search items (JSON)

## Data Flow

### Creating an Item with Location

```
1. User fills form
   └─> POST /items/new

2. Flask route handler (items.py)
   ├─> Validate input
   ├─> Create Item object
   ├─> db.session.add(item)
   ├─> db.session.flush()  # Get item.id
   ├─> Create ItemLocation object
   ├─> db.session.add(item_location)
   └─> db.session.commit()

3. Database
   ├─> INSERT INTO items
   └─> INSERT INTO item_locations

4. Redirect to item view page
```

### Searching for Items

```
1. User enters search query
   └─> GET /search/?q=M6+bolt

2. Flask route handler (search.py)
   ├─> Extract query parameter
   ├─> Build SQL ILIKE query
   │   WHERE name ILIKE '%M6%bolt%'
   │   OR description ILIKE '%M6%bolt%'
   │   OR tags ILIKE '%M6%bolt%'
   └─> Execute query via SQLAlchemy

3. Database
   └─> Return matching rows

4. Render results template
   └─> Show items with locations
```

### Viewing Location Grid

```
1. User clicks level
   └─> GET /modules/levels/<id>

2. Flask route handler (modules.py)
   ├─> Query level by ID
   ├─> Query all locations for level
   ├─> Organize into grid structure
   │   grid[row][column] = location
   └─> Pass to template

3. Template (levels/view.html)
   ├─> Iterate rows
   ├─> Iterate columns
   ├─> Render table cell
   │   ├─> Show location address
   │   ├─> Show item count
   │   └─> Apply CSS class (occupied/empty)
   └─> Generate interactive grid

4. Browser
   └─> Render visual grid with colors
```

## Security Considerations

### Phase 1 (Current)
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ CSRF protection via Flask
- ✅ Input validation
- ⚠️ No authentication (single-user)
- ⚠️ No HTTPS (development only)
- ⚠️ Default database password

### Future Phases
- 🔜 User authentication
- 🔜 Role-based access control
- 🔜 HTTPS/TLS
- 🔜 Session management
- 🔜 API rate limiting
- 🔜 Audit logging

## Performance Characteristics

### Current (Phase 1)
- **Database**: Single PostgreSQL instance
- **Queries**: Non-optimized, works well up to ~10k items
- **Indexing**: Primary keys only
- **Caching**: None
- **Concurrent users**: 1-5 recommended

### Future Optimizations
- Database indexing on frequently queried fields
- Query optimization with eager loading
- Redis caching layer
- Connection pooling
- CDN for static assets

## Deployment Configurations

### Development
```yaml
services:
  postgres:
    # Development with data persistence
  backend:
    FLASK_ENV: development
    # Auto-reload enabled
  nginx:
    # Basic proxy only
```

### Production (Recommended Changes)
```yaml
services:
  postgres:
    # Strong password
    # Backup volumes
    # Resource limits
  backend:
    FLASK_ENV: production
    # Gunicorn/uWSGI
    # Multiple workers
  nginx:
    # SSL/TLS certificates
    # Gzip compression
    # Rate limiting
```

## Monitoring & Logging

### Current Logging
- Flask request logs (stdout)
- PostgreSQL logs (Docker logs)
- nginx access logs (Docker logs)

### View Logs
```bash
docker-compose logs backend
docker-compose logs postgres
docker-compose logs nginx
```

### Future Monitoring
- Application performance monitoring (APM)
- Error tracking (Sentry)
- Metrics (Prometheus)
- Dashboards (Grafana)

## Scalability Path

### Current Limits
- Single server deployment
- ~10,000 items perform well
- ~1,000 locations per level max
- Single database instance

### Future Scaling
**Horizontal:**
- Load balancer → Multiple Flask instances
- Read replicas for PostgreSQL
- Redis for session storage

**Vertical:**
- More RAM for larger datasets
- SSD for database performance
- CPU for concurrent users

## Extensibility Points

### Adding Features
1. **New routes**: Add to `app/routes/`
2. **New models**: Extend `app/models.py`
3. **New templates**: Add to `frontend/templates/`
4. **New API endpoints**: Follow existing pattern

### Plugin Architecture (Future)
- Custom location types
- Custom item attributes
- Export formats
- Integration hooks

## Development Workflow

### Adding a New Feature

1. **Model changes**
   ```python
   # app/models.py
   class NewTable(db.Model):
       # Define schema
   ```

2. **Route handler**
   ```python
   # app/routes/new_feature.py
   @bp.route('/new')
   def new_feature():
       # Logic here
   ```

3. **Template**
   ```html
   <!-- frontend/templates/new_feature.html -->
   {% extends "base.html" %}
   ```

4. **Register blueprint**
   ```python
   # app/__init__.py
   app.register_blueprint(new_feature.bp)
   ```

### Testing Changes
```bash
docker-compose restart backend
docker-compose logs -f backend
```

## Migration Path to Phase 2+

### Phase 2 Additions
- Location suggestion service
- Size/type constraint checking
- Visual location picker

### Phase 3 Additions
- Duplicate detection service
- Fuzzy matching algorithm
- Similarity scoring

### Phase 4 Additions
- Sentence transformer model
- Embedding generation service
- Vector similarity search
- pgvector extension

### Phase 5 Additions
- CLI tool (`invctl`)
- Batch operations
- CSV import/export

### Phase 6 Additions
- Voice service (Whisper/Vosk)
- Wake word detection (Porcupine)
- TTS service
- Audio interface

## Technical Debt

### Known Issues
- No database migrations setup (add Flask-Migrate migrations)
- No automated tests
- No CI/CD pipeline
- Limited error handling
- No rate limiting

### Future Improvements
- Add pytest test suite
- Set up GitHub Actions
- Improve error messages
- Add request validation with marshmallow
- Implement caching strategy

## Dependencies

### Python Packages
```
Flask==3.0.0              # Web framework
Flask-SQLAlchemy==3.1.1   # ORM
Flask-Migrate==4.0.5      # Migrations
psycopg2-binary==2.9.9    # PostgreSQL driver
python-dotenv==1.0.0      # Environment variables
sqlalchemy==2.0.23        # Database toolkit
```

### System Requirements
- Python 3.11+
- PostgreSQL 15+
- Docker 20.10+
- Docker Compose 2.0+

## Configuration Files

### docker-compose.yml
Defines all services and their relationships

### nginx.conf
Reverse proxy configuration

### .env
Environment variables (DATABASE_URL, SECRET_KEY, etc.)

## File Structure
```
inventory-system/
├── backend/
│   ├── app/
│   │   ├── __init__.py      # App factory
│   │   ├── models.py        # Database models
│   │   ├── routes/          # Route handlers
│   │   │   ├── main.py
│   │   │   ├── items.py
│   │   │   ├── modules.py
│   │   │   ├── locations.py
│   │   │   └── search.py
│   │   └── services/        # Business logic (future)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── run.py
├── frontend/
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   └── [feature]/
│   └── static/
│       ├── css/style.css
│       └── js/main.js
├── data/                    # Docker volumes
│   └── postgres/
├── docker-compose.yml
├── nginx.conf
└── README.md
```

---

This architecture is designed to be:
- **Modular**: Easy to add features
- **Maintainable**: Clear separation of concerns
- **Scalable**: Can grow with your needs
- **Extensible**: Plugin-friendly design
