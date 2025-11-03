# 🗺️ WhereTF? - Development Roadmap

## Current Status: v1.5 (Testing Phase)

**Completed:** Foundation + AI Features
**In Testing:** Semantic search, duplicate detection
**Next Priority:** Testing & validation, then choose Phase 2, 3 refinement, or 5

---

## Phase Overview

| Phase | Status | Goals |
|-------|--------|-------|
| **1 - Foundation** | ✅ Complete | Core inventory management with search-first UI |
| **2 - Smart Locations** | 📋 Planned | Auto-suggest storage, space utilization, compatibility rules |
| **3 - Duplicate Detection** | 🧪 Testing | Embedding-based similarity, specification parsing, merge workflow |
| **4 - Semantic Search** | 🧪 Testing | Natural language queries, vector similarity, ranked results |
| **5 - CLI Interface** | 📋 Planned | Command-line tool, bulk operations, import/export |
| **6 - Voice Interface** | 📋 Planned | Hands-free operation, wake word, speech recognition |
| **7 - Advanced AI** | 📋 Planned | Fine-tuned models, usage analytics, auto-categorization |
| **8 - Production Polish** | 📋 Planned | Multi-user, mobile app, QR codes, monitoring |

---

## Phase 1: Foundation ✅

**What it does:**
- Storage hierarchy (Modules → Levels → Locations)
- Item management with AI-generated descriptions
- Keyword search with omnibox interface
- Location grids and visualization
- Admin panel for system operations

**Status:** Deployed and functional

---

## Phase 2: Smart Location Management 📋

**What it does:**
- Suggest optimal storage locations when adding items
- Track space utilization and availability
- Check compatibility (e.g., no liquids near electronics)
- Provide reorganization recommendations

**Priority:** Medium - improves organization workflow

---

## Phase 3: Duplicate Detection 🧪

**What it does:**
- Detect similar items using embedding similarity
- Parse specifications (M6, 1kΩ, 0805, etc.)
- Side-by-side comparison UI
- Merge duplicates and transfer locations

**Current State:**
- ✅ Embedding-based detection working
- ✅ Resolution UI implemented
- ✅ Soft-delete implemented for merge audit trail
- 🧪 Needs: specification parsing, accuracy validation

**Future Enhancements:**
- Similar Items section on item detail page
  - Show items with high similarity scores
  - Quick actions: View, Mark as Duplicate
  - Marking as duplicate adds pair to resolution queue
  - Helps catch duplicates at item creation time

**Priority:** High - currently testing

---

## Phase 4: Semantic Search 🧪

**What it does:**
- Natural language queries ("metric bolt about 5cm")
- Vector similarity search with pgvector
- Ranked results by relevance
- Search history tracking

**Current State:**
- ✅ Embedding generation working
- ✅ Cosine similarity search implemented
- 🧪 Needs: ranking tuning, real-world validation

**Priority:** High - currently testing

---

## Phase 5: CLI Interface 📋

**What it does:**
- Terminal-based inventory management
- Bulk operations (add, update, delete)
- CSV import/export
- Scriptable for automation

**Priority:** Medium - power user feature

---

## Phase 6: Voice Interface 📋

**What it does:**
- Wake word detection
- Speech-to-text for commands
- Text-to-speech responses
- Hands-free workshop operation

**Priority:** Low - nice to have for workshop use

---

## Phase 7: Advanced AI 📋

**What it does:**
- Fine-tune embedding model on actual inventory
- Usage analytics and access patterns
- Auto-categorization with zero-shot classification
- Suggest items often used together

**Priority:** Medium - depends on Phase 4 results

---

## Phase 8: Production Polish 📋

**What it does:**
- Multi-user authentication
- Mobile-optimized UI / native app
- QR code generation for locations
- Backup/restore UI
- Monitoring dashboard

**Priority:** Low - after core features proven

---

## What's Next?

### Immediate: Testing & Validation (Phase 1.5)

1. Generate realistic test data (200+ items)
2. Test semantic search accuracy
3. Validate duplicate detection
4. Fine-tune similarity thresholds
5. Document findings

### Short-Term: Choose Priority

**Option A - Phase 2:** Better organization with smart location suggestions
**Option B - Refine 3/4:** Add spec parsing, improve search, tune thresholds
**Option C - Phase 5:** Add CLI for power users and bulk operations

### Long-Term

Continue through phases based on usage patterns and pain points discovered during testing.

---

## Success Metrics

- **Phase 1:** Can manage 100+ items efficiently ✅
- **Phase 3:** Duplicate detection catches 90%+ with <10% false positives 🧪
- **Phase 4:** Semantic search returns relevant results for natural queries 🧪
- **Phase 5:** CLI faster than UI for bulk operations
- **Phase 6:** Voice recognition >95% accuracy in workshop environment
- **Phase 7:** Recommendations are useful and actionable
- **Phase 8:** System runs reliably with <200ms response time
