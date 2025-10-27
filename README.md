# 🏠 Homelab Inventory System - Enhanced UI

**Phase 1 with Fluid Navigation & Simplified Data Model**

## 🎯 What's New

This enhanced version features a **completely redesigned interface** with:

### ✨ Key Improvements

1. **Simplified Data Model** 
   - Changed from many-to-many to simple one-to-many relationship
   - Each location can store **exactly one item**
   - Cleaner queries, better performance
   - Easier to understand and maintain

2. **Fluid Navigation Interface**
   - **Expandable modules** - Click to expand inline
   - **Expandable levels** - See grid previews without page loads
   - **Inline grids** - Browse locations without navigating away
   - **Hover for details** - See item info on hover
   - **Sticky sidebar** - Item details panel

3. **Alpine.js Integration**
   - Lightweight reactive UI (15KB)
   - No build process needed
   - Progressive enhancement
   - Fast, smooth animations

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- 2GB RAM
- 10GB disk space

### Deploy

```bash
cd inventory-system
docker-compose up -d
```

Wait 30 seconds, then open: **http://localhost:8080**

### For Existing Installations

If upgrading from the old schema:

```bash
# 1. Backup your database first!
docker-compose exec postgres pg_dump -U inventoryuser inventory > backup.sql

# 2. Stop containers
docker-compose down

# 3. Pull/update code

# 4. Start containers
docker-compose up -d

# 5. Run migration
docker-compose exec backend python migrate_to_simple_location.py
```

The migration script will:
- Add `location_id`, `quantity`, `unit` columns to items
- Migrate data from `item_locations` table
- Keep the first location for items with multiple locations
- Drop the old `item_locations` table

## 📖 User Guide

### Browsing Storage

1. **Navigate to Modules** page
2. **Click a module name** to expand it inline
3. **Click a level** to see the grid preview
4. **Hover over occupied cells** to see item details in the sidebar
5. **Click a cell** to go to the item details page

### Module → Level → Grid Flow

```
┌─────────────────────────────────────────────┐
│ ▼ Zeus (Electronics Cabinet)               │
│   ├─ ▼ Level 1: Top Drawer (4×6)          │
│   │   [Grid shows: Item names visible]     │
│   │   │ A1: M6 Bolts │ A2: Resistors │... │
│   ├─ ▶ Level 2: Middle Drawer (3×4)       │
│   └─ ▶ Level 3: Bottom Drawer (2×3)       │
└─────────────────────────────────────────────┘
```

### Adding Items

Items now require:
- **Name** (required)
- **Description** (required)
- **Location** (optional, but one location max)
- **Quantity** (how many at this location)
- **Unit** (pieces, grams, etc.)

When adding an item, the system will:
- ✅ Check if the location is available
- ❌ Prevent adding if location is occupied
- 💡 Suggest you move the existing item first

### Moving Items

To move an item to a different location:
1. Edit the item
2. Change the location dropdown
3. System checks if new location is available
4. Save - item is moved

## 🛠️ Technical Changes

### Data Model Simplification

**Before (Many-to-Many):**
```python
Item ──< ItemLocation >── Location
```

**After (One-to-Many):**
```python
Item ──> Location (via location_id FK)
```

### Benefits
- Simpler queries: `Item.query.filter_by(location_id=123)`
- Clearer semantics: "Where is this item?"
- Better performance: No join table
- Easier validation: One location per item

### API Changes

**Items API:**
```javascript
// GET /items/api/items/<id>
{
  "id": 1,
  "name": "M6 Bolts",
  "description": "...",
  "location_id": 42,      // Direct FK
  "location": {           // Nested object
    "id": 42,
    "full_address": "Zeus:1:A3"
  },
  "quantity": 100,        // Now on item
  "unit": "pieces"        // Now on item
}
```

**Locations API:**
```javascript
// GET /locations/api/locations/<id>
{
  "id": 42,
  "full_address": "Zeus:1:A3",
  "item_count": 1,        // Always 0 or 1
  "item": {               // The single item (if any)
    "id": 1,
    "name": "M6 Bolts",
    "description": "..."
  }
}
```

### New Routes

- `POST /items/<id>/move` - Move item to different location
- Validation on all item create/edit to prevent conflicts

## 💡 Design Decisions

### Why One Item Per Location?

1. **Simplifies mental model** - Each bin has one thing
2. **Easier physical organization** - No mixed bins
3. **Better for voice interface** - "Put X in location Y"
4. **Clearer inventory** - No quantity splitting confusion

### Why Alpine.js?

1. **Lightweight** - Only 15KB, no build process
2. **Declarative** - HTML-first, like the rest of the app
3. **Progressive** - Enhances existing templates
4. **Voice-interface ready** - Keeps backend simple

### Future Voice Interface

The simplified data model makes voice commands clearer:

```
"Add M6 bolts to Zeus level 1 location A3"
→ Simple: Set item.location_id = location_id of Zeus:1:A3

"Move the bolts from A3 to B2"
→ Simple: Update item.location_id = location_id of B2
```

## 📦 Project Structure

```
inventory-system/
├── backend/
│   ├── app/
│   │   ├── __init__.py              # Flask app factory
│   │   ├── models.py                # Simplified models
│   │   └── routes/                  # All route handlers
│   │       ├── items.py             # Item CRUD + validation
│   │       ├── locations.py         # Location management
│   │       ├── modules.py           # Module/level CRUD
│   │       ├── search.py            # Search functionality
│   │       └── main.py              # Dashboard
│   ├── migrate_to_simple_location.py # Migration script
│   ├── requirements.txt
│   ├── Dockerfile
│   └── run.py
├── frontend/
│   ├── templates/
│   │   ├── base.html               # With Alpine.js
│   │   └── modules/
│   │       └── list.html           # Enhanced with expandables
│   └── static/
│       ├── css/
│       │   └── style.css           # Enhanced styles
│       └── js/
│           └── main.js
├── docker-compose.yml
├── nginx.conf
└── README.md
```

## 🎨 UI Features

### Expandable Modules
- Click module header to expand/collapse
- Shows all levels inline
- Animated transitions

### Inline Grid Preview
- Each level shows its grid when expanded
- Item names visible in occupied cells
- Color-coded (occupied/empty)

### Hover Interactions
- Hover over occupied cell → Sidebar shows details
- Smooth animations
- Click cell → Go to item page

### Sidebar Panel
- Sticky positioning
- Shows selected item details
- Quick actions (View, Edit)
- Auto-hides when not needed

## 🔧 Configuration

### Environment Variables

Create `.env` from `.env.example`:

```bash
cp .env.example .env
```

Edit as needed:
```env
DATABASE_URL=postgresql://user:pass@postgres:5432/inventory
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

### Changing Ports

Edit `docker-compose.yml`:
```yaml
nginx:
  ports:
    - "8080:80"  # Change 8080 to your preferred port
```

## 🐛 Troubleshooting

### Migration Issues

If migration fails:

```bash
# Check what went wrong
docker-compose logs backend

# Reset database (DESTROYS DATA!)
docker-compose down -v
docker-compose up -d
# Start fresh
```

### Multiple Items Per Location (Old Data)

If you had items in multiple locations before:
- Migration keeps the FIRST location only
- Check logs for skipped locations
- Manually re-add items if needed

### Alpine.js Not Working

Check browser console for errors. Ensure:
- Internet connection (for CDN)
- No ad blockers blocking CDN
- Modern browser (Chrome/Firefox/Safari/Edge latest)

## 📝 Development

### Running Without Docker

```bash
# Install PostgreSQL locally
# Create database 'inventory'

cd backend
pip install -r requirements.txt

export DATABASE_URL="postgresql://user:pass@localhost:5432/inventory"
python run.py
```

Access at http://localhost:5000

### Adding New Features

1. Update `models.py` if schema changes
2. Create/update routes in `app/routes/`
3. Create/update templates in `frontend/templates/`
4. Update CSS in `frontend/static/css/style.css`
5. Use Alpine.js for interactivity

## 🔮 Roadmap

### Phase 2: Enhanced Location Features
- Location suggestions based on item type
- Size/compatibility constraints
- Visual location capacity indicators

### Phase 3: Duplicate Detection
- Warn when adding similar items
- Parse specifications automatically
- Suggest consolidation

### Phase 4: AI Semantic Search
- Natural language queries
- "Find long metric bolts" → ranked results
- BERT/Transformer models

### Phase 5: CLI Interface
- `invctl add "M6 bolt" --location Zeus:1:A3`
- Batch operations
- Import/export

### Phase 6: Voice Interface
- Wake word activation
- "Add bolts to Zeus level 1 A3"
- Hands-free workshop operation

## 🎯 Success Criteria

You'll know it's working when:
- ✅ Modules expand/collapse smoothly
- ✅ Grids show inline without page loads
- ✅ Hover shows item details in sidebar
- ✅ No items in multiple locations
- ✅ Moving items validates availability

## 💾 Backup

### Quick Backup
```bash
docker-compose exec postgres pg_dump -U inventoryuser inventory > backup_$(date +%Y%m%d).sql
```

### Restore
```bash
docker-compose exec -T postgres psql -U inventoryuser inventory < backup_20241027.sql
```

## 📜 License

[Your License Here]

## 🙏 Credits

- **Flask** - Web framework
- **PostgreSQL** - Database
- **Alpine.js** - Reactive UI
- **Docker** - Containerization

---

**Version:** 1.1.0 (Enhanced UI)  
**Last Updated:** October 2024

**Previous Version:** 1.0.0 (Phase 1 Foundation)  
**Migration Required:** Yes (run `migrate_to_simple_location.py`)
