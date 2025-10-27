# Contributing to Homelab Inventory System

Thank you for your interest in contributing! This document provides guidelines and information for developers.

## Development Roadmap

### ✅ Phase 1: Enhanced UI (Complete)
- Simplified data model (Item → Location)
- Alpine.js fluid navigation
- Expandable modules/levels
- Docker deployment

### 🚧 Phase 2: Smart Location Management (Next)
- Location type constraints
- Size/geometry validation
- Intelligent location suggestions
- Capacity indicators

### 📋 Phase 3: Duplicate Detection
- Natural language parsing
- Fuzzy matching for similar items
- Consolidation suggestions
- Specification extraction

### 🤖 Phase 4: AI Semantic Search
- Sentence transformer embeddings
- Natural language queries
- "Find long metric bolts" → ranked results
- BERT/MiniLM models

### 💻 Phase 5: CLI Interface
- `invctl` command-line tool
- Add/search/move items
- Batch operations
- Import/export capabilities

### 🎤 Phase 6: Voice Interface
- Wake word activation
- Speech-to-text (Vosk/Whisper)
- Natural language commands
- Text-to-speech feedback

## Project Structure

```
inventory-system/
├── backend/
│   ├── app/
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── __init__.py         # Flask app factory
│   │   ├── routes/             # API endpoints
│   │   └── ml/                 # AI/ML modules (Phase 4+)
│   ├── cli/                    # CLI implementation (Phase 5+)
│   ├── voice/                  # Voice interface (Phase 6+)
│   └── requirements.txt
├── frontend/
│   ├── templates/
│   └── static/
└── docker-compose.yml
```

## Development Setup

### Local Development (Without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Set up database (PostgreSQL required)
createdb inventory
export DATABASE_URL="postgresql://user:pass@localhost:5432/inventory"

# Run development server
python run.py
```

### Docker Development

```bash
# Build and start
docker-compose up --build

# View logs
docker-compose logs -f backend

# Shell into backend
docker-compose exec backend bash

# Database shell
docker-compose exec postgres psql -U inventoryuser inventory
```

## Code Style

### Python
- Follow PEP 8
- Use type hints where beneficial
- Document complex functions
- Keep functions focused and testable

### Frontend
- Semantic HTML5
- Alpine.js for interactivity
- Progressive enhancement
- Mobile-first responsive design

### Commits
- Use conventional commit format
- One feature/fix per commit
- Clear, descriptive messages
- Reference issues when applicable

Examples:
```
feat: Add AI semantic search with sentence transformers
fix: Prevent duplicate items in same location
docs: Update CLI usage examples
refactor: Simplify location validation logic
```

## Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### API Testing
```bash
# Test endpoints
curl http://localhost:5000/api/items
curl http://localhost:5000/api/modules
```

## Adding New Features

### 1. Data Model Changes

Edit `backend/app/models.py`:
```python
class Item(db.Model):
    # Add new field
    new_field = db.Column(db.String(100))
```

Create migration:
```bash
docker-compose exec backend flask db migrate -m "Add new_field to Item"
docker-compose exec backend flask db upgrade
```

### 2. API Endpoints

Create route in `backend/app/routes/`:
```python
from flask import Blueprint, jsonify, request

bp = Blueprint('feature', __name__, url_prefix='/api/feature')

@bp.route('/', methods=['GET'])
def get_feature():
    return jsonify({'status': 'ok'})
```

Register in `backend/app/__init__.py`:
```python
from app.routes import feature
app.register_blueprint(feature.bp)
```

### 3. Frontend Components

Add template in `frontend/templates/`:
```html
{% extends "base.html" %}

{% block content %}
<div x-data="{ show: false }">
    <!-- Your component -->
</div>
{% endblock %}
```

### 4. AI/ML Features (Phase 4+)

Add model in `backend/app/ml/`:
```python
from sentence_transformers import SentenceTransformer

class SemanticSearch:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def search(self, query):
        # Implementation
        pass
```

## Database Migrations

### Creating Migrations
```bash
# After model changes
docker-compose exec backend flask db migrate -m "Description"

# Review the migration file in backend/migrations/
# Edit if necessary

# Apply migration
docker-compose exec backend flask db upgrade
```

### Rolling Back
```bash
docker-compose exec backend flask db downgrade
```

## Performance Optimization

### Database
- Add indexes for frequently queried fields
- Use `select_related`/`joinedload` for relationships
- Implement pagination for large result sets

### Caching (Phase 4+)
```python
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'redis'})

@cache.cached(timeout=300)
def expensive_operation():
    # Your code
    pass
```

### AI/ML Optimization
- Cache embeddings in database
- Batch process items
- Use quantized models for edge devices

## Documentation

### Code Documentation
- Docstrings for all public functions
- Type hints for function signatures
- Comments for complex logic

### API Documentation
- Document all endpoints
- Include request/response examples
- Note authentication requirements

### User Documentation
- Update README.md for new features
- Create tutorials for complex workflows
- Include screenshots where helpful

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write/update tests
5. Update documentation
6. Commit your changes
7. Push to your fork
8. Open a Pull Request

### PR Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No breaking changes (or documented)

## Issue Reporting

### Bug Reports
Include:
- Expected behavior
- Actual behavior
- Steps to reproduce
- Environment (OS, Docker version, etc.)
- Logs/screenshots

### Feature Requests
Include:
- Use case description
- Proposed solution
- Alternative approaches considered
- Impact on existing features

## Questions?

- Check existing issues
- Review documentation
- Ask in discussions

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Happy coding!** 🚀
