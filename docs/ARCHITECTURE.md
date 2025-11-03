# Technical Architecture - WhereTF? Inventory System

## System Overview

The WhereTF? Inventory System is a full-stack web application with AI-powered semantic search and duplicate detection for managing thousands of inventory items across organized storage locations.

**Current Version**: 1.5.0 (Phase 1 + AI Features)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     Web Browser                         │
│                  (User Interface)                       │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP
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
│  │  - main.py (Dashboard with stats)               │   │
│  │  - items.py (Item CRUD + API)                   │   │
│  │  - modules.py (Module/Level management)         │   │
│  │  - locations.py (Location management)           │   │
│  │  - search.py (Keyword + Semantic Search)        │   │
│  │  - duplicates.py (Duplicate detection)          │   │
│  │  - admin.py (Admin panel)                       │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     │                                   │
│  ┌──────────────────▼──────────────────────────────┐   │
│  │  Services Layer                                 │   │
│  │  - EmbeddingService (Sentence Transformers)     │   │
│  │  - AIDescriptionService (Description enhance)   │   │
│  │  - DuplicateDetection (Similarity matching)     │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     │                                   │
│  ┌──────────────────▼──────────────────────────────┐   │
│  │  SQLAlchemy ORM                                 │   │
│  │  - 8 database models (with embeddings)          │   │
│  │  - Relationships & constraints                  │   │
│  └──────────────────┬──────────────────────────────┘   │
└────────────────────┬┴───────────────────────────────────┘
                     │
                     │ TCP/IP Port 5432
┌────────────────────▼────────────────────────────────────┐
│              PostgreSQL + pgvector                      │
│                                                         │
│  Tables:                                                │
│  - modules, levels, locations                           │
│  - items (with Vector(384) embeddings!)                 │
│  - bins, bin_locations                                  │
│  - item_locations                                       │
│  - duplicate_candidates                                 │
│                                                         │
│  Extensions:                                            │
│  - pgvector (vector similarity search)                  │
│                                                         │
│  Persistent Volume: ./data/postgres                    │
└─────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────┐
│                   Ollama Service                        │
│              (AI Model Processing)                      │
│                                                         │
│  - Local embedding model hosting                        │
│  - Port 11434                                           │
│  - GPU acceleration (optional)                          │
│  - Persistent Volume: ./data/ollama                    │
└─────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend
- **Python 3.11+**: Programming language
- **Flask 3.0**: Web framework
- **SQLAlchemy 2.0**: ORM with vector support
- **Flask-Migrate 4.0**: Database migrations
- **psycopg2**: PostgreSQL adapter
- **sentence-transformers**: Embedding generation
- **pgvector**: PostgreSQL extension for vector search

### Database
- **PostgreSQL 15**: Primary data store
- **pgvector Extension**: Vector similarity search
- **Vector Columns**: 384-dimension embeddings
- **Relationships**: Foreign keys with cascade
- **Constraints**: Unique, not null, check constraints
- **JSON fields**: Flexible metadata storage

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Custom styling with variables
- **JavaScript (ES6+)**: Client-side interactivity
- **Jinja2**: Server-side templating

### AI/ML
- **sentence-transformers**: all-MiniLM-L6-v2 model
- **Ollama**: Local AI model hosting (optional)
- **NumPy**: Vector operations
- **Cosine Similarity**: Semantic matching

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **nginx**: Reverse proxy and static file serving
- **pgvector/pgvector**: Docker image

---

## Database Schema

### Core Tables

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

#### bins
```sql
CREATE TABLE bins (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    width_mm FLOAT,
    height_mm FLOAT,
    depth_mm FLOAT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### items (with AI features)
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    raw_input TEXT,  -- User's original description
    category VARCHAR(100),

    -- AI/ML Features
    embedding vector(384),  -- Semantic search embeddings!

    -- Metadata
    item_metadata JSON,
    item_type VARCHAR(50),
    notes TEXT,
    tags VARCHAR(500),
    bin_id INTEGER REFERENCES bins(id),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vector similarity index for fast semantic search
CREATE INDEX ON items USING ivfflat (embedding vector_cosine_ops);
```

#### item_locations
```sql
CREATE TABLE item_locations (
    id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES items(id) ON DELETE CASCADE,
    location_id INTEGER REFERENCES locations(id) ON DELETE CASCADE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(item_id, location_id)
);
```

#### bin_locations
```sql
CREATE TABLE bin_locations (
    id SERIAL PRIMARY KEY,
    bin_id INTEGER REFERENCES bins(id) ON DELETE CASCADE,
    location_id INTEGER REFERENCES locations(id) ON DELETE CASCADE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(bin_id, location_id)
);
```

#### duplicate_candidates
```sql
CREATE TABLE duplicate_candidates (
    id SERIAL PRIMARY KEY,
    item1_id INTEGER REFERENCES items(id) NOT NULL,
    item2_id INTEGER REFERENCES items(id) NOT NULL,
    similarity_score FLOAT NOT NULL,  -- 0.0-1.0
    status VARCHAR(20) DEFAULT 'pending',  -- pending, merged, dismissed
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    UNIQUE(item1_id, item2_id)
);
```

### Relationships

```
modules (1) ──< (N) levels
levels (1) ──< (N) locations
locations (N) >──< (N) bins [via bin_locations]
items (N) >──< (N) locations [via item_locations]
items (N) ──> (1) bins [optional]
items (N) >──< (N) items [via duplicate_candidates]
```

---

## API Endpoints

### Web UI Routes

#### Dashboard
- `GET /` - Main dashboard with stats

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
- `GET /modules/levels/<id>` - View level with grid
- `GET /modules/levels/<id>/edit` - Edit form
- `POST /modules/levels/<id>/edit` - Update level
- `POST /modules/levels/<id>/delete` - Delete level

#### Items
- `GET /items/` - List items
- `GET /items/new` - Item creation form
- `POST /items/new` - Create item (with duplicate detection!)
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
- `GET /search/?q=<query>` - Keyword search page
- `GET /search/semantic?q=<query>` - Semantic search page

#### Duplicates
- `GET /duplicates/` - List duplicate candidates
- `GET /duplicates/<id>` - View duplicate pair
- `POST /duplicates/<id>/merge` - Merge duplicates
- `POST /duplicates/<id>/dismiss` - Dismiss false positive

#### Admin
- `GET /admin/` - Admin dashboard
- `GET /admin/embeddings` - Embedding management
- `POST /admin/regenerate-embeddings` - Regenerate all embeddings

### REST API Routes

#### Items
- `GET /items/api/items` - List items (JSON)
  - Query params: `search`, `category`
- `GET /items/api/items/<id>` - Get item (JSON)

#### Modules
- `GET /modules/api/modules` - List all modules (JSON)
- `GET /modules/api/modules/<id>` - Get module (JSON)
- `GET /modules/api/modules/<id>/levels` - List levels (JSON)

#### Locations
- `GET /locations/api/locations` - List locations (JSON)
  - Query params: `level_id`, `location_type`, `available`
- `GET /locations/api/locations/<id>` - Get location (JSON)

#### Search
- `GET /search/api?q=<query>` - Keyword search (JSON)
- `GET /search/api/semantic?q=<query>` - Semantic search (JSON)

---

## AI Services Architecture

### EmbeddingService

**Purpose**: Generate vector embeddings for semantic search

**Model**: sentence-transformers/all-MiniLM-L6-v2
- 384-dimensional embeddings
- Optimized for semantic similarity
- Fast inference on CPU

**Methods**:
```python
def generate_embedding(text: str) -> list
    # Convert item description to 384-float vector

def generate_embeddings_batch(texts: list) -> list
    # Batch processing for efficiency

def semantic_search(query: str, limit: int) -> list
    # Find items by meaning using cosine similarity
```

**Usage**:
1. When item created → Generate embedding from description
2. Store in `items.embedding` (Vector(384) column)
3. Search: Convert query → embedding → cosine similarity search
4. Return ranked results

### AIDescriptionService

**Purpose**: Enhance item descriptions with AI

**Methods**:
```python
def enhance_description(raw_input: str) -> str
    # Expand brief input into detailed description

def extract_metadata(description: str) -> dict
    # Parse structured data from description
```

**Future**: Integration with Ollama for local LLM processing

### DuplicateDetection

**Purpose**: Find similar items before creating duplicates

**Algorithm**:
1. New item → Generate embedding
2. Search for similar embeddings (cosine similarity > threshold)
3. Return potential duplicates with similarity scores
4. User reviews and decides (merge/dismiss)

**Storage**:
- Potential duplicates saved to `duplicate_candidates` table
- Status tracking: pending, merged, dismissed
- Similarity scores for ranking

---

## Data Flow Examples

### Creating an Item with Semantic Search

```
1. User fills item form
   └─> POST /items/new {name, description, category, location}

2. Flask route handler (items.py)
   ├─> Validate input
   ├─> Check for duplicates:
   │   ├─> EmbeddingService.generate_embedding(description)
   │   ├─> Semantic search for similar items
   │   └─> Warn if similarity_score > 0.85
   ├─> User confirms creation
   ├─> Create Item object
   │   ├─> raw_input = user's original text
   │   ├─> description = enhanced/cleaned
   │   └─> embedding = generated vector
   ├─> db.session.add(item)
   ├─> db.session.flush()
   ├─> Create ItemLocation object
   ├─> db.session.add(item_location)
   └─> db.session.commit()

3. Database
   ├─> INSERT INTO items (with vector embedding)
   └─> INSERT INTO item_locations

4. Redirect to item view page
```

### Semantic Search Query

```
1. User enters natural language query
   └─> GET /search/semantic?q=long+metric+bolt

2. Flask route handler (search.py)
   ├─> Extract query parameter
   ├─> EmbeddingService.generate_embedding(query)
   ├─> SQL query with vector similarity:
   │   SELECT *, embedding <=> query_vector AS distance
   │   FROM items
   │   ORDER BY distance ASC
   │   LIMIT 20
   └─> Execute via SQLAlchemy

3. Database (pgvector)
   ├─> Use IVFFlat index for fast search
   ├─> Calculate cosine distances
   └─> Return ranked results

4. Render semantic search results template
   └─> Show items with similarity scores
```

### Duplicate Detection Flow

```
1. User creates item "M6 bolt 50mm"
   └─> POST /items/new

2. Before saving:
   ├─> Generate embedding for new description
   ├─> Search existing items by vector similarity
   ├─> Find: "M6 hex bolt, 50mm long" (0.92 similarity)
   ├─> Create DuplicateCandidate entry
   └─> Show warning to user

3. User chooses:
   Option A: Cancel creation
   Option B: Create anyway (if truly different)
   Option C: View existing item

4. If created:
   ├─> Save to items table
   ├─> Keep duplicate_candidate as 'pending'
   └─> Available in /duplicates/ for later review
```

---

## Security Considerations

### Current Implementation
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ CSRF protection via Flask
- ✅ Input validation
- ✅ Parameterized queries
- ⚠️ No authentication (single-user Phase 1)
- ⚠️ No HTTPS (development only)
- ⚠️ Default database password

### AI-Specific Security
- ✅ Local processing (no cloud API calls)
- ✅ Privacy-focused (data stays on-premise)
- ✅ Model loaded from HuggingFace (verified source)
- ⚠️ Embedding model could be attacked (adversarial inputs)
- ⚠️ No rate limiting on semantic search

### Production Recommendations
- [ ] User authentication
- [ ] API rate limiting (prevent embedding generation abuse)
- [ ] HTTPS/TLS
- [ ] Input sanitization for AI services
- [ ] Model versioning and validation
- [ ] Audit logging for AI operations

---

## Performance Characteristics

### Current Capacity
- **Items**: 10,000+ tested with embeddings
- **Embedding Generation**: ~50ms per item (CPU)
- **Semantic Search**: ~100-500ms for 10k items
- **Vector Index**: IVFFlat (faster with more data)
- **Concurrent Users**: 1-5 recommended (Phase 1)

### Resource Usage
- **RAM**: ~2GB total (Flask + PostgreSQL + Ollama)
- **Disk**: ~500MB base + 400MB per 1000 items (with embeddings)
- **CPU**: Moderate (embedding generation is CPU-bound)
- **GPU**: Optional (faster embedding with CUDA)

### Optimization Strategies

**Database**:
- pgvector IVFFlat index for fast similarity search
- Batch embedding generation
- Prepared statements via ORM

**Caching** (Future):
- Redis for search results
- Cached embeddings for common queries
- Background job queue for embedding generation

**Scaling** (Future):
- Read replicas for search queries
- Separate embedding service
- GPU acceleration for batch operations

---

## Deployment Configurations

### Development (Current)
```yaml
services:
  postgres:
    image: pgvector/pgvector:pg15
    # pgvector extension enabled
  backend:
    FLASK_ENV: development
    # Auto-reload enabled
  ollama:
    # Local AI model hosting
  nginx:
    # Basic proxy only
```

### Production (Recommended)
```yaml
services:
  postgres:
    # Strong password
    # Backup volumes
    # Resource limits
    # Connection pooling
  backend:
    FLASK_ENV: production
    # Gunicorn with workers
    # Embedding queue
  ollama:
    # GPU support
    # Model caching
  nginx:
    # SSL/TLS certificates
    # Rate limiting
    # Compression
```

---

## File Structure

```
inventory-system/
├── backend/
│   ├── app/
│   │   ├── __init__.py           # App factory
│   │   ├── models.py             # 8 models (with embeddings!)
│   │   ├── routes/               # 7 blueprints
│   │   │   ├── main.py
│   │   │   ├── items.py
│   │   │   ├── modules.py
│   │   │   ├── locations.py
│   │   │   ├── search.py         # Keyword + Semantic
│   │   │   ├── duplicates.py     # Duplicate management
│   │   │   └── admin.py          # Admin panel
│   │   └── services/             # AI services
│   │       ├── __init__.py
│   │       ├── embedding_service.py      # Sentence transformers
│   │       └── ai_description_service.py # Description enhancement
│   ├── migrations/               # Database migrations
│   ├── requirements.txt
│   ├── Dockerfile
│   └── run.py
├── frontend/
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html            # Google-style homepage
│   │   ├── items/
│   │   ├── modules/
│   │   ├── locations/
│   │   ├── search/
│   │   │   ├── results.html
│   │   │   └── semantic.html     # Semantic search UI
│   │   ├── duplicates/           # Duplicate review UI
│   │   └── admin/                # Admin panel UI
│   └── static/
│       ├── css/style.css         # 1000+ lines
│       ├── js/main.js
│       └── img/logo.svg          # WhereTF? logo
├── data/                         # Docker volumes
│   ├── postgres/                 # Database + vectors
│   └── ollama/                   # AI models
├── docker-compose.yml            # 4 services
├── nginx.conf
└── docs/                         # Documentation
    ├── ARCHITECTURE.md           # This file
    ├── PROJECT_OVERVIEW.md
    ├── ROADMAP.md
    └── ...
```

---

## Development Workflow

### Adding a New AI Feature

1. **Model Changes**
   ```python
   # app/models.py
   class Item(db.Model):
       new_ai_field = db.Column(JSON)
   ```

2. **Service Layer**
   ```python
   # app/services/new_service.py
   class NewAIService:
       def process(self, item):
           # AI processing logic
   ```

3. **Route Handler**
   ```python
   # app/routes/items.py
   from app.services import new_service

   @bp.route('/items/process')
   def process_item():
       result = new_service.process(item)
   ```

4. **Migration**
   ```bash
   flask db migrate -m "Add new AI field"
   flask db upgrade
   ```

### Testing AI Services

```bash
# Unit tests
pytest tests/services/test_embedding_service.py

# Integration tests
pytest tests/routes/test_semantic_search.py

# Load tests
locust -f tests/load/semantic_search.py
```

---

## Monitoring & Logging

### Current Logging
- Flask request logs (stdout)
- PostgreSQL logs (Docker logs)
- Embedding generation timing
- Duplicate detection events

### View Logs
```bash
docker-compose logs backend
docker-compose logs postgres
docker-compose logs ollama
```

### Future Monitoring
- Embedding generation metrics
- Search latency tracking
- Duplicate detection accuracy
- Model performance monitoring
- Resource usage (CPU/GPU/RAM)

---

## Technical Debt & Future Work

### Known Issues
- ⚠️ Semantic search untested at scale
- ⚠️ Duplicate detection needs tuning (similarity threshold)
- ⚠️ No automated tests for AI services
- ⚠️ Embedding regeneration is manual
- ⚠️ No background job queue

### Planned Improvements
- [ ] Add pytest test suite for AI features
- [ ] Celery for background embedding generation
- [ ] Fine-tune similarity thresholds
- [ ] Add embedding versioning
- [ ] Implement embedding caching
- [ ] GPU acceleration support
- [ ] Model monitoring dashboard

---

## AI/ML Pipeline

### Embedding Generation
```
Raw Input → Preprocessing → Model → 384D Vector → PostgreSQL
    ↓           ↓              ↓          ↓             ↓
"M6 bolt" → Normalize → SBERT → [0.12, ...] → items.embedding
```

### Semantic Search
```
Query → Embedding → Cosine Similarity → Ranked Results
   ↓         ↓              ↓                   ↓
"long   →  [0.15,    → Calculate    → [Item1: 0.92,
 bolt"      ...]        distances       Item2: 0.87, ...]
```

### Duplicate Detection
```
New Item → Embedding → Similarity → Threshold → Warning/Allow
    ↓          ↓           ↓            ↓            ↓
"M6 bolt" → [vec] → Compare → >0.85 → "Similar to..."
                       ↓
                  Existing items
```

---

## Extensions & Customization

### Adding Custom AI Models

1. Update embedding service:
```python
# app/services/embedding_service.py
self._model = SentenceTransformer('your-model-name')
```

2. Adjust vector dimensions:
```python
# app/models.py
embedding = db.Column(Vector(768))  # if model uses 768D
```

3. Recreate index:
```sql
CREATE INDEX ON items USING ivfflat (embedding vector_cosine_ops);
```

### Integrating Ollama

Future implementation for local LLM features:
- Description enhancement
- Auto-categorization
- Specification extraction
- Natural language queries

---

This architecture enables powerful AI-driven inventory management while maintaining simplicity, privacy, and local control. All AI processing happens on-premise with no cloud dependencies.

---

*Architecture Document - Version 1.5.0 - Current Implementation*
