# 🚀 WhereTF? - START HERE

## Quick Start

**Get running in 3 steps:**

```bash
# 1. Navigate to project
cd wheretf

# 2. Start system
docker-compose up -d

# 3. Open browser
http://localhost:8080
```

**Done!** The system is now running.

---

## What It Does

**Core Features (v1.5):**
- Store and find items across hierarchical locations
- AI-powered description generation
- Semantic search (natural language queries)
- Duplicate detection and resolution
- Search-first UI with omnibox interface
- Admin panel for system operations

**Current Status:**
- ✅ Foundation complete
- 🧪 Testing semantic search and duplicate detection
- 📋 Planned: Smart locations, CLI, voice interface

---

## Essential Commands

```bash
# Start system
docker-compose up -d

# Stop system
docker-compose stop

# View logs
docker-compose logs -f backend

# Backup database
docker exec inventory-db pg_dump -U inventoryuser inventory > backup.sql

# Restart services
docker-compose restart backend
```

---

## First Steps

1. **Create a Module** - Storage unit (e.g., "Zeus", "Workbench Cabinet")
2. **Add Levels** - Shelves/drawers within module
3. **Create Locations** - Individual storage spots (grid positions)
4. **Add Items** - Use AI to generate descriptions from short inputs
5. **Search** - Find items with keyword or semantic search

---

## Documentation Guide

**Quick Reference:**
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Commands and workflows

**Planning:**
- [ROADMAP.md](ROADMAP.md) - Development phases and priorities
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Detailed system overview

**Architecture:**
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical implementation details

---

## Troubleshooting

**Can't access UI?**
```bash
docker-compose logs nginx
docker-compose ps
```

**Items not saving?**
```bash
docker-compose logs backend
docker-compose restart backend
```

**Database issues?**
```bash
docker-compose logs postgres
docker-compose restart postgres
```

**Reset everything:**
```bash
docker-compose down -v
docker-compose up -d
```

---

## System Requirements

**Minimum:**
- Docker & Docker Compose installed
- 4GB RAM (for AI features)
- 20GB disk space
- Ports 5000, 5432, 8080, 11434 available

**Tested On:**
- Linux, macOS, Windows (Docker Desktop)
- Raspberry Pi 4+
- Proxmox LXC containers

---

## Security Note

**Default settings are for local/development use.**

For production deployment:
- Change database password in docker-compose.yml
- Set unique SECRET_KEY in backend configuration
- Configure firewall rules
- Set up automated backups

See DEPLOY.md for details.

---

## What's Next?

**Immediate:**
1. Explore the UI
2. Add some test items
3. Try semantic search vs keyword search
4. Review duplicate detection

**Short-term:**
Read QUICK_REFERENCE.md for daily workflows

**Long-term:**
Check ROADMAP.md to see what's coming next

---

**Current Version:** v1.5 (Foundation + AI Features - Testing)

**Ready? Start the system and open http://localhost:8080 🚀**
