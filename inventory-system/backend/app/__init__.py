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
    from app.routes import main, items, locations, modules, search
    app.register_blueprint(main.bp)
    app.register_blueprint(items.bp, url_prefix='/items')
    app.register_blueprint(locations.bp, url_prefix='/locations')
    app.register_blueprint(modules.bp, url_prefix='/modules')
    app.register_blueprint(search.bp, url_prefix='/search')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
