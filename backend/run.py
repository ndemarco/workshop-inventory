#!/usr/bin/env python3
"""
WhereTF? - Flask Application Runner
Phase 1: Foundation
"""

import os
from app import create_app
from app.models import db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Create all database tables
        db.create_all()
        print("Database tables created successfully!")
    
    # Run the application
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"\n{'='*60}")
    print("WhereTF? - Bin there, found that.")
    print(f"{'='*60}")
    print(f"Starting Flask server on http://0.0.0.0:{port}")
    print(f"Debug mode: {debug}")
    print(f"{'='*60}\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
