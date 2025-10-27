# ✅ Phase 1 Testing Checklist

Use this checklist to verify your inventory system is working correctly after deployment.

---

## Pre-Deployment Checks

### System Requirements
- [ ] Docker installed and running
- [ ] Docker Compose installed
- [ ] Minimum 2GB RAM available
- [ ] Minimum 10GB disk space free
- [ ] Ports 5000, 5432, 8080 available

**Verification:**
```bash
docker --version
docker-compose --version
df -h
netstat -tuln | grep -E '5000|5432|8080'
```

---

## Deployment Checks

### Container Startup
- [ ] All containers start without errors
- [ ] PostgreSQL container is healthy
- [ ] Backend container is running
- [ ] Nginx container is running

**Verification:**
```bash
cd inventory-system
docker-compose up -d
sleep 30
docker-compose ps

# Expected output: 3 containers with "Up" status
# inventory-db       Up (healthy)
# inventory-backend  Up
# inventory-nginx    Up
```

### Log Check
- [ ] No errors in PostgreSQL logs
- [ ] Backend initializes database
- [ ] No critical errors in backend logs
- [ ] Nginx starts successfully

**Verification:**
```bash
docker-compose logs postgres | grep -i error
docker-compose logs backend | grep -i error
docker-compose logs nginx | grep -i error
```

### Web Access
- [ ] Can access http://localhost:8080
- [ ] Homepage loads correctly
- [ ] No 404 or 500 errors
- [ ] Navigation menu appears

**Verification:**
```bash
curl -I http://localhost:8080
# Should return: HTTP/1.1 200 OK
```

---

## Database Checks

### Connection
- [ ] Backend can connect to PostgreSQL
- [ ] Database 'inventory' exists
- [ ] All tables are created

**Verification:**
```bash
docker-compose exec postgres psql -U inventoryuser -d inventory -c "\dt"

# Expected tables:
# - modules
# - levels
# - locations
# - items
# - item_locations
```

### Schema
- [ ] `modules` table has correct columns
- [ ] `levels` table has correct columns
- [ ] `locations` table has correct columns
- [ ] `items` table has correct columns
- [ ] `item_locations` table has correct columns
- [ ] All foreign keys are set up
- [ ] All unique constraints exist

**Verification:**
```bash
docker-compose exec postgres psql -U inventoryuser -d inventory -c "\d modules"
docker-compose exec postgres psql -U inventoryuser -d inventory -c "\d items"
```

---

## Module Management Tests

### Create Module
- [ ] Can access "Modules" page
- [ ] "Add Module" button works
- [ ] Can create module with name "TestModule"
- [ ] Description field works
- [ ] Location description field works
- [ ] Module appears in list after creation
- [ ] Can view module details

**Test Steps:**
1. Navigate to http://localhost:8080/modules
2. Click "Add Module"
3. Fill in:
   - Name: TestModule
   - Description: Test module for verification
   - Location: Test bench
4. Click "Create Module"
5. Verify module appears in list
6. Click module name to view details

### Edit Module
- [ ] Can click "Edit" on module
- [ ] Can change name
- [ ] Can change description
- [ ] Changes save correctly
- [ ] Updated module displays new info

### Delete Module
- [ ] Can delete empty module
- [ ] Confirmation prompt appears
- [ ] Module is removed from list

⚠️ **Note:** Don't delete TestModule yet - needed for level tests

---

## Level Management Tests

### Create Level
- [ ] Can view module details page
- [ ] "Add Level" button works
- [ ] Can create level with number 1
- [ ] Row count field works (try 4)
- [ ] Column count field works (try 6)
- [ ] Level appears under module
- [ ] Locations are auto-created (24 for 4×6)

**Test Steps:**
1. View TestModule details
2. Click "Add Level"
3. Fill in:
   - Level Number: 1
   - Name: Test Level
   - Rows: 4
   - Columns: 6
   - Description: 4×6 grid test
4. Click "Create Level"
5. Verify level appears
6. Click level to view locations

### Verify Location Grid
- [ ] Grid displays correctly (4 rows × 6 columns)
- [ ] All locations are present (A1-D6)
- [ ] Can click individual locations
- [ ] Empty locations are indicated
- [ ] Grid is visually clear

### Edit Level
- [ ] Can edit level details
- [ ] Can change name
- [ ] Can change description
- [ ] Changes save

⚠️ **Note:** Changing rows/columns after creation doesn't auto-create new locations in Phase 1

---

## Location Tests

### View Location
- [ ] Can click on location (e.g., A1)
- [ ] Location details page loads
- [ ] Full address displays (TestModule:1:A1)
- [ ] Empty location shows "No items"

### Edit Location
- [ ] Can edit location
- [ ] Can set location type (try "medium_bin")
- [ ] Can set dimensions (width, height, depth)
- [ ] Can add notes
- [ ] Changes save correctly

### Location Types
- [ ] Can select "small_box"
- [ ] Can select "medium_bin"
- [ ] Can select "large_bin"
- [ ] Can select "liquid_container"
- [ ] Can select "smd_container"
- [ ] Can select "general"

---

## Item Management Tests

### Create Item (Simple)
- [ ] Can access "Items" page
- [ ] "Add Item" button works
- [ ] Can create item with minimal info
- [ ] Name field required
- [ ] Description field required

**Test Steps:**
1. Navigate to http://localhost:8080/items
2. Click "Add Item"
3. Fill in:
   - Name: Test Item
   - Description: Simple test item
4. Click "Create Item"
5. Verify item appears in list

### Create Item (Full)
- [ ] Can fill all fields
- [ ] Category dropdown works
- [ ] Item type dropdown works
- [ ] Quantity field works
- [ ] Unit field works
- [ ] Tags field works (comma-separated)
- [ ] Location can be selected
- [ ] Item saves with all data

**Test Steps:**
1. Create item with all fields:
   - Name: M6x50 Test Bolt
   - Description: Hex head bolt, M6 diameter, 50mm long, zinc plated
   - Category: Fasteners
   - Item Type: solid
   - Quantity: 100
   - Unit: pieces
   - Tags: bolt, m6, metric, test
   - Location: TestModule:1:A1
2. Verify all data displays correctly

### View Item
- [ ] Can click item name
- [ ] Item details page loads
- [ ] All fields display correctly
- [ ] Location(s) shown
- [ ] Tags display as list

### Edit Item
- [ ] Can edit item
- [ ] Can change name
- [ ] Can change description
- [ ] Can change quantity
- [ ] Can add/remove tags
- [ ] Changes save

### Delete Item
- [ ] Can delete item
- [ ] Confirmation prompt appears
- [ ] Item removed from list

---

## Item-Location Relationship Tests

### Multiple Locations
- [ ] Can add item to multiple locations
- [ ] Each location shows separately
- [ ] Quantities per location tracked
- [ ] Total quantity calculated correctly

**Test Steps:**
1. Edit existing item
2. Add to location TestModule:1:B2
3. Set quantity at B2 to 50
4. Verify item shows in both A1 and B2
5. Verify total quantity updates

### Location Displays Item
- [ ] Navigate to location A1
- [ ] Item appears in location's item list
- [ ] Item quantity shown
- [ ] Can click item to view details

---

## Search Tests

### Basic Search
- [ ] Can access search page
- [ ] Search box works
- [ ] Enter "test" finds test items
- [ ] Results display correctly
- [ ] Item details visible in results

### Search by Name
- [ ] Search for exact item name
- [ ] Item is found
- [ ] Partial name search works

### Search by Description
- [ ] Search for word in description
- [ ] Items with matching descriptions found
- [ ] Multiple matches displayed

### Search by Tags
- [ ] Search for tag (e.g., "bolt")
- [ ] Items with that tag found
- [ ] Multiple tags work

### Search by Category
- [ ] Search for category name
- [ ] Items in that category found

### No Results
- [ ] Search for non-existent term
- [ ] "No results" message displays
- [ ] No errors occur

---

## API Tests

### Modules API
```bash
# List modules
curl http://localhost:8080/modules/api/modules

# Expected: JSON array of modules
```

- [ ] Returns valid JSON
- [ ] Contains created modules
- [ ] Status code 200

### Items API
```bash
# List items
curl http://localhost:8080/items/api/items

# Expected: JSON array of items
```

- [ ] Returns valid JSON
- [ ] Contains created items
- [ ] Status code 200

### Search API
```bash
# Search items
curl "http://localhost:8080/items/api/items?search=test"

# Expected: JSON array of matching items
```

- [ ] Returns filtered results
- [ ] Search query works
- [ ] Status code 200

### Locations API
```bash
# List locations
curl http://localhost:8080/locations/api/locations

# Expected: JSON array of locations
```

- [ ] Returns valid JSON
- [ ] Contains created locations
- [ ] Status code 200

---

## Sample Data Tests

### Load Sample Data
```bash
python3 create_sample_data.py
```

- [ ] Script runs without errors
- [ ] 3 modules created (Zeus, Muse, Apollo)
- [ ] Levels created for each module
- [ ] 10+ items created
- [ ] Items have proper descriptions
- [ ] Can browse sample data in UI

### Verify Sample Data
- [ ] Zeus module exists
- [ ] Zeus has 3 levels
- [ ] Muse module exists
- [ ] Apollo module exists
- [ ] Electronics items exist
- [ ] Fastener items exist
- [ ] Tool items exist
- [ ] Paint items exist

---

## UI/UX Tests

### Navigation
- [ ] Home link works
- [ ] Modules link works
- [ ] Items link works
- [ ] Search link works
- [ ] All pages load without errors

### Responsive Design
- [ ] Desktop view looks good (1920×1080)
- [ ] Laptop view looks good (1366×768)
- [ ] Tablet view works (768×1024)
- [ ] Mobile view works (375×667)

**Note:** Optimal mobile support comes in Phase 8

### Forms
- [ ] All forms have proper labels
- [ ] Required fields marked
- [ ] Validation works
- [ ] Error messages are clear
- [ ] Success messages appear

### Visual Elements
- [ ] Grid layouts display correctly
- [ ] Tables are readable
- [ ] Buttons are clickable
- [ ] Links are styled
- [ ] Colors are consistent

---

## Performance Tests

### Load Time
- [ ] Homepage loads in < 2 seconds
- [ ] Module list loads in < 2 seconds
- [ ] Item list loads in < 2 seconds
- [ ] Search results appear quickly

### With Data
Add 100 items, then:
- [ ] Search still fast (< 1 second)
- [ ] List pages load quickly
- [ ] No noticeable slowdown

### Concurrent Access
Open 3 browser tabs:
- [ ] All tabs work independently
- [ ] No conflicts
- [ ] Data stays consistent

---

## Data Integrity Tests

### Relationships
- [ ] Deleting level doesn't orphan locations
- [ ] Deleting module deletes levels
- [ ] Item-location relationships persist
- [ ] No broken foreign keys

**Test:**
1. Create module with level and items
2. Delete module
3. Verify levels and locations also deleted
4. Items remain but locations removed

### Unique Constraints
- [ ] Can't create duplicate module names
- [ ] Can't create duplicate level numbers in same module
- [ ] Can't create duplicate locations in same level

**Test:**
1. Try to create module with existing name
2. Should show error
3. Verify constraint enforced

---

## Backup/Restore Tests

### Backup
```bash
docker-compose exec postgres pg_dump -U inventoryuser inventory > test_backup.sql
```

- [ ] Backup file created
- [ ] File size > 0 bytes
- [ ] Contains SQL statements
- [ ] No errors during backup

### Restore
```bash
# Reset database
docker-compose down -v
docker-compose up -d
sleep 30

# Restore
docker-compose exec -T postgres psql -U inventoryuser inventory < test_backup.sql
```

- [ ] Restore completes without errors
- [ ] All modules restored
- [ ] All items restored
- [ ] All relationships intact
- [ ] Can access UI with restored data

---

## Error Handling Tests

### Invalid Input
- [ ] Empty required fields show error
- [ ] Invalid numbers rejected
- [ ] SQL injection attempts blocked
- [ ] XSS attempts sanitized

**Test:**
1. Try to create item without name
2. Try to create item without description
3. Try negative quantity
4. Try SQL in name field: `'; DROP TABLE items; --`
5. Verify all rejected gracefully

### 404 Handling
- [ ] Invalid URLs show 404 page
- [ ] Non-existent item IDs handled
- [ ] Non-existent module IDs handled

**Test:**
```bash
curl http://localhost:8080/items/999999
curl http://localhost:8080/invalid-page
```

### Network Issues
- [ ] Graceful handling if database unreachable
- [ ] Error message shown to user
- [ ] System recovers after database restart

**Test:**
```bash
docker-compose stop postgres
# Try to use UI - should show error
docker-compose start postgres
# Wait 10 seconds, try again - should work
```

---

## Security Tests (Phase 1 Basic)

### Port Exposure
```bash
netstat -tuln | grep -E '5432|5000|8080'
```

- [ ] Port 8080 open (nginx)
- [ ] Port 5432 open locally (if needed for admin)
- [ ] Port 5000 only accessible via nginx
- [ ] No unnecessary ports open

### SQL Injection
- [ ] Try SQL injection in search
- [ ] Try SQL injection in item name
- [ ] Verify SQLAlchemy prevents injection
- [ ] No direct SQL exposed

**Test:**
```bash
curl "http://localhost:8080/items/api/items?search=' OR '1'='1"
# Should return empty or safe results, not all items
```

⚠️ **Note:** Full security hardening comes in Phase 8

---

## Clean-up Tests

### Reset System
```bash
docker-compose down -v
docker-compose up -d
```

- [ ] All data deleted
- [ ] Fresh database created
- [ ] System starts clean
- [ ] No orphaned data

### Storage Space
```bash
du -sh data/
```

- [ ] Database size reasonable (< 100MB for test data)
- [ ] No excessive log files
- [ ] Backups not accumulating

---

## Documentation Tests

### README
- [ ] All commands in README work
- [ ] Examples are accurate
- [ ] Links are not broken
- [ ] Screenshots match UI (if included)

### QUICKSTART
- [ ] 5-minute deployment actually works
- [ ] Sample data script works
- [ ] First-time setup instructions accurate

### API Documentation
- [ ] All listed endpoints work
- [ ] Examples are correct
- [ ] Response formats match documentation

---

## Success Criteria

Phase 1 is considered fully working if:

- ✅ All containers run reliably
- ✅ Can create modules, levels, locations
- ✅ Can add, edit, delete items
- ✅ Search finds items correctly
- ✅ Multiple items per location works
- ✅ UI is usable and clear
- ✅ No data loss or corruption
- ✅ API endpoints respond correctly
- ✅ Backup/restore works
- ✅ Sample data loads successfully

---

## Checklist Summary

### Critical (Must Pass)
- [ ] System starts (docker-compose up -d)
- [ ] Web UI accessible
- [ ] Can create modules
- [ ] Can create items
- [ ] Search works
- [ ] No data loss
- [ ] Backup works

### Important (Should Pass)
- [ ] All CRUD operations work
- [ ] Grid visualization works
- [ ] API endpoints respond
- [ ] Sample data loads
- [ ] Error handling works

### Nice to Have (Good if Pass)
- [ ] Performance is good
- [ ] UI is polished
- [ ] Mobile view works
- [ ] Documentation complete

---

## Test Report Template

```
# Phase 1 Test Report

Date: ___________
Tester: ___________

## Environment
- OS: ___________
- Docker Version: ___________
- RAM: ___________
- Disk Space: ___________

## Results
- Critical Tests Passed: ___ / ___
- Important Tests Passed: ___ / ___
- Nice-to-Have Tests Passed: ___ / ___

## Issues Found
1. ___________
2. ___________
3. ___________

## Overall Status
[ ] PASS - Ready for use
[ ] PARTIAL - Usable with limitations
[ ] FAIL - Not ready

## Notes
___________________________________________
___________________________________________
```

---

## Next Steps After Testing

### If All Tests Pass:
1. ✅ Start using the system for real inventory
2. ✅ Add your first 20-50 items
3. ✅ Set up regular backups
4. ✅ Provide feedback for Phase 2

### If Some Tests Fail:
1. Document failures
2. Check logs: `docker-compose logs`
3. Try rebuilding: `docker-compose up --build`
4. Reset if needed: `docker-compose down -v && docker-compose up -d`
5. Retry failed tests

### If Critical Tests Fail:
1. Check prerequisites (Docker, ports, etc.)
2. Review error messages
3. Check system resources
4. Consult troubleshooting in README
5. Open issue with logs

---

## Continuous Testing

As you use the system:

### Daily
- [ ] Backup works
- [ ] Items save correctly
- [ ] Search finds items

### Weekly
- [ ] No performance degradation
- [ ] No data corruption
- [ ] All features still working

### Monthly
- [ ] Full backup/restore test
- [ ] Review any errors in logs
- [ ] Check disk space usage

---

**Happy Testing! 🧪✅**

Once you've verified Phase 1 works correctly, you're ready to start using it for real inventory management!
