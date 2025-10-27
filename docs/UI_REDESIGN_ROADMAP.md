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

## Summary Timeline

| Phase | Tasks | Estimated Hours | Priority |
|-------|-------|-----------------|----------|
| Phase 1: Backend Enhancements | 3 tasks | 9 hours | Critical |
| Phase 2: Module Grid Display | 3 tasks | 9 hours | Critical |
| Phase 3: Search Interface | 4 tasks | 14 hours | Critical |
| Phase 4: Configuration | 2 tasks | 6 hours | Medium |
| Phase 5: Testing & Refinement | 3 tasks | 12 hours | High |
| **TOTAL** | **15 tasks** | **50 hours** | - |

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
