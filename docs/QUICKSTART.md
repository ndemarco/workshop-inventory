# Quick Deployment Guide

## Prerequisites Check

Before starting, ensure you have:
- [ ] Docker installed (`docker --version`)
- [ ] Docker Compose installed (`docker-compose --version`)
- [ ] At least 2GB free RAM
- [ ] At least 10GB free disk space
- [ ] Ports 8080, 5432, and 5000 available

## 5-Minute Deployment

### Step 1: Navigate to Project Directory
```bash
cd inventory-system
```

### Step 2: Start the System
```bash
docker-compose up -d
```

Wait for containers to start (usually 30-60 seconds).

### Step 3: Verify Deployment
```bash
docker-compose ps
```

You should see three containers running:
- `inventory-db` (postgres)
- `inventory-backend` (flask)
- `inventory-nginx` (nginx)

### Step 4: Access the Application

Open your web browser and go to:
```
http://localhost:8080
```

You should see the Inventory System dashboard!

## First-Time Setup

### 1. Create Your First Module

Click "Modules" → "Add Module"

Example:
- **Name**: Zeus
- **Description**: Main component storage cabinet
- **Physical Location**: North wall, workshop

Click "Create Module"

### 2. Add Levels to Your Module

Click on your module name → "Add Level"

Example:
- **Level Number**: 1
- **Name**: Top Drawer
- **Rows**: 4
- **Columns**: 6
- **Description**: Small components and fasteners

Click "Create Level"

This creates a 4×6 grid of locations (A1-A6, B1-B6, C1-C6, D1-D6)

### 3. Add Your First Item

Click "Items" → "Add Item"

Example:
- **Name**: M6 Bolts
- **Description**: Hex head bolt, M6 diameter, 50mm long, zinc plated, metric
- **Category**: Fasteners
- **Item Type**: solid
- **Quantity**: 100
- **Unit**: pieces
- **Tags**: bolt, metric, m6, hex, zinc
- **Location**: Zeus:1:A1

Click "Create Item"

### 4. Test Search

Click "Search" and type "M6" or "bolt"

You should see your item in the results!

## Common Tasks

### Viewing Storage Hierarchy

1. Click "Modules" to see all storage units
2. Click a module name to see its levels
3. Click a level to see the location grid
4. Click a location to see what's stored there

### Adding Items to Existing Locations

1. Click "Items" → "Add Item"
2. Fill in item details
3. Select location from dropdown
4. Submit

Or:

1. Find the item you want to update
2. Click "Edit" on the item page
3. Add a new location

### Searching for Items

1. Click "Search" in the navigation
2. Type keywords (name, description, tags)
3. View results with locations

### Editing Location Properties

1. Navigate to the location (Modules → Module → Level → Location)
2. Click "Edit"
3. Set location type (small_box, medium_bin, etc.)
4. Add dimensions if needed
5. Save

## Stopping the System

### Temporary Stop (keeps data)
```bash
docker-compose stop
```

### Start Again
```bash
docker-compose start
```

### Complete Shutdown (keeps data)
```bash
docker-compose down
```

### Nuclear Option (deletes ALL data)
```bash
docker-compose down -v
```

⚠️ **Warning**: The `-v` flag deletes the database volume. Only use if you want to start fresh!

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs backend

# Common issue: Port already in use
# Solution: Change port in docker-compose.yml or stop conflicting service
```

### Can't Connect to Database

```bash
# Check if PostgreSQL is healthy
docker-compose ps

# Restart PostgreSQL
docker-compose restart postgres

# Check PostgreSQL logs
docker-compose logs postgres
```

### Web UI Not Loading

```bash
# Check if nginx is running
docker-compose ps

# Check nginx logs
docker-compose logs nginx

# Restart nginx
docker-compose restart nginx
```

### Port 8080 Already in Use

Edit `docker-compose.yml` and change the nginx port:
```yaml
nginx:
  ports:
    - "8081:80"  # Changed from 8080 to 8081
```

Then restart:
```bash
docker-compose down
docker-compose up -d
```

## Accessing from Other Devices

To access from other computers on your network:

1. Find your server's IP address:
   ```bash
   hostname -I
   ```

2. On other devices, open browser to:
   ```
   http://YOUR_SERVER_IP:8080
   ```

Example: `http://192.168.1.100:8080`

## Backup Your Data

### Quick Backup
```bash
# Backup database
docker-compose exec postgres pg_dump -U inventoryuser inventory > backup.sql

# Backup everything
tar -czf inventory-backup-$(date +%Y%m%d).tar.gz data/
```

### Restore from Backup
```bash
# Restore database
docker-compose exec -T postgres psql -U inventoryuser inventory < backup.sql
```

## Performance Tips

### For Better Performance:

1. **Add more RAM** to Docker (Docker Desktop → Resources)
2. **Use SSD** for the data directory
3. **Limit concurrent users** (single-user recommended for Phase 1)

## Security Notes

⚠️ **Important for Production**:

1. Change default PostgreSQL password in `docker-compose.yml`
2. Set a secure SECRET_KEY in environment variables
3. Don't expose PostgreSQL port (5432) to the network
4. Use HTTPS with a reverse proxy
5. Set up regular backups

## Getting Help

If you encounter issues:

1. Check the logs: `docker-compose logs`
2. Verify all containers are running: `docker-compose ps`
3. Try restarting: `docker-compose restart`
4. Check the main README.md for detailed documentation
5. Open an issue on GitHub with error logs

## Next Steps

Once you're comfortable with the basics:

1. ✅ Add more modules for different storage areas
2. ✅ Organize items into categories
3. ✅ Use tags for better searchability
4. ✅ Set up location types for different bin sizes
5. ✅ Experiment with the grid layout for different storage configs

Enjoy your new inventory system! 🎉
