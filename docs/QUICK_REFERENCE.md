# 📋 Quick Reference Card

## Essential Commands

### Starting & Stopping
```bash
# Start system
docker-compose up -d

# Stop system (keep data)
docker-compose stop

# Restart system
docker-compose restart

# Shutdown completely (keep data)
docker-compose down

# Nuclear option (DELETE ALL DATA)
docker-compose down -v
```

### Status Checks
```bash
# Check if containers are running
docker-compose ps

# View logs (all services)
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f nginx
```

### Backup & Restore
```bash
# Backup database
docker-compose exec postgres pg_dump -U inventoryuser inventory > backup_$(date +%Y%m%d).sql

# Backup entire data directory
tar -czf backup_$(date +%Y%m%d).tar.gz data/

# Restore database
docker-compose exec -T postgres psql -U inventoryuser inventory < backup_20241026.sql
```

### Troubleshooting
```bash
# Restart a stuck container
docker-compose restart backend

# Rebuild containers
docker-compose up --build -d

# Check container health
docker-compose ps

# Reset everything
docker-compose down -v && docker-compose up -d
```

---

## Web Interface

### Access
- Local: `http://localhost:8080`
- Network: `http://YOUR_IP:8080`

### Navigation
- **Dashboard** → Overview of inventory
- **Modules** → Manage storage units
- **Items** → Browse/add inventory
- **Search** → Find items

### Adding Items Flow
1. Click "Items" → "Add Item"
2. Fill in name and description
3. Select category and type
4. Enter quantity
5. Choose/create location
6. Add tags (comma-separated)
7. Click "Create Item"

### Location Format
```
ModuleName:LevelNumber:RowCol

Examples:
Zeus:1:A3    → Module "Zeus", Level 1, Location A3
Muse:2:B5    → Module "Muse", Level 2, Location B5
Apollo:3:C2  → Module "Apollo", Level 3, Location C2
```

---

## Common Workflows

### Workflow 1: New Storage Module
```
1. Modules → Add Module
   - Name: Zeus
   - Description: Electronics cabinet
   - Location: North wall

2. Click module → Add Level
   - Level: 1
   - Rows: 4
   - Columns: 6
   - Creates 24 locations (A1-D6)

3. Repeat for other levels
```

### Workflow 2: Adding First Item
```
1. Items → Add Item
2. Name: M6 Bolts
3. Description: Hex head bolt, M6 diameter, 50mm long, zinc plated
4. Category: Fasteners
5. Type: solid
6. Quantity: 100
7. Unit: pieces
8. Location: Zeus:1:A3
9. Tags: bolt, metric, m6, hex
10. Create Item
```

### Workflow 3: Finding Items
```
Option A: Browse
1. Modules → Zeus
2. Level 1
3. Click location (e.g., A3)
4. See all items in that location

Option B: Search
1. Search → Type "M6"
2. View results
3. Click item for details & location
```

### Workflow 4: Moving Items
```
1. Find item (search or browse)
2. Click item name
3. Click "Edit"
4. Change location
5. Update quantity at each location
6. Save
```

### Workflow 5: Organizing
```
1. Create module for category (e.g., "Electronics")
2. Add levels for subcategories
   - Level 1: Resistors
   - Level 2: Capacitors
   - Level 3: ICs
3. Set up grid for each level
4. Move items to appropriate locations
5. Use tags for cross-referencing
```

---

## Tips & Best Practices

### Item Descriptions
✅ **Good:**
- "Pan head phillips screw, #8 size, 3/4 inch long, mild steel, zinc plated"
- "Ceramic capacitor, 0.1 microfarad, 0805 package, 50V rating, X7R dielectric"
- "M6 hex bolt, 50mm length, zinc plated, metric coarse thread"

❌ **Bad:**
- "Screw"
- "Capacitor"
- "Bolt"

### Tagging Strategy
```
Use multiple tags for findability:
- Material: steel, aluminum, plastic, ceramic
- Size: m6, #8, 0805, 1/4-inch
- Type: screw, bolt, resistor, capacitor
- Finish: zinc, stainless, black-oxide
- Category: fastener, electronics, tool
```

### Module Naming
```
✅ Descriptive & Memorable:
- Zeus (main electronics)
- Muse (fasteners)
- Apollo (tools)
- Workshop-Main
- Garage-Cabinet-1

❌ Generic:
- Cabinet1
- Storage2
- Box3
```

### Level Organization
```
Top to Bottom or Most to Least Used:

Level 1: Frequently accessed items
Level 2: Moderate use
Level 3: Occasional use
Level 4: Rarely used / archive

Or by size:
Level 1: Small components
Level 2: Medium parts
Level 3: Large items
Level 4: Bulk storage
```

---

## Location Types

| Type | Best For | Examples |
|------|----------|----------|
| `small_box` | Tiny components | SMD parts, small screws |
| `medium_bin` | Standard parts | Resistors, bolts, LEDs |
| `large_bin` | Bigger items | Tools, wire spools |
| `liquid_container` | Liquids/chemicals | Paints, solvents, oils |
| `smd_container` | Surface-mount | 0402, 0603, 0805 parts |
| `bulk_bin` | Loose items | Zip ties, cable, wire |
| `tool_holder` | Tools | Screwdrivers, pliers |
| `general` | Default | Anything |

---

## Item Types

| Type | Description | Examples |
|------|-------------|----------|
| `solid` | Standard parts | Bolts, resistors, brackets |
| `liquid` | Liquids/coatings | Paint, glue, solvents |
| `smd_component` | Surface-mount | 0805 caps, SOT-23 transistors |
| `bulk` | Loose/bulk items | Wire, zip ties, sandpaper |
| `tool` | Tools/equipment | Screwdrivers, meters, crimpers |
| `consumable` | Used up over time | Solder, flux, tape |

---

## API Quick Reference

### List Items
```bash
curl http://localhost:8080/items/api/items
```

### Search Items
```bash
curl http://localhost:8080/items/api/items?search=M6
```

### Get Item Details
```bash
curl http://localhost:8080/items/api/items/42
```

### List Modules
```bash
curl http://localhost:8080/modules/api/modules
```

### List Locations
```bash
curl http://localhost:8080/locations/api/locations
```

---

## Keyboard Shortcuts (Web UI)

| Key | Action |
|-----|--------|
| `/` | Focus search |
| `Ctrl+K` | Quick search |
| `Escape` | Close modals |

*(More shortcuts coming in future phases)*

---

## Maintenance Schedule

### Daily
- Use the system!
- Add items as you acquire them

### Weekly
- Review uncategorized items
- Update quantities as needed
- Check for low stock

### Monthly
- Backup database
- Review organization
- Archive old logs (Phase 8)

### Quarterly
- Deep clean/reorganize
- Review location efficiency
- Update documentation

---

## When Things Go Wrong

### Problem: Can't access web UI

**Check:**
```bash
# Are containers running?
docker-compose ps

# Check nginx logs
docker-compose logs nginx

# Restart nginx
docker-compose restart nginx
```

### Problem: Items not saving

**Check:**
```bash
# Check backend logs
docker-compose logs backend

# Check database
docker-compose exec postgres psql -U inventoryuser inventory -c "SELECT COUNT(*) FROM items;"

# Restart backend
docker-compose restart backend
```

### Problem: Search not working

**Check:**
```bash
# Check backend logs
docker-compose logs backend

# Try searching via API
curl "http://localhost:8080/items/api/items?search=test"
```

### Problem: Database connection failed

**Fix:**
```bash
# Restart PostgreSQL
docker-compose restart postgres

# Wait 10 seconds, then restart backend
sleep 10
docker-compose restart backend
```

### Problem: Port already in use

**Fix:**
Edit `docker-compose.yml`:
```yaml
nginx:
  ports:
    - "8081:80"  # Change 8080 to 8081
```

Then:
```bash
docker-compose down && docker-compose up -d
```

### Problem: Out of disk space

**Fix:**
```bash
# Remove old Docker images
docker system prune -a

# Remove old backups
rm old_backup_*.sql

# Clean up logs
docker-compose logs --tail=100 > recent_logs.txt
# (Then manually clean up old logs)
```

---

## Performance Tips

1. **Add more RAM** to Docker (Settings → Resources)
2. **Use SSD** for data directory
3. **Regular backups** prevent data loss
4. **Limit concurrent users** (Phase 1 is single-user optimized)
5. **Index frequently searched fields** (automatically done)

---

## Security Checklist

For production deployments:

- [ ] Changed default PostgreSQL password
- [ ] Set secure `SECRET_KEY`
- [ ] PostgreSQL port not exposed to internet
- [ ] Using HTTPS (Let's Encrypt)
- [ ] Firewall configured
- [ ] Regular backups enabled
- [ ] Updates applied regularly
- [ ] Monitoring enabled (Phase 8)

---

## Sample Data

Want to test with realistic data?

```bash
python3 create_sample_data.py
```

This adds:
- 3 modules (Zeus, Muse, Apollo)
- Multiple levels per module
- 10 sample items

Delete sample data later:
```sql
docker-compose exec postgres psql -U inventoryuser inventory
DELETE FROM items WHERE name LIKE '%sample%';
```

---

## Getting Help

1. **Check logs:** `docker-compose logs`
2. **Review README.md** for detailed docs
3. **Check ROADMAP.md** for future features
4. **Try sample data** to verify setup
5. **Ask for help** (open issue, forum, etc.)

---

## Phase 1 Limitations

What's NOT included yet (coming in future phases):

- ❌ AI semantic search (Phase 4)
- ❌ Duplicate detection (Phase 3)
- ❌ Location suggestions (Phase 2)
- ❌ CLI interface (Phase 5)
- ❌ Voice control (Phase 6)
- ❌ User authentication (Phase 8)
- ❌ Mobile app (Phase 8)
- ❌ Barcode scanning (Phase 8)

But you CAN:
- ✅ Track unlimited items
- ✅ Organize in modules/levels/locations
- ✅ Search by keyword
- ✅ View location grids
- ✅ Export/backup data
- ✅ Access from any device on network

---

## Next Steps

1. **Deploy:** `docker-compose up -d`
2. **Create first module:** Your main storage unit
3. **Add 10-20 items:** Get familiar with the system
4. **Experiment:** Try different organizations
5. **Provide feedback:** What works? What's missing?

---

## Emergency Recovery

If everything breaks:

```bash
# 1. Backup current database (if possible)
docker-compose exec postgres pg_dump -U inventoryuser inventory > emergency_backup.sql

# 2. Stop everything
docker-compose down

# 3. Fresh start (DELETES DATA)
docker-compose down -v
docker-compose up -d

# 4. Restore from backup
docker-compose exec -T postgres psql -U inventoryuser inventory < emergency_backup.sql
```

---

## Version Info

- **Version:** 1.0.0 (Phase 1)
- **Status:** Production Ready
- **Last Updated:** October 2024

---

**Print this card and keep it near your workstation!** 📌

---

## Quick URL Reference

| Service | URL |
|---------|-----|
| Web UI | http://localhost:8080 |
| API Docs | http://localhost:8080/api (Phase 8) |
| Health Check | http://localhost:8080/health |

---

**Happy organizing! 🏠🔧📦**
