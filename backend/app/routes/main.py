from flask import Blueprint, render_template
from app.models import Module, Level, Location, Item

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Main dashboard - Google-style search homepage"""
    # Exclude soft-deleted items
    total_items = Item.active_query().count()
    total_locations = Location.query.count()

    # Calculate occupied locations (locations with at least one active item)
    from sqlalchemy import func
    from app.models import ItemLocation
    occupied_locations = Location.query.join(ItemLocation).join(Item).filter(Item.deleted_at.is_(None)).distinct().count()

    # Calculate occupancy percentage
    occupancy_percent = (occupied_locations / total_locations * 100) if total_locations > 0 else 0

    stats = {
        'total_items': total_items,
        'total_locations': total_locations,
        'occupied_locations': occupied_locations,
        'occupancy_percent': round(occupancy_percent, 1),
    }

    return render_template('index.html', stats=stats)


@bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')
