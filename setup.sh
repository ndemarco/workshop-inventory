#!/bin/bash
# Quick Setup Script for Homelab Inventory System
# This script automates the initial setup process

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Homelab Inventory System - Quick Setup                ║"
echo "║                                                            ║"
echo "║     Phase 1: Enhanced UI with Alpine.js                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi
echo "✅ Docker found: $(docker --version)"

# Check Docker Compose
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed or is an old version."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi
echo "✅ Docker Compose found: $(docker compose version)"

echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    
    # Generate random secret key
    if command -v openssl &> /dev/null; then
        SECRET_KEY=$(openssl rand -hex 32)
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/change-this-to-a-random-secret-key-in-production/$SECRET_KEY/" .env
        else
            # Linux
            sed -i "s/change-this-to-a-random-secret-key-in-production/$SECRET_KEY/" .env
        fi
        echo "✅ Generated random SECRET_KEY"
    else
        echo "⚠️  Could not generate random SECRET_KEY (openssl not found)"
        echo "   Please edit .env and set SECRET_KEY manually"
    fi
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🏗️  Building and starting services..."
echo "   This may take a few minutes on first run..."
echo ""

# Pull and build images
docker compose pull
docker compose build

# Start services
docker compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."

# Wait for PostgreSQL to be ready
MAX_RETRIES=30
RETRY_COUNT=0
while ! docker compose exec -T postgres pg_isready -U inventoryuser > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -gt $MAX_RETRIES ]; then
        echo "❌ PostgreSQL did not start in time"
        echo "   Check logs: docker compose logs postgres"
        exit 1
    fi
    echo "   Waiting for PostgreSQL... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

echo "✅ PostgreSQL is ready"

# Wait for backend to be ready
sleep 5
if docker compose ps | grep -q "backend.*running"; then
    echo "✅ Backend is ready"
else
    echo "⚠️  Backend may not be running correctly"
    echo "   Check logs: docker compose logs backend"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    🎉 Setup Complete!                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Service Status:"
docker compose ps
echo ""
echo "🌐 Access the application:"
echo "   URL: http://localhost:8080"
echo ""
echo "📝 Useful Commands:"
echo "   View logs:        docker compose logs -f"
echo "   Stop services:    docker compose stop"
echo "   Start services:   docker compose start"
echo "   Restart:          docker compose restart"
echo "   Shutdown:         docker compose down"
echo "   Full reset:       docker compose down -v"
echo ""
echo "📚 Documentation:"
echo "   README.md       - User guide and features"
echo "   DEPLOYMENT.md   - Advanced deployment options"
echo "   CONTRIBUTING.md - Development guidelines"
echo ""
echo "🚀 Next Steps:"
echo "   1. Open http://localhost:8080 in your browser"
echo "   2. Create your first storage module"
echo "   3. Add levels (drawers/shelves) to the module"
echo "   4. Add items to locations"
echo ""
echo "💾 Database Backup:"
echo "   docker compose exec -T postgres pg_dump -U inventoryuser inventory > backup.sql"
echo ""
echo "Happy organizing! 📦"
