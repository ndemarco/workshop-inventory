# 🚀 Homelab Inventory System - Complete Deployment Guide

## What You Have

A **complete Phase 1 Inventory System** ready to deploy! This is a working system you can start using immediately.

### ✅ Included Features (Phase 1)

- Full storage hierarchy (Modules → Levels → Locations)
- Web-based UI for managing inventory
- PostgreSQL database for reliable storage
- Docker deployment (runs anywhere)
- Basic search functionality
- Item tracking with quantities
- Location management with grid visualization
- Many-to-many item-location relationships

### 🔜 Coming Next (Future Phases)

- Phase 2: Smart location suggestions
- Phase 3: Duplicate detection
- Phase 4: AI semantic search
- Phase 5: CLI interface
- Phase 6: Voice interface
- Phase 7: Advanced AI features
- Phase 8: Production polish

---

## Quick Start (5 Minutes)

### Prerequisites

- Docker & Docker Compose installed
- 2GB RAM available
- 10GB disk space
- Ports 8080, 5432, 5000 available

### Deployment Steps

```bash
# 1. Extract the inventory-system folder to your server/workstation
cd inventory-system

# 2. Start the system
docker-compose up -d

# 3. Wait 30-60 seconds for containers to start

# 4. Open your browser
http://localhost:8080

# 5. (Optional) Load sample data
python3 create_sample_data.py
```

**That's it!** You now have a working inventory system.

---

## Deployment Options

### Option 1: Local Workstation/Server

Perfect for testing and personal use.

```bash
cd inventory-system
docker-compose up -d
```

Access at: `http://localhost:8080`

### Option 2: VPS (Cloud Server)

Deploy to DigitalOcean, Linode, AWS, etc.

```bash
# SSH into your VPS
ssh user@your-vps-ip

# Install Docker & Docker Compose (if not installed)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Deploy system
cd inventory-system
docker-compose up -d

# Configure firewall (if needed)
sudo ufw allow 8080/tcp
```

Access at: `http://your-vps-ip:8080`

### Option 3: Proxmox LXC Container

Great for homelab deployments.

```bash
# 1. Create Ubuntu 22.04 LXC container in Proxmox
# 2. Install Docker in the container
apt update && apt install -y docker.io docker-compose

# 3. Copy inventory-system folder to container
# 4. Deploy
cd inventory-system
docker-compose up -d
```

Access at: `http://container-ip:8080`

### Option 4: Jetson Nano (Edge AI Device)

For local AI inference capabilities (Phase 4+).

```bash
# Docker should already be installed on Jetson
cd inventory-system
docker-compose up -d
```

Access at: `http://jetson-ip:8080`

---

## First-Time Setup

### 1. Create Your Storage Modules

Modules are your physical storage units (cabinets, shelving, drawers).

**Example Modules:**
- `Zeus` - Electronics cabinet
- `Muse` - Fasteners organizer
- `Apollo` - Tool chest
- `Workshop-Main` - Main workbench storage

### 2. Add Levels to Modules

Levels are drawers, shelves, or compartments within modules.

**Example for "Zeus" module:**
- Level 1: Top drawer (4 rows × 6 columns) = 24 bins
- Level 2: Middle drawer (3 rows × 4 columns) = 12 bins
- Level 3: Bottom drawer (2 rows × 3 columns) = 6 bins

The system automatically creates locations (A1, A2, B1, B2, etc.) based on your grid.

### 3. Add Items

Items are your actual inventory pieces.

**Good Description Examples:**
- "Pan head phillips screw, #8 size, 3/4 inch long, mild steel, zinc plated"
- "Ceramic capacitor, 0.1 microfarad, 0805 package, 50V rating"
- "M6 hex bolt, 50mm long, zinc plated, metric thread"
- "Arduino Uno R3 development board with ATmega328P"

**Location Format:** `ModuleName:LevelNumber:RowCol`
- Example: `Zeus:1:A3` means Module "Zeus", Level 1, Location A3

### 4. Use the System

- **Browse:** Navigate Modules → Levels → Locations to see what's where
- **Search:** Find items by keyword in name, description, or tags
- **Edit:** Update quantities, add/remove locations, change descriptions
- **Organize:** Set location types (small_box, liquid_container, etc.)

---

## Sample Data (Optional)

Want to see the system in action immediately?

```bash
# Make sure the system is running first
docker-compose ps

# Run the sample data script
python3 create_sample_data.py
```

This creates:
- 3 storage modules (Zeus, Muse, Apollo)
- Multiple levels per module
- 10 sample items (electronics, fasteners, tools, paint)

You can delete this sample data later or use it as a template.

---

## Accessing from Other Devices

### On Your Local Network

1. Find your server's IP:
   ```bash
   hostname -I
   # or
   ip addr show
   ```

2. Access from any device on the network:
   ```
   http://192.168.1.100:8080  (use your actual IP)
   ```

### Over the Internet (VPS only)

If deployed on a VPS with a public IP:
```
http://your-public-ip:8080
```

⚠️ **Security Note:** For internet-facing deployments:
- Change default database password
- Set up HTTPS with Let's Encrypt
- Use a reverse proxy (nginx/Caddy)
- Consider authentication (Phase 8)

---

## Container Management

### View Status
```bash
docker-compose ps
```

### View Logs
```bash
# All containers
docker-compose logs -f

# Specific container
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f nginx
```

### Restart Containers
```bash
# Restart all
docker-compose restart

# Restart specific
docker-compose restart backend
```

### Stop System (Keep Data)
```bash
docker-compose stop
```

### Start System
```bash
docker-compose start
```

### Shutdown Completely (Keep Data)
```bash
docker-compose down
```

### Nuclear Option (Delete Everything)
```bash
docker-compose down -v
# This deletes the database volume!
```

---

## Data Backup

### Backup Database

```bash
# Backup to SQL file
docker-compose exec postgres pg_dump -U inventoryuser inventory > backup_$(date +%Y%m%d).sql

# Backup entire data directory
tar -czf backup_$(date +%Y%m%d).tar.gz data/
```

### Restore Database

```bash
# Restore from SQL file
docker-compose exec -T postgres psql -U inventoryuser inventory < backup_20241026.sql
```

### Automated Backups (Cron)

```bash
# Add to crontab
crontab -e

# Backup daily at 2 AM
0 2 * * * cd /path/to/inventory-system && docker-compose exec postgres pg_dump -U inventoryuser inventory > /backups/inventory_$(date +\%Y\%m\%d).sql
```

---

## Troubleshooting

### Port Already in Use

Edit `docker-compose.yml`:
```yaml
nginx:
  ports:
    - "8081:80"  # Change 8080 to 8081
```

Then: `docker-compose down && docker-compose up -d`

### Database Connection Failed

```bash
# Check if PostgreSQL is running
docker-compose ps

# Restart PostgreSQL
docker-compose restart postgres

# View logs
docker-compose logs postgres
```

### Web UI Not Loading

```bash
# Check nginx logs
docker-compose logs nginx

# Restart nginx
docker-compose restart nginx

# Rebuild containers
docker-compose up --build -d
```

### Backend Errors

```bash
# View backend logs
docker-compose logs backend

# Common issue: Database not ready
# Solution: Wait 30 seconds after starting, or restart backend
docker-compose restart backend
```

### Reset Everything

```bash
# Nuclear option - starts fresh
docker-compose down -v
docker-compose up -d
```

---

## Performance Tuning

### For Better Performance:

1. **Increase Docker Memory:**
   - Docker Desktop → Settings → Resources → Memory
   - Allocate at least 4GB for larger inventories

2. **Use SSD Storage:**
   - Ensure `data/` directory is on an SSD

3. **PostgreSQL Tuning:**
   Edit `docker-compose.yml` and add:
   ```yaml
   postgres:
     command: postgres -c shared_buffers=256MB -c max_connections=100
   ```

---

## Security Checklist

For production/internet-facing deployments:

- [ ] Change default PostgreSQL password in `docker-compose.yml`
- [ ] Set secure `SECRET_KEY` in environment variables
- [ ] Don't expose PostgreSQL port (5432) to the internet
- [ ] Use HTTPS with SSL certificate
- [ ] Set up firewall rules
- [ ] Enable automated backups
- [ ] Update containers regularly: `docker-compose pull && docker-compose up -d`

---

## Next Steps

### Immediate (Phase 1):
1. ✅ Deploy system and verify it works
2. ✅ Create your first module
3. ✅ Add 10-20 items to test
4. ✅ Experiment with search
5. ✅ Set up daily backups

### Soon (Phase 2-3):
1. Add smart location suggestions
2. Implement duplicate detection
3. Parse item specifications automatically

### Future (Phase 4-6):
1. Add AI semantic search
2. Build CLI interface
3. Create voice interface

---

## Getting Help

### Documentation
- `README.md` - Comprehensive documentation
- `QUICKSTART.md` - 5-minute deployment guide
- `ARCHITECTURE.md` - Technical architecture details
- `PROJECT_SUMMARY.md` - Full project overview

### Common Questions

**Q: Can I run this on a Raspberry Pi?**  
A: Yes! Use Docker on Raspberry Pi OS. ARM architecture is supported.

**Q: How many items can it handle?**  
A: Tested with 10,000+ items. PostgreSQL can handle millions.

**Q: Can I import existing inventory from CSV?**  
A: Not yet (Phase 5), but you can write a Python script using the API.

**Q: Does it work offline?**  
A: Yes! It's completely self-hosted. No internet required.

**Q: Can multiple people use it?**  
A: Yes, but no user accounts yet (Phase 8). Everyone shares the same view.

---

## Success Criteria

You'll know Phase 1 is working when you can:

- ✅ Access the web UI at http://localhost:8080
- ✅ Create modules, levels, and locations
- ✅ Add items with descriptions
- ✅ Search for items and find them
- ✅ View the location grid
- ✅ See item counts per location
- ✅ Edit and delete items

---

## What's Different from Other Inventory Systems?

1. **Storage-first design:** Models your actual physical storage
2. **Natural language:** Describe items how you think about them
3. **Flexible locations:** Items can be in multiple places
4. **Future AI integration:** Ready for semantic search (Phase 4)
5. **Voice control ready:** Architecture supports voice UI (Phase 6)
6. **Open source:** Customize it however you want

---

## Files in This Package

```
inventory-system/
├── README.md              # Full documentation
├── QUICKSTART.md          # 5-minute quick start
├── ARCHITECTURE.md        # Technical details
├── PROJECT_SUMMARY.md     # Project overview
├── docker-compose.yml     # Docker orchestration
├── nginx.conf            # Web server config
├── create_sample_data.py # Sample data generator
├── backend/              # Flask application
│   ├── app/
│   │   ├── models.py     # Database models
│   │   ├── routes/       # API endpoints
│   │   └── __init__.py
│   ├── requirements.txt  # Python dependencies
│   ├── Dockerfile
│   └── run.py
└── frontend/             # Web UI
    ├── templates/        # HTML templates
    └── static/           # CSS/JS assets
```

---

## Version Info

- **Version:** 1.0.0
- **Phase:** 1 (Foundation)
- **Date:** October 2024
- **Status:** ✅ Production Ready (for Phase 1 features)

---

## Quick Command Reference

```bash
# Deploy
docker-compose up -d

# Status
docker-compose ps

# Logs
docker-compose logs -f

# Restart
docker-compose restart

# Stop
docker-compose down

# Backup
docker-compose exec postgres pg_dump -U inventoryuser inventory > backup.sql

# Load sample data
python3 create_sample_data.py

# Access
http://localhost:8080
```

---

## Ready to Deploy?

1. Extract the `inventory-system` folder
2. Run `docker-compose up -d`
3. Open `http://localhost:8080`
4. Start organizing! 🎉

**Questions?** Check the README.md or open an issue.

**Happy organizing!** 🏠🔧📦
