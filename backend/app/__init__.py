import os
from flask import Flask
from flask_migrate import Migrate
from app.models import db


def create_app():
    app = Flask(__name__, 
                template_folder='../frontend/templates',
                static_folder='../frontend/static')
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 
        'postgresql://inventoryuser:inventorypass@localhost:5432/inventory'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Register blueprints
    from app.routes import main, items, locations, modules, search, duplicates, admin
    app.register_blueprint(main.bp)
    app.register_blueprint(items.bp, url_prefix='/items')
    app.register_blueprint(locations.bp, url_prefix='/locations')
    app.register_blueprint(modules.bp, url_prefix='/modules')
    app.register_blueprint(search.bp, url_prefix='/search')
    app.register_blueprint(duplicates.bp)
    app.register_blueprint(admin.bp)

    # Context processor for footer stats
    @app.context_processor
    def inject_stats():
        from app.models import Item, Location, ItemLocation
        from sqlalchemy import func

        # Exclude soft-deleted items from stats
        total_items = Item.active_query().count()
        total_locations = Location.query.count()

        # Calculate occupied locations (locations with at least one active item)
        occupied_locations = Location.query.join(ItemLocation).join(Item).filter(Item.deleted_at.is_(None)).distinct().count()

        # Calculate occupancy percentage
        occupancy_percent = (occupied_locations / total_locations * 100) if total_locations > 0 else 0

        return dict(
            stats={
                'total_items': total_items,
                'total_locations': total_locations,
                'occupied_locations': occupied_locations,
                'occupancy_percent': round(occupancy_percent, 1),
            }
        )

    # Create tables
    with app.app_context():
        db.create_all()

    return app
