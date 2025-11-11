import os
from flask import Flask, jsonify, send_from_directory
from flask_migrate import Migrate
from flask_cors import CORS
from app.models import db


def create_app():
    app = Flask(__name__)
    
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
    
    # Enable CORS - allow everything
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=False)

    # Serve generated OpenAPI JSON (development tool)
    @app.route('/api/openapi.json')
    def serve_openapi():
        # static folder is located at project_root/api/static
        static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
        filename = 'openapi.json'
        file_path = os.path.join(static_dir, filename)
        if os.path.exists(file_path):
            return send_from_directory(static_dir, filename)
        return jsonify({'error': 'OpenAPI spec not generated'}), 404

    
    # Register blueprints
    from app.routes import main, items, locations, modules, search
    app.register_blueprint(main.bp, url_prefix='/api')
    app.register_blueprint(items.bp, url_prefix='/api/items')
    app.register_blueprint(locations.bp, url_prefix='/api/locations')
    app.register_blueprint(modules.bp, url_prefix='/api/modules')
    app.register_blueprint(search.bp, url_prefix='/api/search')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
