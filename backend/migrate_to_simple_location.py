"""
Migration: Simplify Item-Location Relationship
From: Many-to-Many (via item_locations table)
To: One-to-Many (location_id FK on items table)

Run this AFTER deploying the new models.py
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db

def migrate():
    """Migrate from old schema to new schema"""
    app = create_app()
    
    with app.app_context():
        print("Starting migration...")
        
        # Get database connection
        conn = db.engine.raw_connection()
        cursor = conn.cursor()
        
        try:
            # Step 1: Add new columns to items table
            print("Step 1: Adding new columns to items table...")
            try:
                cursor.execute("ALTER TABLE items ADD COLUMN location_id INTEGER REFERENCES locations(id)")
                cursor.execute("ALTER TABLE items ADD COLUMN quantity INTEGER DEFAULT 1")
                cursor.execute("ALTER TABLE items ADD COLUMN unit VARCHAR(20)")
                conn.commit()
                print("  ✓ Columns added")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                    print("  ✓ Columns already exist, skipping...")
                    conn.rollback()
                else:
                    raise
            
            # Step 2: Migrate data from item_locations to items
            print("Step 2: Migrating data from item_locations to items...")
            
            # Check if item_locations table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'item_locations'
                )
            """)
            table_exists = cursor.fetchone()[0]
            
            if table_exists:
                # Get all item-location relationships
                cursor.execute("""
                    SELECT item_id, location_id, quantity 
                    FROM item_locations
                    ORDER BY item_id, created_at
                """)
                relationships = cursor.fetchall()
                
                if relationships:
                    # For each item, take the FIRST location (since we can only have one now)
                    # Keep track of which items we've seen
                    seen_items = set()
                    migrated_count = 0
                    skipped_count = 0
                    
                    for item_id, location_id, quantity in relationships:
                        if item_id not in seen_items:
                            # First location for this item - migrate it
                            cursor.execute("""
                                UPDATE items 
                                SET location_id = %s, quantity = %s
                                WHERE id = %s
                            """, (location_id, quantity or 1, item_id))
                            seen_items.add(item_id)
                            migrated_count += 1
                        else:
                            # Item already has a location - skip additional locations
                            skipped_count += 1
                    
                    conn.commit()
                    print(f"  ✓ Migrated {migrated_count} item-location relationships")
                    if skipped_count > 0:
                        print(f"  ⚠ Skipped {skipped_count} duplicate locations (items can only have 1 location now)")
                else:
                    print("  ✓ No data to migrate")
                
                # Step 3: Drop old item_locations table
                print("Step 3: Dropping old item_locations table...")
                cursor.execute("DROP TABLE IF EXISTS item_locations CASCADE")
                conn.commit()
                print("  ✓ Old table dropped")
            else:
                print("  ✓ item_locations table doesn't exist, skipping migration...")
            
            print("\n✅ Migration completed successfully!")
            print("\nSummary:")
            print("  - Items now have location_id field")
            print("  - Each item can only be in one location")
            print("  - Old item_locations table has been removed")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

if __name__ == '__main__':
    migrate()
