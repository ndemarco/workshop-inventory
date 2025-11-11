# 🧹 TidyLab

A modern, comprehensive inventory management system designed for homelabs, makerspaces, and workshops. Track thousands of items across organized storage modules with advanced search, QR code integration, and intelligent duplicate detection.

[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)
[![React](https://img.shields.io/badge/React-18.2.0-blue)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)](https://www.postgresql.org/)

---

**This is a rebranded fork of [Wheretf](https://github.com/ndemarco/wheretf) by [ndemarco](https://github.com/ndemarco). Rebranded and maintained by Ruben Costa.**

---

## ✨ Features

### 🏗️ Storage Management
- **Hierarchical Organization**: Modules → Levels → Locations for structured storage
- **Visual Location Grid**: Interactive grid view for easy location management
- **Color-Coded Locations**: Assign colors to locations for quick identification

### 📦 Item Management
- **Full CRUD Operations**: Create, read, update, and delete items with ease
- **Quantity Tracking**: Real-time quantity management with increment/decrement buttons
- **Categories & Tags**: Organize items with categories and flexible tagging system
- **Specifications**: Store detailed specifications for technical items

### 🔍 Search & Discovery
- **Advanced Search**: Search by name, description, tags, and categories
- **Filtering**: Filter items by category, location, or custom criteria
- **Pagination**: Efficient browsing with 9-item pagination on mobile/desktop

### 📱 QR Code Integration
- **QR Code Generation**: Automatically generate QR codes for items
- **QR Code Scanning**: Scan QR codes to quickly access item details
- **Visual QR Display**: View QR codes directly in the item detail page
- **Download QR Codes**: Export QR codes as PNG files

### 🧠 Intelligent Features
- **Duplicate Detection**: Real-time duplicate prevention with similarity scoring
- **Smart Suggestions**: AI-powered location suggestions for new items
- **Pattern Recognition**: Automatic categorization for fasteners and electronics
- **Specification Extraction**: Intelligent parsing of item specifications

### 🎨 User Interface
- **Responsive Design**: Fully optimized for mobile and desktop
- **Modern UI**: Built with React 18, Tailwind CSS, and Vite
- **Touch-Friendly**: Mobile-optimized buttons and interactions
- **Dark/Light Themes**: Coming in future updates

### 🚀 Deployment
- **Docker Ready**: One-command deployment with Docker Compose
- **PostgreSQL Backend**: Robust database with proper relationships
- **Nginx Proxy**: Production-ready reverse proxy setup
- **API Documentation**: Auto-generated OpenAPI specification

## � Screenshots

### Dashboard Overview
![Dashboard](screenshots/dashboard.png)
*Main dashboard showing recent items and statistics*

### Items Management
![Items List](screenshots/items-list.png)
*Items page with search, filtering, and pagination*

### Item Details with QR Code
![Item Detail](screenshots/item-detail.png)
*Detailed item view with QR code display and quantity controls*

### QR Code Scanning
![QR Scanner](screenshots/qr-scanner.png)
*Mobile QR code scanner for quick item access*

### Location Grid View
![Location Grid](screenshots/location-grid.png)
*Visual grid representation of storage locations*

### Mobile Responsive Design
![Mobile View](screenshots/mobile-view.png)
*Responsive design optimized for mobile devices*

> **Note**: Screenshots are placeholders. To add real screenshots:
> 1. Take screenshots of your running application
> 2. Save them in a `screenshots/` folder in the repo root
> 3. Replace the placeholder paths above with actual image paths

## �🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rubencosta13/tidylab.git
   cd tidylab
   ```

2. **Start the application:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Web UI: http://localhost:8080
   - API: http://localhost:5000/api
   - Database: localhost:5432

### Development Setup

#### Backend (Flask + PostgreSQL)
```bash
cd api
pip install -r requirements.txt
export DATABASE_URL="postgresql://inventoryuser:inventorypass@localhost:5432/inventory"
flask run
```

#### Frontend (React + Vite)
```bash
cd ui
npm install
npm run dev
```

## 📖 Usage

### Managing Items
1. **Add Items**: Click "New Item" to create items with name, description, category, quantity, and tags
2. **Edit Items**: Click the edit button on any item to modify details
3. **Quantity Management**: Use +/- buttons on item details to adjust quantities
4. **QR Codes**: Generate and download QR codes for quick access

### Organizing Storage
1. **Create Modules**: Add storage modules (cabinets, shelves, etc.)
2. **Define Levels**: Organize modules into levels (shelves, drawers)
3. **Set Locations**: Create specific storage locations with coordinates

### Searching & Filtering
- Use the search bar to find items by name, description, or tags
- Filter by category using the category buttons
- Browse paginated results (9 items per page)

### QR Code Workflow
1. **Generate**: Create QR codes for items from the Items page
2. **Scan**: Use the QR Scanner page to scan codes and view items
3. **Display**: View QR codes visually on the Item Detail page

## 🔧 API Documentation

TidyLab provides a RESTful API with comprehensive documentation:

- **Base URL**: `http://localhost:5000/api`
- **OpenAPI Spec**: Available at `/api/openapi.json`
- **Interactive Docs**: View API documentation in your browser

### Key Endpoints

#### Items
- `GET /api/items` - List items with filtering
- `POST /api/items` - Create new item
- `PUT /api/items/{id}` - Update item
- `DELETE /api/items/{id}` - Delete item
- `POST /api/items/{id}/qr/generate` - Generate QR code

#### Locations
- `GET /api/locations` - List locations
- `POST /api/locations` - Create location
- `PUT /api/locations/{id}` - Update location

#### Modules & Levels
- `GET /api/modules` - List modules
- `POST /api/modules` - Create module
- `GET /api/modules/{id}/levels` - Get levels in module

## 🏗️ Architecture

```
TidyLab/
├── api/                 # Flask backend
│   ├── app/            # Application code
│   ├── scripts/        # Utility scripts
│   └── requirements.txt
├── ui/                 # React frontend
│   ├── src/           # Source code
│   ├── public/        # Static assets
│   └── package.json
├── nginx/             # Reverse proxy config
├── docker-compose.yml # Docker orchestration
└── README.md
```

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow conventional commit format
- Write tests for new features
- Update documentation as needed
- Ensure mobile responsiveness

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Credits

- **Original Project**: [Wheretf](https://github.com/ndemarco/wheretf) by [ndemarco](https://github.com/ndemarco)
- **Rebranded & Maintained by**: Ruben Costa
- **Technologies**: React, Flask, PostgreSQL, Docker, Tailwind CSS

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/rubencosta13/tidylab/issues)
- **Discussions**: [GitHub Discussions](https://github.com/rubencosta13/tidylab/discussions)

---

*Keep your workspace tidy with TidyLab! 🧹*

### Specification Extraction
- **One-click extraction**: Click "✨ Extract Specs" to auto-parse descriptions
- **Pattern recognition** for:
  - **Fasteners**: M6x50, #8 x 3/4", hex head, phillips, pan head, etc.
  - **Resistors**: 1kΩ, 4.7MΩ, 10Ω with tolerance and wattage
  - **Capacitors**: 0.1μF, 100nF, 220μF with voltage and type
  - **IC Packages**: 0805, 1206, SOT-23, SOIC, DIP
  - **Materials**: stainless steel, brass, aluminum, plastic
  - **Dimensions**: 100x50x30mm, measurements
- **Auto-populate**: Automatically fills category and tags based on detected specs
- **Confidence scoring**: Shows how confident the parser is about the extraction

### Supported Formats
```
Fasteners:
  - M6, M8x50 (metric threads)
  - #8, #10 x 3/4 (imperial screws)
  - Pan head, hex head, socket head
  - Phillips, flathead, hex, torx drives

Electronics:
  - 1kΩ, 4.7MΩ, 10Ω (resistors)
  - 0.1μF, 100nF, 10pF (capacitors)
  - 0805, 1206, SOT-23 (SMD packages)

Measurements:
  - 10mm, 5.5cm (metric length)
  - 1/4 inch, 3/4" (imperial)
  - 100g, 1.5kg (weight)
  - 100x50x30mm (dimensions)
```

### How It Works
1. When creating a new item, fill in name and description
2. System automatically checks for duplicates (70% similarity threshold)
3. If found, you'll see a warning with similar items
4. Review the matches and their locations
5. Either:
   - Update the existing item's quantity instead, or
   - Check "proceed anyway" to create a new item
6. Use "Extract Specs" to automatically fill tags and category

## 📋 Prerequisites

- Docker and Docker Compose
- Git (for cloning)
- 2GB RAM minimum
- 10GB disk space

## 🏃 Quick Start

### 1. Clone or Extract the Project

If you have the project as files:
```bash
cd inventory-system
```

### 2. Start the System

```bash
docker-compose up -d
```

This will:
- Start PostgreSQL database
- Build and start the Flask backend
- Start nginx reverse proxy

### 3. Access the Application

Open your browser and navigate to:
```
http://localhost:8080
```

### 4. Stop the System

```bash
docker-compose down
```

To stop and remove all data:
```bash
docker-compose down -v
```

## 📚 Usage Guide

### First Steps

1. **Create a Module**: A module is a storage unit (cabinet, shelving unit, etc.)
   - Navigate to "Modules" → "Add Module"
   - Example: Name it "Zeus" or "Main Workbench"

2. **Add Levels**: Levels are drawers, shelves, or compartments within a module
   - View your module → "Add Level"
   - Specify grid dimensions (rows × columns)
   - Example: 4 rows × 6 columns creates locations A1-A6, B1-B6, etc.

3. **Add Items**: Store your inventory items
   - Navigate to "Items" → "Add Item"
   - Provide a natural language description
   - Optionally assign a storage location
   - Example: "Pan head phillips screw, 3/4 inch long, #8, mild steel"

4. **Search**: Find items quickly
   - Use the search bar to find items by name, description, or tags
   - View item locations on the results page

### Storage Hierarchy

```
Module (e.g., "Zeus", "Muse")
├── Level 1 (e.g., drawer, shelf)
│   ├── Location A1
│   ├── Location A2
│   └── ...
├── Level 2
│   ├── Location A1
│   └── ...
└── ...
```

### Example: Adding a Screw

1. Go to "Items" → "Add Item"
2. Fill in:
   - **Name**: "Phillips Pan Head #8 Screw"
   - **Description**: "Pan head phillips screw, 3/4 inch long, #8 diameter, mild steel"
   - **Category**: "Fasteners"
   - **Item Type**: "solid"
   - **Quantity**: "100"
   - **Unit**: "pieces"
   - **Tags**: "screw, phillips, pan head, #8, fastener"
   - **Location**: "Muse:4:A3" (Module: Muse, Level: 4, Location: A3)
3. Click "Create Item"

### Location Types

The system supports different location types for various storage needs:

- **general**: Standard bins
- **small_box**: For tiny components (SMD parts, small hardware)
- **medium_bin**: Standard drawer compartments
- **large_bin**: Bulk storage
- **liquid_container**: For paints, solvents, coatings
- **smd_container**: Specialized for surface-mount components

## 🗂️ Database Schema

```
modules
├── id
├── name (unique)
├── description
└── location_description

levels
├── id
├── module_id → modules.id
├── level_number
├── rows
└── columns

locations
├── id
├── level_id → levels.id
├── row
├── column
├── location_type
└── dimensions (width, height, depth)

items
├── id
├── name
├── description
├── category
├── quantity
├── metadata (JSON)
└── tags

item_locations (many-to-many)
├── item_id → items.id
├── location_id → locations.id
└── quantity
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql://inventoryuser:inventorypass@postgres:5432/inventory

# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Port
PORT=5000
```

### Changing Ports

Edit `docker-compose.yml`:

```yaml
services:
  nginx:
    ports:
      - "8080:80"  # Change 8080 to your preferred port
```

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps

# View PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Application Won't Start

```bash
# View backend logs
docker-compose logs backend

# Rebuild containers
docker-compose up --build

# Reset everything
docker-compose down -v
docker-compose up --build
```

### Port Already in Use

If port 8080 is in use:

```bash
# Find what's using the port
lsof -i :8080

# Or change the port in docker-compose.yml
```

## 📊 API Endpoints

The system provides REST API endpoints for programmatic access:

### Modules
- `GET /modules/api/modules` - List all modules
- `GET /modules/api/modules/<id>` - Get module details
- `GET /modules/api/modules/<id>/levels` - List module levels

### Locations
- `GET /locations/api/locations` - List locations (with filters)
- `GET /locations/api/locations/<id>` - Get location details

### Items
- `GET /items/api/items` - List items (with search)
- `GET /items/api/items/<id>` - Get item details

### Search
- `GET /search/api?q=query` - Search items

Example:
```bash
curl http://localhost:8080/items/api/items?search=screw
```

## 🚢 Deployment Options

### Option 1: Local VPS/Server
```bash
# Clone and run
git clone <your-repo>
cd inventory-system
docker-compose up -d
```

### Option 2: Proxmox Container
1. Create an LXC container (Ubuntu 22.04+)
2. Install Docker and Docker Compose
3. Clone and run as above

### Option 3: Jetson Nano
1. Install Docker on Jetson
2. Clone the repository
3. Run with docker-compose

### Production Considerations

For production deployment:

1. **Change default passwords** in `docker-compose.yml`
2. **Set a secure SECRET_KEY** in environment variables
3. **Enable HTTPS** with Let's Encrypt
4. **Set up backups** for the PostgreSQL data volume
5. **Configure firewall rules**
6. **Use production WSGI server** (Gunicorn instead of Flask dev server)

## 💾 Backup and Restore

### Backup Database

```bash
docker-compose exec postgres pg_dump -U inventoryuser inventory > backup.sql
```

### Restore Database

```bash
docker-compose exec -T postgres psql -U inventoryuser inventory < backup.sql
```

### Backup Data Directory

```bash
tar -czf backup-$(date +%Y%m%d).tar.gz data/
```

## 🛠️ Development

### Running Without Docker

```bash
# Install PostgreSQL locally
# Create database 'inventory'

# Install Python dependencies
cd backend
pip install -r requirements.txt

# Set environment variable
export DATABASE_URL="postgresql://user:pass@localhost:5432/inventory"

# Run application
python run.py
```

Access at http://localhost:5000

### Project Structure

```
inventory-system/
├── backend/
│   ├── app/
│   │   ├── models.py          # Database models
│   │   ├── routes/            # Route handlers
│   │   │   ├── main.py
│   │   │   ├── items.py
│   │   │   ├── modules.py
│   │   │   ├── locations.py
│   │   │   └── search.py
│   │   └── __init__.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── run.py
├── frontend/
│   ├── templates/             # Jinja2 templates
│   └── static/
│       ├── css/
│       └── js/
├── docker-compose.yml
├── nginx.conf
└── README.md
```

## 📖 Next Steps

After getting comfortable with Phase 1:

1. Add your first 50-100 items
2. Organize them into modules and levels
3. Test the search functionality
4. Provide feedback on what features you need most

## 🐛 Known Limitations

- No AI-powered semantic search yet (coming in Phase 4)
- No CLI or voice interface (coming in Phases 5-6)
- No automatic item merging (duplicates are detected but not auto-merged)
- Basic keyword search only (semantic search in Phase 4)
- No user authentication (single-user system for now)

## 🤝 Support

For issues, questions, or feature requests, please open an issue in the project repository.

## 📝 License

[Your License Here]

## 🎯 Roadmap

- [x] Phase 1: Foundation ✅
- [x] Phase 2: Smart Location Management ✅
- [x] Phase 3: Duplicate Detection ✅
- [ ] Phase 4: Semantic Search
- [ ] Phase 5: CLI Interface
- [ ] Phase 6: Voice Interface
- [ ] Phase 7: Advanced AI Features
- [ ] Phase 8: Production Polish

---

**Version**: 3.0.0 (Phases 1-3 Complete)  
**Last Updated**: November 2025
