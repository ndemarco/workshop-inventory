# UI Redesign Roadmap: Module-Centric Dashboard

## Overview

This roadmap outlines the transformation of the dashboard from a recent-items-focused layout to a module-centric, search-first interface that prioritizes visual navigation and rapid item discovery.

**Target User Flow:**
1. User lands on dashboard → sees all modules in a grid
2. User scans modules visually → each shows occupancy statistics
3. User searches for item → sees results with location breadcrumbs
4. User hovers over result → corresponding module/level highlights
5. User clicks result → drills into location detail with item information

---

## Phase 1: Backend Enhancements

**Goal:** Add API endpoints and data aggregation for the new UI requirements

### Task 1.1: Enhanced Statistics API
**File:** `backend/app/routes/main.py`

Add comprehensive statistics calculation for dashboard:

```python
@bp.route('/api/dashboard/stats')
def dashboard_stats():
    """
    Returns:
    - Total modules, levels, locations
    - Overall occupancy (occupied/total locations)
    - Per-module statistics (occupied/free locations)
    - Per-level statistics within each module
    """
```

**Implementation Details:**
- Query all modules with eager-loaded levels and locations
- For each location, check if `items` relationship is populated (occupied) or empty (free)
- Calculate:
  - `total_locations = Location.query.count()`
  - `occupied_locations = Location.query.join(Item).count()`
  - `occupancy_percentage = (occupied / total) * 100`
- Per-module: aggregate location counts from all child levels
- Per-level: count occupied locations using `len([loc for loc in level.locations if loc.items])`

**Acceptance Criteria:**
- API returns JSON with nested module/level statistics
- Performance test: <500ms response time for 20 modules with 100 levels
- Unit tests cover edge cases (empty modules, fully occupied levels)

**Estimated Effort:** 4 hours

---

### Task 1.2: Live Search API with Location Context
**File:** `backend/app/routes/search.py`

Enhance existing search to return formatted location breadcrumbs:

```python
@bp.route('/api/search/live')
def live_search():
    """
    Query params: ?q=<query>&limit=<num>
    Returns: List of items with:
    - item.name, item.description, item.category
    - location.full_address (e.g., "Zeus:3:B4")
    - location_breadcrumb (e.g., "Zeus Cabinet → Level 3 → B4")
    - module_id, level_id (for highlighting)
    """
```

**Implementation Details:**
- Accept `limit` parameter (default: 5, configurable)
- Use existing `Item.query.filter()` with ilike pattern matching
- Eager-load `location`, `location.level`, `location.level.module`
- Generate `location_breadcrumb` as formatted string: `"{module.name} → Level {level.level_number} → {row}{column}"`
- Return structured JSON with module/level IDs for UI highlighting

**Acceptance Criteria:**
- Search returns results in <200ms for typical queries
- Results include all necessary data for breadcrumb display and highlighting
- Empty query returns empty array (no error)
- Limit parameter respected (default 5, max 20)

**Estimated Effort:** 3 hours

---

### Task 1.3: Location Detail API
**File:** `backend/app/routes/locations.py`

Add endpoint for location drill-down view:

```python
@bp.route('/api/locations/<int:location_id>/detail')
def location_detail(location_id):
    """
    Returns:
    - Full location information (address, dimensions, type)
    - Item in location (if any) with all metadata
    - Breadcrumb context (module → level → location)
    - Adjacent locations (same level, nearby rows/columns)
    """
```

**Implementation Details:**
- Query `Location` with all relationships loaded
- Include item details if present (item.to_dict())
- Calculate adjacent locations: same level, ±1 row/column
- Return navigation context for "drill-down" view

**Acceptance Criteria:**
- Returns 404 if location doesn't exist
- Includes full item details when location is occupied
- Adjacent locations list is accurate (max 8 neighbors in grid)
- Response time <100ms

**Estimated Effort:** 2 hours

---

## Phase 2: Frontend - Module Grid Display

**Goal:** Replace dashboard's two-column layout with module-centric grid

### Task 2.1: Module Grid Layout
**Files:**
- `frontend/templates/index.html` (major rewrite)
- `frontend/static/css/style.css` (add module-grid styles)

Replace existing dashboard content with:

```html
<div x-data="dashboardState()">
  <!-- Persistent Search Bar (see Task 3.1) -->

  <!-- Module Grid -->
  <div class="module-grid">
    <template x-for="module in modules" :key="module.id">
      <div class="module-cell"
           :class="{ 'highlighted': highlightedModule === module.id }"
           @mouseenter="onModuleHover(module.id)"
           @mouseleave="onModuleLeave()">

        <!-- Module Name -->
        <h3 class="module-cell-title" x-text="module.name"></h3>

        <!-- Level Links -->
        <ul class="level-links">
          <template x-for="level in module.levels" :key="level.id">
            <li :class="{ 'highlighted': highlightedLevel === level.id }">
              <a :href="`/levels/${level.id}`" x-text="levelLabel(level)"></a>
              <span class="level-stats" x-text="levelStats(level)"></span>
            </li>
          </template>
        </ul>

        <!-- Module Statistics (minimized text at bottom) -->
        <div class="module-stats-footer">
          <span x-text="moduleStats(module)"></span>
        </div>
      </div>
    </template>
  </div>

  <!-- Footer Statistics (see Task 2.3) -->
</div>
```

**CSS Requirements:**
```css
.module-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}

.module-cell {
  background: var(--card-bg);
  border: 2px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.25rem;
  transition: all 0.2s ease;
}

.module-cell.highlighted {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  transform: translateY(-2px);
}

.module-cell-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  color: var(--text-primary);
}

.level-links {
  list-style: none;
  padding: 0;
  margin: 0 0 1rem 0;
}

.level-links li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  border-radius: 0.25rem;
  transition: background-color 0.15s;
}

.level-links li.highlighted {
  background-color: var(--grid-hover);
}

.level-links a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
}

.level-stats {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 400;
}

.module-stats-footer {
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-color);
  font-size: 0.7rem;
  color: var(--text-muted);
  text-align: center;
}
```

**Alpine.js State Management:**
```javascript
function dashboardState() {
  return {
    modules: [],
    highlightedModule: null,
    highlightedLevel: null,

    init() {
      this.loadModules();
    },

    async loadModules() {
      const response = await fetch('/api/dashboard/stats');
      const data = await response.json();
      this.modules = data.modules;
    },

    levelLabel(level) {
      return level.name || `Level ${level.level_number}`;
    },

    levelStats(level) {
      return `${level.occupied}/${level.total}`;
    },

    moduleStats(module) {
      return `${module.occupied}/${module.total} (${module.occupancy_pct}%)`;
    },

    onModuleHover(moduleId) {
      this.highlightedModule = moduleId;
    },

    onModuleLeave() {
      if (!this.searchHoverActive) {
        this.highlightedModule = null;
        this.highlightedLevel = null;
      }
    }
  };
}
```

**Acceptance Criteria:**
- Modules display in responsive grid (1-4 columns depending on viewport)
- Each module cell shows name, all levels as clickable links, and occupancy stats
- Level statistics appear in deprioritized text (smaller, muted color)
- Module statistics appear at bottom in minimized text
- Grid adapts to viewport: 1 column on mobile, 2 on tablet, 3-4 on desktop

**Estimated Effort:** 6 hours

---

### Task 2.2: Module/Level Highlighting on Hover
**Files:**
- Alpine.js component in `index.html`
- CSS transitions in `style.css`

Implement hover states:
1. **Hovering on module cell** → subtle highlight (border color change, slight elevation)
2. **Hovering on level link** → level list item background change
3. **Hovering on search result** → highlights corresponding module cell and level item (see Task 3.3)

**Implementation:**
- Use Alpine.js `@mouseenter` and `@mouseleave` directives
- Toggle CSS classes dynamically: `.highlighted` on module-cell and level-link
- Smooth transitions (0.15-0.2s duration)
- Ensure highlight persists when search result is hovered (search hover takes priority)

**Acceptance Criteria:**
- Hover feedback is immediate (<50ms visual response)
- Transitions are smooth, no jarring state changes
- Multiple hover sources (module hover vs. search hover) don't conflict
- Accessible: focus states work for keyboard navigation

**Estimated Effort:** 2 hours

---

### Task 2.3: Footer Statistics Bar
**Files:**
- `frontend/templates/index.html` (footer section)
- `frontend/static/css/style.css`

Add persistent footer at bottom of dashboard:

```html
<div class="dashboard-footer-stats">
  <span class="stat-item">
    <strong x-text="stats.modules"></strong> modules
  </span>
  <span class="stat-separator">•</span>
  <span class="stat-item">
    <strong x-text="stats.levels"></strong> levels
  </span>
  <span class="stat-separator">•</span>
  <span class="stat-item">
    <strong x-text="stats.locations"></strong> locations
  </span>
  <span class="stat-separator">•</span>
  <span class="stat-item">
    Overall: <strong x-text="stats.occupancy_pct"></strong>% occupied
    (<span x-text="`${stats.occupied}/${stats.total}`"></span>)
  </span>
</div>
```

**CSS:**
```css
.dashboard-footer-stats {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--card-bg);
  border-top: 1px solid var(--border-color);
  padding: 0.75rem 1rem;
  font-size: 0.75rem;
  color: var(--text-muted);
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.75rem;
  z-index: 90;
}

.stat-item strong {
  color: var(--text-primary);
  font-weight: 600;
}

.stat-separator {
  color: var(--border-color);
}
```

**Acceptance Criteria:**
- Footer stays visible at bottom of viewport (fixed positioning)
- Statistics update when data changes (reactive to Alpine.js state)
- Text is readable but deprioritized (small font, muted color)
- Responsive: stacks vertically on narrow screens

**Estimated Effort:** 1 hour

---

## Phase 3: Frontend - Persistent Search Interface

**Goal:** Add always-visible search bar with live results, hover interactions, and drill-down

### Task 3.1: Persistent Search Bar
**Files:**
- `frontend/templates/index.html`
- `frontend/static/css/style.css`

Add search bar at top of dashboard (below navbar, above module grid):

```html
<div class="persistent-search" x-data="searchState()">
  <div class="search-bar-wrapper">
    <input
      type="text"
      class="search-input"
      placeholder="Search inventory..."
      x-model="query"
      @input.debounce.300ms="performSearch()"
      @focus="searchFocused = true"
      @blur.debounce.200ms="searchFocused = false"
    >
    <span class="search-icon">🔍</span>
    <span class="search-result-count" x-show="results.length > 0" x-text="`${results.length} results`"></span>
  </div>

  <!-- Search Results Dropdown (see Task 3.2) -->
</div>
```

**CSS:**
```css
.persistent-search {
  position: sticky;
  top: 80px; /* Below navbar */
  z-index: 95;
  margin-bottom: 2rem;
}

.search-bar-wrapper {
  position: relative;
  max-width: 600px;
  margin: 0 auto;
}

.search-input {
  width: 100%;
  padding: 0.875rem 3rem 0.875rem 1rem;
  border: 2px solid var(--border-color);
  border-radius: 0.5rem;
  font-size: 1rem;
  background: var(--card-bg);
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.search-icon {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.25rem;
  opacity: 0.5;
}

.search-result-count {
  position: absolute;
  right: 3rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.75rem;
  color: var(--text-muted);
  background: var(--bg-color);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}
```

**Acceptance Criteria:**
- Search bar remains visible when scrolling (sticky positioning)
- Input has clear focus states
- Search triggers after 300ms debounce (prevents excessive API calls)
- Result count appears when results exist

**Estimated Effort:** 2 hours

---

### Task 3.2: Search Results Dropdown
**Files:**
- `frontend/templates/index.html` (search component)
- `frontend/static/css/style.css`

Display live search results in dropdown below search bar:

```html
<div class="search-results-dropdown"
     x-show="searchFocused && results.length > 0"
     x-transition:enter="transition ease-out duration-200"
     x-transition:enter-start="opacity-0 transform scale-95"
     x-transition:enter-end="opacity-100 transform scale-100">

  <template x-for="item in results" :key="item.id">
    <div class="search-result-item"
         @mouseenter="onSearchResultHover(item)"
         @mouseleave="onSearchResultLeave()"
         @click="viewLocation(item.location_id)">

      <div class="result-main">
        <span class="result-name" x-text="item.name"></span>
        <span class="result-category badge" x-text="item.category"></span>
      </div>

      <div class="result-breadcrumb" x-text="item.location_breadcrumb"></div>
    </div>
  </template>

  <div class="search-footer" x-show="results.length >= searchLimit">
    Showing <span x-text="searchLimit"></span> results. Refine search for more specific results.
  </div>
</div>
```

**Alpine.js Search State:**
```javascript
function searchState() {
  return {
    query: '',
    results: [],
    searchLimit: 5, // Configurable
    searchFocused: false,

    async performSearch() {
      if (this.query.length < 2) {
        this.results = [];
        return;
      }

      const response = await fetch(`/api/search/live?q=${encodeURIComponent(this.query)}&limit=${this.searchLimit}`);
      const data = await response.json();
      this.results = data.results;
    },

    onSearchResultHover(item) {
      this.$dispatch('highlight-location', {
        moduleId: item.module_id,
        levelId: item.level_id
      });
    },

    onSearchResultLeave() {
      this.$dispatch('clear-highlight');
    },

    viewLocation(locationId) {
      // Transition to location detail view (Task 3.4)
      this.$dispatch('show-location-detail', { locationId });
    }
  };
}
```

**CSS:**
```css
.search-results-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  left: 0;
  right: 0;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  max-height: 400px;
  overflow-y: auto;
  z-index: 100;
}

.search-result-item {
  padding: 0.875rem 1rem;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background-color 0.15s;
}

.search-result-item:hover {
  background-color: var(--bg-color);
}

.result-main {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.result-name {
  font-weight: 500;
  color: var(--text-primary);
}

.result-breadcrumb {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.search-footer {
  padding: 0.75rem 1rem;
  font-size: 0.75rem;
  color: var(--text-muted);
  text-align: center;
  background: var(--bg-color);
  border-top: 1px solid var(--border-color);
}
```

**Acceptance Criteria:**
- Dropdown appears when search has focus and results exist
- Results display item name, category badge, and location breadcrumb
- Breadcrumb text is minimized (smaller font, muted color)
- Configurable result limit (default 5)
- Footer message appears when result count equals limit
- Smooth enter/exit animations

**Estimated Effort:** 4 hours

---

### Task 3.3: Search Result Hover Highlighting
**Files:**
- Alpine.js components in `index.html`
- Event communication between search and module grid components

Implement cross-component communication:

1. **Search result hover** → emits `highlight-location` event with `moduleId` and `levelId`
2. **Module grid** → listens for event, sets `highlightedModule` and `highlightedLevel`
3. **Corresponding module cell and level link** → receive `.highlighted` class
4. **Search result hover leave** → emits `clear-highlight` event, removes highlights

**Implementation:**
```javascript
// In dashboardState() - add event listeners
Alpine.effect(() => {
  window.addEventListener('highlight-location', (event) => {
    this.highlightedModule = event.detail.moduleId;
    this.highlightedLevel = event.detail.levelId;
  });

  window.addEventListener('clear-highlight', () => {
    this.highlightedModule = null;
    this.highlightedLevel = null;
  });
});
```

**Acceptance Criteria:**
- Hovering over search result highlights the correct module cell
- Corresponding level link also highlights within that module
- Highlight persists while hovering over result
- Highlight clears when mouse leaves result
- No conflicts with direct module/level hover interactions
- Performance: no lag in highlighting (<50ms response)

**Estimated Effort:** 3 hours

---

### Task 3.4: Location Detail Drill-Down View
**Files:**
- `frontend/templates/index.html` (modal/slide-in panel)
- `frontend/static/css/style.css`
- New Alpine.js component for detail view

When user clicks a search result, show location details:

```html
<div class="location-detail-panel"
     x-data="locationDetailState()"
     x-show="visible"
     @show-location-detail.window="showDetail($event.detail.locationId)"
     x-transition:enter="transition ease-out duration-300"
     x-transition:enter-start="transform translate-x-full"
     x-transition:enter-end="transform translate-x-0">

  <div class="detail-header">
    <h2>Location Details</h2>
    <button @click="visible = false" class="close-btn">&times;</button>
  </div>

  <div class="detail-body">
    <!-- Breadcrumb -->
    <div class="detail-breadcrumb" x-text="location.breadcrumb"></div>

    <!-- Location Info -->
    <div class="detail-section">
      <h3>Location</h3>
      <p><strong>Address:</strong> <span x-text="location.full_address"></span></p>
      <p><strong>Type:</strong> <span x-text="location.location_type"></span></p>
      <p x-show="location.dimensions">
        <strong>Dimensions:</strong>
        <span x-text="formatDimensions(location.dimensions)"></span>
      </p>
    </div>

    <!-- Item Info (if occupied) -->
    <div class="detail-section" x-show="location.item">
      <h3>Item in this Location</h3>
      <p><strong>Name:</strong> <span x-text="location.item?.name"></span></p>
      <p><strong>Description:</strong> <span x-text="location.item?.description"></span></p>
      <p x-show="location.item?.category">
        <strong>Category:</strong>
        <span class="badge" x-text="location.item?.category"></span>
      </p>
    </div>

    <!-- Actions -->
    <div class="detail-actions">
      <a :href="`/items/${location.item?.id}`" x-show="location.item" class="btn btn-primary">
        View Full Item Details
      </a>
      <a :href="`/levels/${location.level_id}`" class="btn btn-secondary">
        View Full Level Grid
      </a>
    </div>
  </div>
</div>
```

**Alpine.js Component:**
```javascript
function locationDetailState() {
  return {
    visible: false,
    location: {},

    async showDetail(locationId) {
      const response = await fetch(`/api/locations/${locationId}/detail`);
      const data = await response.json();
      this.location = data;
      this.visible = true;
    },

    formatDimensions(dims) {
      if (!dims) return '';
      return `${dims.width_mm} × ${dims.height_mm} × ${dims.depth_mm} mm`;
    }
  };
}
```

**CSS:**
```css
.location-detail-panel {
  position: fixed;
  right: 0;
  top: 0;
  width: 400px;
  height: 100vh;
  background: var(--card-bg);
  border-left: 1px solid var(--border-color);
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.15);
  z-index: 150;
  overflow-y: auto;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  background: var(--card-bg);
  z-index: 10;
}

.detail-breadcrumb {
  background: var(--bg-color);
  padding: 0.75rem 1rem;
  font-size: 0.8rem;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border-color);
}

.detail-body {
  padding: 1.5rem;
}

.detail-section {
  margin-bottom: 2rem;
}

.detail-section h3 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: var(--text-secondary);
  text-transform: uppercase;
}

.detail-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

@media (max-width: 768px) {
  .location-detail-panel {
    width: 100%;
  }
}
```

**Acceptance Criteria:**
- Panel slides in from right when search result is clicked
- Displays full location address with breadcrumb
- Shows item details if location is occupied
- Provides links to full item details and level grid view
- Close button hides panel with smooth transition
- Responsive: full-width on mobile

**Estimated Effort:** 5 hours

---

## Phase 4: Configuration & Settings

**Goal:** Make search result limit and other UI parameters configurable

### Task 4.1: Configuration Endpoint
**File:** `backend/app/routes/main.py`

Add configuration management:

```python
@bp.route('/api/config')
def get_config():
    """Returns UI configuration"""
    return jsonify({
        'search': {
            'default_limit': 5,
            'max_limit': 20,
            'debounce_ms': 300
        },
        'display': {
            'module_grid_columns': 'auto',  # or fixed number
            'show_empty_modules': True
        }
    })
```

**Acceptance Criteria:**
- Configuration is stored in app config or database
- API returns JSON with all configurable parameters
- Frontend reads config on initialization

**Estimated Effort:** 2 hours

---

### Task 4.2: Settings UI (Optional Enhancement)
**Files:**
- `frontend/templates/settings.html` (new)
- `backend/app/routes/settings.py` (new blueprint)

Add basic settings page to adjust:
- Search result limit (5, 10, 15, 20)
- Module grid column count (auto, 2, 3, 4)
- Show/hide empty modules

**Priority:** Low (can be done after core features)

**Estimated Effort:** 4 hours

---

## Phase 5: Testing & Refinement

### Task 5.1: End-to-End Testing
- **User Flow Test:** Navigate from dashboard → search → result hover → location detail → item view
- **Performance Test:** Dashboard load time with 50 modules, 200 levels, 1000 locations
- **Responsive Test:** Test on mobile (320px), tablet (768px), desktop (1440px)
- **Accessibility Test:** Keyboard navigation, screen reader compatibility

**Estimated Effort:** 6 hours

---

### Task 5.2: Performance Optimization
- Database query optimization (add indexes on commonly searched fields)
- Implement caching for statistics API (Redis or in-memory cache)
- Lazy-load module statistics (fetch per-module on hover if needed)
- Bundle size optimization (ensure Alpine.js is only dependency)

**Estimated Effort:** 4 hours

---

### Task 5.3: Documentation Updates
- Update `README.md` with new dashboard functionality
- Add screenshots/GIFs of new UI
- Document API endpoints in `docs/API.md`
- Update `CLAUDE.md` with new architecture details

**Estimated Effort:** 2 hours

---

## Phase 6: Item Photo Management

**Goal:** Allow users to upload, manage, and display multiple photos per item with a designated main image

### Task 6.1: Database Schema for Item Photos

**File:** `backend/app/models.py`

Add new `ItemPhoto` model:

```python
class ItemPhoto(db.Model):
    """Photos associated with inventory items"""
    __tablename__ = 'item_photos'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)  # Stored filename
    original_filename = db.Column(db.String(255))  # Original upload name
    file_path = db.Column(db.String(500), nullable=False)  # Relative path from uploads dir
    file_size = db.Column(db.Integer)  # Size in bytes
    mime_type = db.Column(db.String(100))  # image/jpeg, image/png, etc.
    is_main = db.Column(db.Boolean, default=False)  # Main photo to display
    display_order = db.Column(db.Integer, default=0)  # Order for gallery display
    caption = db.Column(db.Text)  # Optional caption
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    item = db.relationship('Item', back_populates='photos')

    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'url': f"/uploads/items/{self.file_path}",
            'thumbnail_url': f"/uploads/items/thumbnails/{self.file_path}",
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'is_main': self.is_main,
            'display_order': self.display_order,
            'caption': self.caption,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }

# Update Item model
class Item(db.Model):
    # ... existing fields ...

    # Add relationship
    photos = db.relationship('ItemPhoto', back_populates='item',
                            cascade='all, delete-orphan',
                            order_by='ItemPhoto.display_order')

    def get_main_photo(self):
        """Get the main photo or first photo if no main is set"""
        main = next((p for p in self.photos if p.is_main), None)
        return main or (self.photos[0] if self.photos else None)
```

**Database Migration:**
```bash
docker-compose exec backend flask db migrate -m "Add item_photos table"
docker-compose exec backend flask db upgrade
```

**File Storage Structure:**
```
uploads/
  items/
    {item_id}/
      original/
        {uuid}_{filename}.jpg
      thumbnails/
        {uuid}_{filename}_thumb.jpg
```

**Acceptance Criteria:**
- ItemPhoto model created with all fields
- Relationship to Item established
- Migration creates table successfully
- Cascade delete removes photos when item deleted
- Only one photo per item can be marked as main (enforced in API)

**Estimated Effort:** 2 hours

---

### Task 6.2: Photo Upload API Endpoints

**File:** `backend/app/routes/items.py`

Add photo management endpoints:

```python
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image

UPLOAD_FOLDER = 'uploads/items'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
THUMBNAIL_SIZE = (300, 300)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/<int:item_id>/photos/upload', methods=['POST'])
def upload_item_photo(item_id):
    """Upload one or more photos for an item"""
    item = Item.query.get_or_404(item_id)

    if 'photos' not in request.files:
        return jsonify({'error': 'No photos provided'}), 400

    files = request.files.getlist('photos')
    uploaded_photos = []

    for file in files:
        if file and allowed_file(file.filename):
            # Generate unique filename
            original_filename = secure_filename(file.filename)
            ext = original_filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{ext}"

            # Create directories
            item_dir = os.path.join(UPLOAD_FOLDER, str(item_id), 'original')
            thumb_dir = os.path.join(UPLOAD_FOLDER, str(item_id), 'thumbnails')
            os.makedirs(item_dir, exist_ok=True)
            os.makedirs(thumb_dir, exist_ok=True)

            # Save original
            original_path = os.path.join(item_dir, unique_filename)
            file.save(original_path)

            # Create thumbnail
            with Image.open(original_path) as img:
                img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
                thumb_path = os.path.join(thumb_dir, unique_filename)
                img.save(thumb_path)

            # Get file size
            file_size = os.path.getsize(original_path)

            # Determine display order
            max_order = db.session.query(db.func.max(ItemPhoto.display_order))\
                .filter_by(item_id=item_id).scalar() or 0

            # Create database record
            photo = ItemPhoto(
                item_id=item_id,
                filename=unique_filename,
                original_filename=original_filename,
                file_path=f"{item_id}/original/{unique_filename}",
                file_size=file_size,
                mime_type=file.mimetype,
                is_main=(len(item.photos) == 0),  # First photo is main by default
                display_order=max_order + 1
            )
            db.session.add(photo)
            uploaded_photos.append(photo)

    db.session.commit()

    return jsonify({
        'success': True,
        'photos': [p.to_dict() for p in uploaded_photos]
    })

@bp.route('/<int:item_id>/photos/<int:photo_id>/set-main', methods=['POST'])
def set_main_photo(item_id, photo_id):
    """Set a photo as the main photo for an item"""
    item = Item.query.get_or_404(item_id)
    photo = ItemPhoto.query.filter_by(id=photo_id, item_id=item_id).first_or_404()

    # Unset current main photo
    for p in item.photos:
        p.is_main = False

    # Set new main photo
    photo.is_main = True
    db.session.commit()

    return jsonify({'success': True, 'photo': photo.to_dict()})

@bp.route('/<int:item_id>/photos/<int:photo_id>', methods=['DELETE'])
def delete_photo(item_id, photo_id):
    """Delete a photo"""
    photo = ItemPhoto.query.filter_by(id=photo_id, item_id=item_id).first_or_404()

    # Delete files
    original_path = os.path.join('uploads/items', photo.file_path)
    thumb_path = original_path.replace('/original/', '/thumbnails/')

    try:
        if os.path.exists(original_path):
            os.remove(original_path)
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
    except OSError as e:
        print(f"Error deleting photo files: {e}")

    # If this was the main photo, set another as main
    was_main = photo.is_main
    db.session.delete(photo)

    if was_main:
        item = Item.query.get(item_id)
        if item.photos:
            item.photos[0].is_main = True

    db.session.commit()

    return jsonify({'success': True})

@bp.route('/<int:item_id>/photos/reorder', methods=['POST'])
def reorder_photos(item_id):
    """Reorder photos by providing array of photo IDs in desired order"""
    item = Item.query.get_or_404(item_id)
    photo_ids = request.json.get('photo_ids', [])

    for index, photo_id in enumerate(photo_ids):
        photo = ItemPhoto.query.filter_by(id=photo_id, item_id=item_id).first()
        if photo:
            photo.display_order = index

    db.session.commit()

    return jsonify({'success': True})
```

**Requirements:**
- Add `Pillow` to `requirements.txt` for image processing
- Add `python-magic` for MIME type detection (optional)
- Configure Flask upload settings in `backend/app/__init__.py`

**Acceptance Criteria:**
- Multiple photos can be uploaded at once
- Photos stored with unique filenames to avoid collisions
- Thumbnails generated automatically
- First photo defaults to main
- Main photo can be changed via API
- Photos can be deleted
- Photos can be reordered

**Estimated Effort:** 6 hours

---

### Task 6.3: Photo Display in Item Forms

**Files:**
- `frontend/templates/items/form.html` (edit)
- `frontend/templates/items/view.html` (edit)

Add photo upload/management UI to item edit form:

```html
<!-- In item edit form -->
<div class="form-group" x-data="photoManager()">
    <label>Photos</label>

    <!-- Upload Area -->
    <div class="photo-upload-area"
         @drop.prevent="handleDrop($event)"
         @dragover.prevent="dragOver = true"
         @dragleave.prevent="dragOver = false"
         :class="{ 'drag-over': dragOver }">

        <input type="file"
               id="photo-upload"
               multiple
               accept="image/*"
               @change="handleFileSelect($event)"
               style="display: none;">

        <label for="photo-upload" class="upload-prompt">
            <span class="upload-icon">📷</span>
            <span>Click to upload or drag photos here</span>
            <span class="upload-hint">PNG, JPG, GIF up to 10MB</span>
        </label>
    </div>

    <!-- Photo Gallery -->
    <div class="photo-gallery" x-show="photos.length > 0">
        <template x-for="(photo, index) in photos" :key="photo.id">
            <div class="photo-item" :class="{ 'is-main': photo.is_main }">
                <img :src="photo.thumbnail_url" :alt="photo.original_filename">

                <div class="photo-overlay">
                    <button @click="setMainPhoto(photo.id)"
                            class="btn-icon"
                            :disabled="photo.is_main"
                            title="Set as main photo">
                        <span x-show="photo.is_main">⭐</span>
                        <span x-show="!photo.is_main">☆</span>
                    </button>

                    <button @click="deletePhoto(photo.id)"
                            class="btn-icon btn-danger"
                            title="Delete photo">
                        🗑️
                    </button>
                </div>

                <div class="photo-info" x-show="photo.is_main">
                    <span class="main-badge">Main Photo</span>
                </div>
            </div>
        </template>
    </div>

    <!-- Upload Progress -->
    <div class="upload-progress" x-show="uploading">
        <div class="progress-bar" :style="`width: ${uploadProgress}%`"></div>
        <span x-text="`Uploading... ${uploadProgress}%`"></span>
    </div>
</div>

<script>
function photoManager() {
    return {
        photos: {{ item.photos | tojson }},
        uploading: false,
        uploadProgress: 0,
        dragOver: false,

        async handleFileSelect(event) {
            const files = Array.from(event.target.files);
            await this.uploadPhotos(files);
        },

        async handleDrop(event) {
            this.dragOver = false;
            const files = Array.from(event.dataTransfer.files)
                .filter(f => f.type.startsWith('image/'));
            await this.uploadPhotos(files);
        },

        async uploadPhotos(files) {
            const formData = new FormData();
            files.forEach(file => formData.append('photos', file));

            this.uploading = true;
            this.uploadProgress = 0;

            try {
                const response = await fetch(`/items/{{ item.id }}/photos/upload`, {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                if (data.success) {
                    this.photos.push(...data.photos);
                }
            } catch (error) {
                alert('Error uploading photos');
            } finally {
                this.uploading = false;
                this.uploadProgress = 0;
            }
        },

        async setMainPhoto(photoId) {
            try {
                const response = await fetch(
                    `/items/{{ item.id }}/photos/${photoId}/set-main`,
                    { method: 'POST' }
                );

                if (response.ok) {
                    this.photos.forEach(p => p.is_main = (p.id === photoId));
                }
            } catch (error) {
                alert('Error setting main photo');
            }
        },

        async deletePhoto(photoId) {
            if (!confirm('Delete this photo?')) return;

            try {
                const response = await fetch(
                    `/items/{{ item.id }}/photos/${photoId}`,
                    { method: 'DELETE' }
                );

                if (response.ok) {
                    this.photos = this.photos.filter(p => p.id !== photoId);
                }
            } catch (error) {
                alert('Error deleting photo');
            }
        }
    };
}
</script>
```

**CSS Additions:**
```css
.photo-upload-area {
    border: 2px dashed var(--border-color);
    border-radius: 0.5rem;
    padding: 2rem;
    text-align: center;
    transition: all 0.2s;
    cursor: pointer;
}

.photo-upload-area.drag-over {
    border-color: var(--primary-color);
    background: rgba(37, 99, 235, 0.05);
}

.photo-gallery {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.photo-item {
    position: relative;
    aspect-ratio: 1;
    border: 2px solid var(--border-color);
    border-radius: 0.5rem;
    overflow: hidden;
}

.photo-item.is-main {
    border-color: var(--warning-color);
    box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.photo-item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.photo-overlay {
    position: absolute;
    top: 0;
    right: 0;
    display: flex;
    gap: 0.25rem;
    padding: 0.25rem;
    opacity: 0;
    transition: opacity 0.2s;
}

.photo-item:hover .photo-overlay {
    opacity: 1;
}

.main-badge {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(245, 158, 11, 0.9);
    color: white;
    font-size: 0.7rem;
    padding: 0.25rem;
    text-align: center;
}
```

**Acceptance Criteria:**
- Drag-and-drop photo upload works
- Click to upload works
- Multiple photos can be uploaded at once
- Photo gallery displays thumbnails
- Main photo indicated with star and badge
- Click star to set/unset main photo
- Delete button removes photo
- Upload progress shown

**Estimated Effort:** 5 hours

---

### Task 6.4: Display Main Photo in Views

**Files:**
- `frontend/templates/items/view.html` (update)
- `frontend/templates/index.html` (search results)
- `frontend/templates/modules/view.html` (grid cells)

Add main photo display to various views:

**Item Detail View:**
```html
<!-- At top of item view page -->
<div class="item-header-with-photo">
    <div class="item-main-photo">
        {% if item.get_main_photo() %}
            <img src="{{ item.get_main_photo().url }}"
                 alt="{{ item.name }}">
        {% else %}
            <div class="no-photo-placeholder">
                <span>📦</span>
                <span>No photo</span>
            </div>
        {% endif %}
    </div>

    <div class="item-header-info">
        <h1>{{ item.name }}</h1>
        <!-- Rest of item info -->
    </div>
</div>

<!-- Photo gallery -->
{% if item.photos|length > 1 %}
<div class="item-photo-gallery">
    <h3>All Photos ({{ item.photos|length }})</h3>
    <div class="photo-grid">
        {% for photo in item.photos %}
        <a href="{{ photo.url }}" target="_blank" class="photo-grid-item">
            <img src="{{ photo.thumbnail_url }}" alt="{{ photo.original_filename }}">
        </a>
        {% endfor %}
    </div>
</div>
{% endif %}
```

**Search Results (with thumbnail):**
```javascript
// Update search result item in index.html
<div class="search-result-item-with-photo">
    <div class="result-photo" x-show="item.main_photo">
        <img :src="item.main_photo?.thumbnail_url" :alt="item.name">
    </div>
    <div class="result-content">
        <div class="result-main">
            <span class="result-name" x-text="item.name"></span>
            <span class="badge" x-show="item.category" x-text="item.category"></span>
        </div>
        <div class="result-breadcrumb" x-text="item.location_breadcrumb"></div>
    </div>
</div>
```

**Location Detail Panel:**
```html
<!-- Update detail panel to show item photo -->
<div class="detail-section" x-show="location.item">
    <div class="item-photo-preview" x-show="location.item?.main_photo">
        <img :src="location.item.main_photo?.url" :alt="location.item?.name">
    </div>

    <h3>Item in this Location</h3>
    <!-- Rest of item details -->
</div>
```

**Acceptance Criteria:**
- Main photo displayed prominently in item detail view
- Photo gallery shows all photos
- Search results show thumbnail of main photo
- Location detail panel shows main photo
- Placeholder shown when no photo exists
- Photos are clickable to view full size

**Estimated Effort:** 3 hours

---

### Task 6.5: Update API Responses to Include Photos

**Files:**
- `backend/app/models.py` (update Item.to_dict())
- `backend/app/routes/search.py` (include main_photo)
- `backend/app/routes/locations.py` (include main_photo in item)

Update API responses:

```python
# In models.py - Item.to_dict()
def to_dict(self, include_location=True, include_photos=True):
    result = {
        'id': self.id,
        'name': self.name,
        'description': self.description,
        'category': self.category,
        # ... other fields ...
    }

    if include_photos:
        main_photo = self.get_main_photo()
        result['main_photo'] = main_photo.to_dict() if main_photo else None
        result['photo_count'] = len(self.photos)
        result['photos'] = [p.to_dict() for p in self.photos]

    # ... rest of method ...
    return result
```

**Acceptance Criteria:**
- All API endpoints returning items include main_photo
- Photo count included in responses
- Full photo array optional (for detail views)
- No N+1 query issues (use eager loading)

**Estimated Effort:** 2 hours

---

### Task 6.6: Photo Storage Configuration

**Files:**
- `docker-compose.yml` (add volume mount)
- `backend/app/__init__.py` (configure Flask)
- `.gitignore` (ignore uploads folder)

Configure file storage:

```yaml
# docker-compose.yml
services:
  backend:
    volumes:
      - ./backend:/app
      - ./uploads:/app/uploads  # Add this line
```

```python
# backend/app/__init__.py
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max

# Serve uploaded files in development
from flask import send_from_directory

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
```

```gitignore
# .gitignore
uploads/
*.pyc
__pycache__/
```

**Production Considerations:**
- In production, serve uploads via nginx or CDN
- Consider cloud storage (S3, CloudFlare R2) for scalability
- Implement image optimization pipeline
- Add virus scanning for uploaded files

**Acceptance Criteria:**
- Uploads folder created and mounted
- Files persist across container restarts
- Development server can serve uploaded files
- Production-ready configuration documented

**Estimated Effort:** 1 hour

---

## Summary Timeline (Updated)

| Phase | Tasks | Estimated Hours | Priority |
|-------|-------|-----------------|----------|
| Phase 1: Backend Enhancements | 3 tasks | 9 hours | Critical ✅ |
| Phase 2: Module Grid Display | 3 tasks | 9 hours | Critical ✅ |
| Phase 3: Search Interface | 4 tasks | 14 hours | Critical ✅ |
| Phase 4: Configuration | 2 tasks | 6 hours | Medium |
| Phase 5: Testing & Refinement | 3 tasks | 12 hours | High |
| Phase 6: Item Photo Management | 6 tasks | 19 hours | High |
| **TOTAL** | **21 tasks** | **69 hours** | - |

**Recommended Development Order:**
1. Phase 1 (backend) - provides data for frontend
2. Phase 2 (module grid) - core visual foundation
3. Phase 3 (search) - primary interaction mechanism
4. Phase 5.1 (testing) - validate functionality
5. Phase 4 (configuration) - polish and flexibility
6. Phase 5.2-5.3 (optimization & docs) - production readiness

---

## Technical Considerations

### Browser Compatibility
- Target: Modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- Alpine.js 3.x compatible with all target browsers
- CSS Grid and Flexbox support confirmed

### Performance Targets
- Dashboard initial load: <1 second
- Search response: <200ms
- Smooth 60fps animations
- Works with up to 100 modules without degradation

### Data Flow
```
User Input (Search)
  → API Request (/api/search/live)
  → Database Query (ILIKE on item.name, item.description)
  → JSON Response (items with location data)
  → Alpine.js State Update
  → DOM Update (search results dropdown)
  → Event Emission (on hover)
  → Module Grid Highlight
```

### State Management
- **Alpine.js Stores:** Consider using Alpine.store() for global state (search results, highlights)
- **Event-Driven:** Use custom DOM events for component communication
- **No External State Library:** Alpine.js reactive data is sufficient for this scope

---

## Future Enhancements (Post-Roadmap)

1. **Visual Grid Preview:** Show miniature grid in module cell on hover
2. **Keyboard Navigation:** Arrow keys to navigate module grid and search results
3. **Search Filters:** Filter by category, location, date added
4. **Batch Operations:** Select multiple items from search results
5. **Location Heatmap:** Color-code modules by occupancy percentage
6. **Recent Activity Timeline:** Show recent item additions/moves on dashboard
7. **Export Function:** Export search results or full inventory to CSV/JSON

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Performance degradation with many modules | High | Implement pagination, lazy-loading, or virtual scrolling |
| Search doesn't find expected items | Medium | Add fuzzy matching, synonyms, or full-text search |
| Hover interactions feel laggy | Medium | Optimize event handlers, use CSS transforms for smooth animations |
| Mobile UX is cramped | Medium | Adjust grid columns, increase touch target sizes, simplify mobile layout |
| Database queries are slow | High | Add indexes, implement caching, optimize joins |

---

## Open Questions

1. **Module Ordering:** Should modules be sorted alphabetically, by occupancy, or custom order?
   - **Recommendation:** Alphabetical by default, allow custom sort order in Phase 4

2. **Empty Modules:** Should empty modules (no levels/locations) be shown?
   - **Recommendation:** Show all modules, mark empty ones with special styling

3. **Search Scope:** Should search include module names, level names, or only items?
   - **Recommendation:** Items only for initial implementation, expand in future

4. **Location Detail Panel:** Slide-in from right, or modal overlay?
   - **Recommendation:** Slide-in panel (less disruptive, keeps context visible)

5. **Breadcrumb Format:** "Module → Level → Location" or "Module:Level:Location"?
   - **Recommendation:** Use arrow format for readability, colon format in compact views

---

## Success Metrics

After implementation, measure:

- **Task Completion Time:** How long to find and view a specific item?
  - **Target:** <30 seconds for typical search
- **User Engagement:** Dashboard → Search usage ratio
  - **Target:** >70% of sessions use search
- **Navigation Efficiency:** Average clicks to reach target item
  - **Target:** <3 clicks
- **Page Load Performance:** Time to interactive
  - **Target:** <1 second on modern hardware
- **Mobile Usability:** Task completion rate on mobile vs desktop
  - **Target:** >80% mobile success rate

---

## Notes

- This roadmap assumes the existing codebase (Phase 1 complete) as the foundation
- All new code should follow existing patterns (Alpine.js for reactivity, Flask blueprints for routes)
- Maintain backward compatibility with existing `/items`, `/modules`, `/locations` pages
- The new dashboard is additive - old functionality remains intact
- Consider creating a feature flag to toggle between old and new dashboard during development

---

**Document Version:** 1.0
**Last Updated:** 2025-10-27
**Author:** Claude Code
**Status:** Draft - Awaiting Review
