# WhereTF? - Quick Start Guide

## Prerequisites

Before starting:
- [ ] Docker installed (`docker --version`)
- [ ] Docker Compose installed (`docker-compose --version`)
- [ ] 4GB RAM available (for AI features)
- [ ] 20GB disk space
- [ ] Ports 5000, 5432, 8080, 11434 available

---

## Deploy in 3 Steps

```bash
# 1. Navigate to project
cd wheretf

# 2. Start all services
docker-compose up -d

# 3. Wait for startup (30-60 seconds)
docker-compose logs -f backend
# Look for: "WhereTF? - Bin there, found that."
```

**Access:** http://localhost:8080

---

## First-Time Setup

### 1. Create a Module
Modules are storage units (cabinets, shelving, etc.)

**Navigation:** Modules → Add Module

**Example:**
```
Name: Zeus
Description: Main electronics storage
Location: North wall, workshop
```

### 2. Add a Level
Levels are shelves/drawers within modules

**Navigation:** Click module → Add Level

**Example:**
```
Level Number: 1
Name: Top Drawer
Rows: 4
Columns: 6
Description: Small components
```

This creates a 4×6 grid: A1-A6, B1-B6, C1-C6, D1-D6 (24 locations)

### 3. Add an Item (AI-Enhanced)
Items can use AI to generate descriptions

**Navigation:** Dashboard → Add Item (or Items → New Item)

**Example:**
```
1. Enter raw input: "M6 hex bolt 50mm zinc"
2. Click "Generate Description"
3. AI populates:
   - Name: M6 Hex Bolt
   - Description: Hex head bolt, M6 diameter, 50mm length, zinc plated finish
   - Category: Fasteners
   - Type: bolt
   - Tags: M6, hex, bolt, zinc, metric
4. Select location: Zeus:1:A1
5. Create Item
```

### 4. Search for Items
Two search modes available

**Keyword Search:**
- Enter: "M6"
- Click "Search" button
- Returns exact matches

**AI Semantic Search:**
- Enter: "metric bolt about 5cm long"
- Click "AI Search" button
- Returns semantically similar items with scores

---

## Common Operations

### View Storage Hierarchy
```
Modules → Click module → Click level → See grid → Click location
```

### Add Location to Existing Item
```
Items → Find item → Click "Add Location" → Select → Save
```

### Check for Duplicates
```
Duplicates → View pending pairs → Review side-by-side → Keep one
```

### Process Embeddings (Admin)
```
Admin → "Process Embeddings" → Generates vectors for AI search
Admin → "Detect Duplicates" → Finds similar items
```

---

## Managing the System

### Start/Stop
```bash
# Stop (keeps data)
docker-compose stop

# Start again
docker-compose start

# Restart service
docker-compose restart backend

# Shutdown (keeps data)
docker-compose down

# Reset everything (deletes data!)
docker-compose down -v
```

### Backup
```bash
# Database backup
docker exec inventory-db pg_dump -U inventoryuser inventory > backup_$(date +%Y%m%d).sql

# Full backup
tar -czf wheretf-backup-$(date +%Y%m%d).tar.gz data/
```

### Restore
```bash
# Restore database
docker exec -i inventory-db psql -U inventoryuser inventory < backup.sql
```

---

## Troubleshooting

### Services Won't Start
```bash
# Check status
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs postgres
docker-compose logs nginx
docker-compose logs ollama

# Restart specific service
docker-compose restart backend
```

### Port Already in Use
Edit `docker-compose.yml`, change the port mapping:
```yaml
ports:
  - "8081:80"  # Changed from 8080
```

### Can't Access UI
```bash
# Check nginx
docker-compose logs nginx

# Check all services running
docker-compose ps

# Restart all
docker-compose restart
```

### Database Connection Error
```bash
# Check postgres health
docker-compose logs postgres

# Wait for healthy status
docker-compose ps
# Should show "healthy" for postgres
```

---

## Network Access

### From Other Devices

1. Find server IP:
```bash
hostname -I
# or
ip addr show | grep "inet "
```

2. Access from other devices:
```
http://192.168.1.100:8080
```

---

## Security Checklist

**For local/development use:** Default settings are fine

**For production deployment:**
- [ ] Change database password in `docker-compose.yml`
- [ ] Set unique `SECRET_KEY` environment variable
- [ ] Configure firewall rules
- [ ] Enable HTTPS with reverse proxy
- [ ] Set up automated backups
- [ ] Don't expose port 5432 (PostgreSQL)

---

## What's Next?

**Immediate:**
1. Add 10-20 test items
2. Try both search modes (keyword vs AI)
3. Test duplicate detection
4. Explore the admin panel

**Short-term:**
- Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for workflows
- Check [ROADMAP.md](ROADMAP.md) for upcoming features

**Long-term:**
- Organize your full inventory
- Fine-tune search thresholds based on results
- Provide feedback on AI feature accuracy

---

**System deployed! Start organizing at http://localhost:8080 🚀**
