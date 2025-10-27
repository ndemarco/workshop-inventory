from flask import Blueprint, render_template, jsonify
from app.models import Module, Level, Location, Item
from sqlalchemy.orm import joinedload

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Main dashboard"""
    stats = {
        'modules': Module.query.count(),
        'levels': Level.query.count(),
        'locations': Location.query.count(),
        'items': Item.query.count(),
    }

    recent_items = Item.query.order_by(Item.created_at.desc()).limit(10).all()
    modules = Module.query.order_by(Module.name).all()

    return render_template('index.html', stats=stats, recent_items=recent_items, modules=modules)


@bp.route('/api/dashboard/stats')
def dashboard_stats():
    """
    Enhanced statistics API for dashboard
    Returns:
    - Total modules, levels, locations
    - Overall occupancy (occupied/total locations)
    - Per-module statistics with occupied/free locations
    - Per-level statistics within each module
    """
    # Get all modules with eager-loaded relationships for efficiency
    modules = Module.query.options(
        joinedload(Module.levels).joinedload(Level.locations).joinedload(Location.items)
    ).order_by(Module.name).all()

    # Calculate overall statistics
    total_locations = Location.query.count()
    occupied_locations = Location.query.join(Item).filter(Item.location_id == Location.id).count()

    occupancy_percentage = round((occupied_locations / total_locations * 100), 1) if total_locations > 0 else 0

    # Build module statistics
    modules_data = []
    for module in modules:
        # Calculate module-level statistics
        module_total_locations = 0
        module_occupied_locations = 0

        levels_data = []
        for level in module.levels:
            level_total = len(level.locations)
            level_occupied = sum(1 for loc in level.locations if loc.items)

            module_total_locations += level_total
            module_occupied_locations += level_occupied

            levels_data.append({
                'id': level.id,
                'level_number': level.level_number,
                'name': level.name or f"Level {level.level_number}",
                'rows': level.rows,
                'columns': level.columns,
                'total': level_total,
                'occupied': level_occupied,
                'free': level_total - level_occupied,
                'occupancy_pct': round((level_occupied / level_total * 100), 1) if level_total > 0 else 0
            })

        module_occupancy_pct = round((module_occupied_locations / module_total_locations * 100), 1) if module_total_locations > 0 else 0

        modules_data.append({
            'id': module.id,
            'name': module.name,
            'description': module.description,
            'location_description': module.location_description,
            'total': module_total_locations,
            'occupied': module_occupied_locations,
            'free': module_total_locations - module_occupied_locations,
            'occupancy_pct': module_occupancy_pct,
            'levels': levels_data
        })

    return jsonify({
        'overall': {
            'modules': len(modules),
            'levels': Level.query.count(),
            'locations': total_locations,
            'items': Item.query.count(),
            'occupied': occupied_locations,
            'free': total_locations - occupied_locations,
            'occupancy_pct': occupancy_percentage
        },
        'modules': modules_data
    })


@bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')
