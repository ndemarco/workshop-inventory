# Deployment Guide

Complete guide for deploying the Homelab Inventory System in various environments.

## Quick Start (Docker - Recommended)

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB RAM minimum
- 10GB disk space

### Steps

```bash
# 1. Clone repository
git clone <your-repo-url>
cd inventory-system

# 2. Copy environment template
cp .env.example .env

# 3. (Optional) Edit .env with your settings
nano .env

# 4. Start all services
docker-compose up -d

# 5. Wait for services to be ready (~30 seconds)
docker-compose logs -f backend

# 6. Open in browser
open http://localhost:8080
```

Done! The system is running.

## Deployment Options

### 1. VPS Deployment (Ubuntu 22.04)

#### Step 1: Prepare VPS
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### Step 2: Deploy Application
```bash
# Clone repository
git clone <your-repo-url>
cd inventory-system

# Configure environment
cp .env.example .env
nano .env  # Set production values

# Start services
docker-compose up -d

# Enable auto-start on boot
sudo systemctl enable docker
```

#### Step 3: Configure Firewall
```bash
# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8080/tcp  # If using non-standard port

# Enable firewall
sudo ufw enable
```

#### Step 4: Set up Reverse Proxy (Optional)

Using Nginx:
```bash
# Install Nginx
sudo apt install nginx

# Create config
sudo nano /etc/nginx/sites-available/inventory
```

```nginx
server {
    listen 80;
    server_name inventory.yourdomain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/inventory /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Set up SSL with Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d inventory.yourdomain.com
```

### 2. Proxmox Container Deployment

#### Option A: Docker in LXC Container

```bash
# Create Ubuntu LXC container in Proxmox
# Allocate: 2GB RAM, 20GB disk, 2 CPU cores

# In container, follow VPS deployment steps above
```

#### Option B: Native LXC Deployment

```bash
# Create container template
pct create 100 local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --hostname inventory \
  --memory 2048 \
  --cores 2 \
  --storage local-lvm \
  --rootfs 20

# Start and enter container
pct start 100
pct enter 100

# Follow VPS deployment steps
```

### 3. Jetson Nano Deployment (For AI/Voice Features)

#### Prerequisites
- Jetson Nano with JetPack 4.6+
- 4GB RAM model recommended
- External storage (SD card or SSD)

#### Step 1: Prepare Jetson
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker (pre-installed on JetPack)
# If not installed:
wget https://github.com/dusty-nv/jetson-containers/raw/master/install_docker.sh
bash install_docker.sh
```

#### Step 2: Deploy with GPU Support
```yaml
# docker-compose.jetson.yml
version: '3.8'

services:
  postgres:
    # ... same as main docker-compose.yml

  backend:
    build: ./backend
    runtime: nvidia  # Enable GPU
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - USE_GPU=true
      # ... other env vars
    volumes:
      - ./backend:/app
      - ai-models:/app/models
    ports:
      - "5000:5000"

volumes:
  ai-models:
```

```bash
# Deploy
docker-compose -f docker-compose.jetson.yml up -d
```

### 4. Raspberry Pi Deployment

#### For Pi 4 (4GB+)
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Use ARM-compatible images
# Modify docker-compose.yml:
# - Use postgres:14-alpine for ARM
# - Build backend from source

docker-compose up -d
```

#### For Pi 3/Zero (Limited)
```bash
# Install Python and PostgreSQL natively
sudo apt install python3 python3-pip postgresql

# Run without Docker
cd backend
pip3 install -r requirements.txt
python3 run.py
```

## Production Configuration

### Environment Variables

```bash
# .env file for production
DATABASE_URL=postgresql://inventoryuser:STRONG_PASSWORD@postgres:5432/inventory
POSTGRES_USER=inventoryuser
POSTGRES_PASSWORD=STRONG_PASSWORD  # Change this!
POSTGRES_DB=inventory

FLASK_ENV=production
SECRET_KEY=RANDOM_SECRET_KEY_HERE  # Generate with: openssl rand -hex 32
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Optional: Redis for caching
REDIS_URL=redis://redis:6379/0

# Optional: Email notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Security Hardening

#### 1. Change Default Passwords
```bash
# Generate strong password
openssl rand -base64 32

# Update .env file
nano .env
```

#### 2. Use SSL/TLS
```bash
# Option 1: Let's Encrypt (automatic)
docker run -it --rm -v /etc/letsencrypt:/etc/letsencrypt \
  certbot/certbot certonly --standalone \
  -d inventory.yourdomain.com

# Option 2: Self-signed (development)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/nginx-selfsigned.key \
  -out /etc/ssl/certs/nginx-selfsigned.crt
```

#### 3. Firewall Rules
```bash
# Allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

#### 4. Regular Backups
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=/backups
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
docker-compose exec -T postgres pg_dump -U inventoryuser inventory > \
  $BACKUP_DIR/inventory_$DATE.sql

# Compress
gzip $BACKUP_DIR/inventory_$DATE.sql

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
EOF

chmod +x backup.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /path/to/backup.sh") | crontab -
```

## Monitoring

### Health Checks

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f postgres

# Check resource usage
docker stats
```

### Set up Monitoring (Optional)

Using Prometheus + Grafana:
```yaml
# Add to docker-compose.yml
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana

volumes:
  prometheus-data:
  grafana-data:
```

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Check if ports are in use
sudo netstat -tulpn | grep -E '(5000|5432|8080)'

# Restart services
docker-compose restart

# Full reset (⚠️ destroys data)
docker-compose down -v
docker-compose up -d
```

### Database Connection Errors

```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Verify database exists
docker-compose exec postgres psql -U inventoryuser -l

# Reset database
docker-compose exec postgres psql -U inventoryuser -c "DROP DATABASE inventory;"
docker-compose exec postgres psql -U inventoryuser -c "CREATE DATABASE inventory;"
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Increase allocated resources in docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G

# Enable PostgreSQL query logging
docker-compose exec postgres psql -U inventoryuser inventory \
  -c "ALTER SYSTEM SET log_min_duration_statement = 1000;"
```

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3
    # ... rest of config

  nginx:
    # Load balancer
    depends_on:
      - backend
```

### Database Replication

```yaml
# Add read replica
  postgres-replica:
    image: postgres:14-alpine
    environment:
      - POSTGRES_PRIMARY_HOST=postgres
      - POSTGRES_REPLICATION_MODE=slave
```

## Updating

### Update Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose up -d --build

# Check migration needed
docker-compose exec backend flask db current
docker-compose exec backend flask db upgrade
```

### Database Migrations

```bash
# Backup first!
./backup.sh

# Run migration
docker-compose exec backend python migrate_to_simple_location.py

# Or use Flask-Migrate
docker-compose exec backend flask db upgrade
```

## Uninstalling

```bash
# Stop services
docker-compose down

# Remove data (⚠️ permanent)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Remove everything
docker system prune -a --volumes
```

---

## Support

For issues or questions:
1. Check troubleshooting section
2. Review logs: `docker-compose logs`
3. Check GitHub issues
4. Consult documentation

## Next Steps

After deployment:
1. Create your first module (storage unit)
2. Add levels (drawers/shelves) to modules
3. Generate locations (grid positions)
4. Start adding items!

See README.md for user guide and feature documentation.
