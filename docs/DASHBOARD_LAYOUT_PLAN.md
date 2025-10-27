# Dashboard Layout Plan - Module-Centric Design

## Visual Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 🏠 Inventory System    [Dashboard] [Items] [Modules] [Locations]        │ ← Navbar (existing)
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  🔍  Search inventory...                              5 results │    │ ← Persistent Search Bar
│  └─────────────────────────────────────────────────────────────────┘    │   (sticky, always visible)
│                                                                           │
│  ┌─────────────────────────────────┐  ┌────────────────────────────┐   │
│  │                                 │  │  ╔═══════════════════════╗  │   │
│  │  ┌───────────────────────────┐  │  │  ║ Search Results        ║  │   │
│  │  │ Zeus Electronics Cabinet  │  │  │  ╠═══════════════════════╣  │   │
│  │  ├───────────────────────────┤  │  │  ║ Arduino Uno Rev3      ║  │   │ ← Search Results
│  │  │ → Level 1 (Drawer 1)   4/8│◄─┼──┼──║   Electronics Cabinet ║  │   │   Dropdown (on focus)
│  │  │ → Level 2 (Drawer 2)   6/8│  │  │  ║   → Level 1 → A1      ║  │   │
│  │  │ → Level 3 (Drawer 3)   8/8│  │  │  ╠═══════════════════════╣  │   │   Hovering result
│  │  │                           │  │  │  ║ Resistor 10K          ║  │   │   highlights module
│  │  │ 18/24 (75%)               │  │  │  ║   Zeus → Level 2 → B3 ║  │   │   & level on left
│  │  └───────────────────────────┘  │  │  ╚═══════════════════════╝  │   │
│  │                                 │  └────────────────────────────┘   │
│  │  ┌───────────────────────────┐  │                                   │
│  │  │ Poseidon Tools Cabinet    │  │                                   │
│  │  ├───────────────────────────┤  │                                   │
│  │  │ → Shelf A              3/12│  │                                   │
│  │  │ → Shelf B              8/12│  │  ┌────────────────────────────┐  │
│  │  │ → Shelf C              2/12│  │  │ Location Detail Panel      │  │
│  │  │                           │  │  │ ┌────────────────────────┐ │  │
│  │  │ 13/36 (36%)               │  │  │ │ Zeus → Level 1 → A1    │ │  │ ← Detail Panel
│  │  └───────────────────────────┘  │  │ ├────────────────────────┤ │  │   (slide-in from right
│  │                                 │  │ │ Location: A1           │ │  │   when result clicked)
│  │  ┌───────────────────────────┐  │  │ │ Type: general          │ │  │
│  │  │ Athena Components         │  │  │ │                        │ │  │
│  │  ├───────────────────────────┤  │  │ │ Item:                  │ │  │
│  │  │ → Drawer 1             0/16│  │  │ │ Arduino Uno Rev3       │ │  │
│  │  │ → Drawer 2             2/16│  │  │ │ Arduino microcontroller│ │  │
│  │  │                           │  │  │ │                        │ │  │
│  │  │ 2/32 (6%)                 │  │  │ │ [View Full Details]    │ │  │
│  │  └───────────────────────────┘  │  │ │ [View Level Grid]      │ │  │
│  │                                 │  │ └────────────────────────┘ │  │
│  └─────────────────────────────────┘  └────────────────────────────┘  │
│                                                                           │
│                                                                           │
│  (Module grid continues, responsive 1-4 columns)                         │
│                                                                           │
├─────────────────────────────────────────────────────────────────────────┤
│ 3 modules • 6 levels • 92 locations • Overall: 50% (46/92)               │ ← Footer Stats Bar
└─────────────────────────────────────────────────────────────────────────┘   (fixed at bottom)
```

## Component Breakdown

### 1. Persistent Search Bar (Sticky, Top)
```
┌───────────────────────────────────────────────┐
│ 🔍  Search inventory...          5 results    │
└───────────────────────────────────────────────┘
```

**Properties:**
- Position: `sticky`, `top: 80px` (below navbar)
- Width: `max-width: 600px`, centered
- Z-index: `95` (above module grid, below dropdown)
- State: Expands to show dropdown when focused + has results

**Behavior:**
- Debounced input (300ms)
- Min 2 characters to trigger search
- Shows result count when results exist
- Focus state: prominent border + dropdown appears

---

### 2. Search Results Dropdown (Conditional)
```
╔════════════════════════════════╗
║ Search Results                 ║
╠════════════════════════════════╣
║ Arduino Uno Rev3          [📦] ║ ← Hover highlights
║   Electronics Cabinet → L1 → A1║   module & level
╠════════════════════════════════╣
║ Resistor 10K              [⚡] ║
║   Zeus → Level 2 → B3          ║
╚════════════════════════════════╝
Showing 5 results
```

**Properties:**
- Position: `absolute`, below search bar
- Z-index: `100` (above everything)
- Max height: `400px`, scroll if needed
- Appears: When `searchFocused && results.length > 0`
- Animation: Fade + scale in (200ms)

**Result Item Structure:**
```html
<div class="search-result-item">
  <div class="result-main">
    <span class="result-name">Arduino Uno Rev3</span>
    <span class="badge">electronics</span>
  </div>
  <div class="result-breadcrumb">
    Electronics Cabinet → Drawer 1 → A1
  </div>
</div>
```

**Interactions:**
- **Hover** → Emit event to highlight corresponding module + level
- **Click** → Show location detail panel (slide-in from right)
- **Footer** → "Showing N results. Refine search..." (if limit reached)

---

### 3. Module Grid (Main Content Area)
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Module Name     │  │ Module Name     │  │ Module Name     │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ → Level 1   4/8 │  │ → Shelf A   3/12│  │ → Drawer 1  0/16│
│ → Level 2   6/8 │  │ → Shelf B   8/12│  │ → Drawer 2  2/16│
│ → Level 3   8/8 │  │ → Shelf C   2/12│  │                 │
│                 │  │                 │  │                 │
│ 18/24 (75%)     │  │ 13/36 (36%)     │  │ 2/32 (6%)       │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

**Grid Properties:**
- CSS Grid: `repeat(auto-fill, minmax(280px, 1fr))`
- Gap: `1.5rem`
- Responsive:
  - Mobile (<768px): 1 column
  - Tablet (768-1024px): 2 columns
  - Desktop (>1024px): 3-4 columns

**Module Cell Structure:**
```html
<div class="module-cell" :class="{ highlighted: highlightedModule === id }">
  <!-- Module Title -->
  <h3 class="module-cell-title">Zeus Electronics Cabinet</h3>

  <!-- Level Links -->
  <ul class="level-links">
    <li :class="{ highlighted: highlightedLevel === levelId }">
      <a href="/levels/1">Level 1 (Drawer 1)</a>
      <span class="level-stats">4/8</span>
    </li>
    <!-- ... more levels ... -->
  </ul>

  <!-- Module Stats Footer -->
  <div class="module-stats-footer">
    18/24 (75%)
  </div>
</div>
```

**Module Cell States:**
1. **Normal** → White background, subtle border
2. **Hover** → Border color change, slight elevation
3. **Highlighted** (from search) → Primary color border, shadow glow

**Level Link Format:**
- Primary text: `Level 1 (Drawer 1)` or `Level 1` if no custom name
- Stats: `4/8` (occupied/total) in muted text, right-aligned

**Module Stats Footer:**
- Format: `18/24 (75%)`
- Style: Small text (0.7rem), muted color, centered, border-top separator

---

### 4. Location Detail Panel (Slide-in, Right)
```
┌────────────────────────────────┐
│ Location Details         [×]   │
├────────────────────────────────┤
│ Zeus → Level 1 → A1            │ ← Breadcrumb
├────────────────────────────────┤
│                                │
│ LOCATION                       │
│ Address: A1                    │
│ Type: general                  │
│ Dimensions: 50×30×20 mm        │
│                                │
│ ITEM IN THIS LOCATION          │
│ Name: Arduino Uno Rev3         │
│ Description: Arduino micro...  │
│ Category: [electronics]        │
│                                │
│ [View Full Item Details]       │
│ [View Full Level Grid]         │
│                                │
└────────────────────────────────┘
```

**Properties:**
- Position: `fixed`, `right: 0`, `top: 0`
- Width: `400px` (desktop), `100%` (mobile)
- Height: `100vh`
- Z-index: `150`
- Animation: Slide in from right (300ms)
- Scroll: `overflow-y: auto`

**Trigger:** Clicking a search result dispatches `show-location-detail` event

**Content Sections:**
1. **Header** → Title + close button (sticky)
2. **Breadcrumb** → Module → Level → Location (background color)
3. **Location Info** → Address, type, dimensions
4. **Item Info** → Full item details if occupied
5. **Actions** → Links to item detail page, level grid view

**Close Actions:**
- Click close button (×)
- Click outside panel (optional)
- Press Escape key

---

### 5. Footer Statistics Bar (Fixed Bottom)
```
┌─────────────────────────────────────────────────────────────┐
│ 3 modules • 6 levels • 92 locations • Overall: 50% (46/92) │
└─────────────────────────────────────────────────────────────┘
```

**Properties:**
- Position: `fixed`, `bottom: 0`, `left: 0`, `right: 0`
- Height: `auto` (padding: 0.75rem)
- Background: Card background with top border
- Z-index: `90`
- Font size: `0.75rem` (small)
- Text color: Muted

**Content Format:**
- **Bold numbers**, regular labels
- Separator: `•` between stats
- Final stat: `Overall: 50% (46/92)`
- Responsive: Stacks vertically on narrow screens (<480px)

---

## Interaction Flow

### Flow 1: Search → Highlight → View Detail

```
User types "arduino" in search bar
         ↓
[300ms debounce]
         ↓
API call: GET /search/api/live?q=arduino&limit=5
         ↓
Results appear in dropdown
         ↓
User hovers over "Arduino Uno Rev3" result
         ↓
Event: highlight-location { moduleId: 1, levelId: 1 }
         ↓
Zeus Electronics Cabinet gets .highlighted class
Level 1 link gets .highlighted class
         ↓
User clicks result
         ↓
Event: show-location-detail { locationId: 1 }
         ↓
API call: GET /locations/api/locations/1/detail
         ↓
Detail panel slides in from right
         ↓
Shows full location + item information
```

### Flow 2: Browse Modules → Drill Down to Level

```
User views module grid
         ↓
User hovers over "Zeus Electronics Cabinet"
         ↓
Module cell shows hover state (subtle highlight)
         ↓
User hovers over "Level 1 (Drawer 1)" link
         ↓
Level link shows hover state (background color)
         ↓
User clicks level link
         ↓
Navigate to /levels/1 (existing level grid view)
         ↓
Shows full grid with all locations
```

### Flow 3: Direct Module Hover (No Search)

```
User hovers over module cell
         ↓
Module border color changes
Slight elevation (translateY -2px)
         ↓
User hovers over specific level link
         ↓
Level background color changes
         ↓
User moves mouse away
         ↓
All hover states clear
```

---

## Responsive Behavior

### Desktop (>1024px)
- Module grid: 3-4 columns
- Search bar: Centered, max 600px wide
- Detail panel: 400px wide slide-in
- Footer: Single horizontal line

### Tablet (768-1024px)
- Module grid: 2 columns
- Search bar: Full width with padding
- Detail panel: Fixed position, 300px wide
- Footer: Single horizontal line

### Mobile (<768px)
- Module grid: 1 column
- Search bar: Full width
- Detail panel: Full screen overlay (100% width)
- Footer: Stacks vertically with centered text
- Navbar: Hamburger menu (existing behavior)

---

## State Management (Alpine.js)

### Dashboard State
```javascript
{
  modules: [],              // Array of module data from API
  highlightedModule: null,  // ID of currently highlighted module
  highlightedLevel: null,   // ID of currently highlighted level
  searchHoverActive: false  // Flag to preserve highlight during search hover
}
```

### Search State
```javascript
{
  query: '',                // Current search query
  results: [],              // Search results array
  searchLimit: 5,           // Configurable result limit
  searchFocused: false      // Is search input focused?
}
```

### Location Detail State
```javascript
{
  visible: false,           // Is panel visible?
  location: {}              // Current location data
}
```

---

## Color Scheme & Visual Hierarchy

### Text Hierarchy
1. **Primary** (module name): `1.25rem`, `font-weight: 600`, `--text-primary`
2. **Secondary** (level links): `1rem`, `font-weight: 500`, `--primary-color`
3. **Tertiary** (stats): `0.75rem`, `font-weight: 400`, `--text-muted`
4. **Footer**: `0.75rem`, `--text-muted`

### Spacing
- Module cell padding: `1.25rem`
- Level links spacing: `0.5rem` per item
- Grid gap: `1.5rem`
- Search bar margin bottom: `2rem`

### Borders & Shadows
- **Normal module**: `2px solid var(--border-color)`
- **Highlighted module**: `2px solid var(--primary-color)` + `box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1)`
- **Search dropdown**: `box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15)`
- **Detail panel**: `box-shadow: -4px 0 12px rgba(0, 0, 0, 0.15)`

### Transitions
- Module hover: `all 0.2s ease`
- Level link hover: `background-color 0.15s`
- Search dropdown: `opacity + scale 200ms`
- Detail panel: `transform 300ms ease-out`

---

## Accessibility Considerations

1. **Keyboard Navigation**
   - Tab through module cells and level links
   - Arrow keys to navigate search results
   - Escape to close detail panel
   - Enter to select search result

2. **Screen Readers**
   - Proper ARIA labels on search input
   - Role="search" on search bar
   - Announce result count when search completes
   - Announce when module/level is highlighted

3. **Focus Management**
   - Visible focus rings on all interactive elements
   - Focus trap in detail panel when open
   - Return focus to search result when panel closes

4. **Color Contrast**
   - All text meets WCAG AA standards
   - Hover states don't rely solely on color
   - Highlighted states use both color + shadow

---

## Performance Considerations

1. **API Calls**
   - Dashboard stats: Load once on page load, cache for session
   - Search: Debounced 300ms, cancel previous requests
   - Location detail: Load on demand, cache results

2. **DOM Updates**
   - Alpine.js reactivity handles efficient updates
   - Virtual scrolling not needed (typical <100 modules)
   - Smooth CSS transitions instead of JS animations

3. **Image/Icon Loading**
   - Use emoji icons (no HTTP requests)
   - SVG icons inline for instant rendering

4. **Target Metrics**
   - Initial page load: <1 second
   - Search response: <200ms
   - Smooth 60fps hover interactions
   - Detail panel slide-in: <300ms

---

## Implementation Priority Order

### Phase 2.1: Module Grid (Critical)
1. Replace current dashboard HTML
2. Fetch data from `/api/dashboard/stats`
3. Render module grid with responsive CSS
4. Display level links with stats
5. Add module stats footer

### Phase 2.2: Hover Highlighting (Critical)
1. Module hover states
2. Level hover states
3. Event listeners for search-triggered highlights

### Phase 2.3: Footer Stats (Medium)
1. Fixed footer bar
2. Display overall statistics
3. Responsive stacking

### Phase 3.1: Search Bar (Critical)
1. Sticky search input
2. Debounced API calls
3. Result count display

### Phase 3.2: Search Dropdown (Critical)
1. Results dropdown UI
2. Result item rendering
3. Show/hide logic

### Phase 3.3: Search Highlighting (Critical)
1. Hover → emit event
2. Module grid receives event
3. Apply highlight classes

### Phase 3.4: Detail Panel (High)
1. Slide-in panel component
2. Fetch detail API
3. Display location + item info
4. Action buttons

---

## Visual Design Tokens

```css
:root {
  /* Module Grid */
  --module-cell-bg: var(--card-bg);
  --module-cell-border: var(--border-color);
  --module-cell-border-highlighted: var(--primary-color);
  --module-cell-padding: 1.25rem;
  --module-grid-gap: 1.5rem;
  --module-grid-min-width: 280px;

  /* Search */
  --search-max-width: 600px;
  --search-dropdown-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  --search-result-hover-bg: var(--bg-color);

  /* Detail Panel */
  --detail-panel-width: 400px;
  --detail-panel-width-mobile: 100%;
  --detail-panel-shadow: -4px 0 12px rgba(0, 0, 0, 0.15);

  /* Footer */
  --footer-height: auto;
  --footer-font-size: 0.75rem;
  --footer-z-index: 90;

  /* Typography */
  --module-title-size: 1.25rem;
  --level-link-size: 1rem;
  --stats-size: 0.75rem;

  /* Timing */
  --transition-fast: 0.15s;
  --transition-medium: 0.2s;
  --transition-slow: 0.3s;
  --debounce-delay: 300ms;
}
```

---

This layout prioritizes:
- **Scan-ability**: Visual module grid for quick browsing
- **Search-first**: Always-visible search as primary interaction
- **Context**: Breadcrumbs and location detail provide navigation context
- **Efficiency**: Minimal clicks to reach target information
- **Feedback**: Hover highlights show relationships between search results and modules
