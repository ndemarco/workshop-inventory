from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON

db = SQLAlchemy()


class Module(db.Model):
    """Storage modules - the big units (cabinets, shelving units, etc.)"""
    __tablename__ = 'modules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    location_description = db.Column(db.String(200))  # Physical location in lab/shop
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    levels = db.relationship('Level', back_populates='module', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Module {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'location_description': self.location_description,
            'level_count': len(self.levels),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Level(db.Model):
    """Levels within modules - drawers, shelves, compartments"""
    __tablename__ = 'levels'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    level_number = db.Column(db.Integer, nullable=False)  # 1, 2, 3, etc.
    name = db.Column(db.String(100))  # Optional custom name
    rows = db.Column(db.Integer, default=1)  # Number of rows in grid
    columns = db.Column(db.Integer, default=1)  # Number of columns in grid
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    module = db.relationship('Module', back_populates='levels')
    locations = db.relationship('Location', back_populates='level', cascade='all, delete-orphan')
    
    # Unique constraint: one level number per module
    __table_args__ = (
        db.UniqueConstraint('module_id', 'level_number', name='unique_module_level'),
    )
    
    def __repr__(self):
        return f'<Level {self.module.name if self.module else "?"} - {self.level_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'module_id': self.module_id,
            'module_name': self.module.name if self.module else None,
            'level_number': self.level_number,
            'name': self.name,
            'rows': self.rows,
            'columns': self.columns,
            'description': self.description,
            'location_count': len(self.locations),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Location(db.Model):
    """Individual storage locations (bins) within levels"""
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    level_id = db.Column(db.Integer, db.ForeignKey('levels.id'), nullable=False)
    row = db.Column(db.String(10), nullable=False)  # A, B, C or 1, 2, 3
    column = db.Column(db.String(10), nullable=False)  # 1, 2, 3 or A, B, C
    
    # Location characteristics
    location_type = db.Column(db.String(50), default='general')  # small_box, medium_bin, large_bin, liquid_container, etc.
    width_mm = db.Column(db.Float)
    height_mm = db.Column(db.Float)
    depth_mm = db.Column(db.Float)
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    level = db.relationship('Level', back_populates='locations')
    item_locations = db.relationship('ItemLocation', back_populates='location', cascade='all, delete-orphan')
    
    # Unique constraint: one location per row/col in a level
    __table_args__ = (
        db.UniqueConstraint('level_id', 'row', 'column', name='unique_level_position'),
    )
    
    def __repr__(self):
        return f'<Location {self.full_address()}>'
    
    def full_address(self):
        """Returns full address like 'Zeus:3:B4'"""
        if self.level and self.level.module:
            return f"{self.level.module.name}:{self.level.level_number}:{self.row}{self.column}"
        return f"{self.row}{self.column}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'level_id': self.level_id,
            'module_name': self.level.module.name if self.level and self.level.module else None,
            'level_number': self.level.level_number if self.level else None,
            'row': self.row,
            'column': self.column,
            'full_address': self.full_address(),
            'location_type': self.location_type,
            'dimensions': {
                'width_mm': self.width_mm,
                'height_mm': self.height_mm,
                'depth_mm': self.depth_mm,
            } if self.width_mm or self.height_mm or self.depth_mm else None,
            'notes': self.notes,
            'item_count': len(self.item_locations),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Item(db.Model):
    """Inventory items"""
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)  # Natural language description
    category = db.Column(db.String(100))  # electronics, fasteners, tools, paints, etc.
    
    # Structured metadata (parsed from description or manually entered)
    item_metadata = db.Column(JSON)  # Flexible storage for specs, dimensions, etc.
    
    # Inventory tracking
    quantity = db.Column(db.Integer, default=1)
    unit = db.Column(db.String(20))  # pieces, meters, liters, etc.
    min_quantity = db.Column(db.Integer)  # For low stock alerts
    
    # Item characteristics
    item_type = db.Column(db.String(50))  # solid, liquid, smd_component, bulk, etc.
    notes = db.Column(db.Text)
    tags = db.Column(db.String(500))  # Comma-separated tags
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    item_locations = db.relationship('ItemLocation', back_populates='item', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Item {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'item_metadata': self.item_metadata,
            'quantity': self.quantity,
            'unit': self.unit,
            'min_quantity': self.min_quantity,
            'item_type': self.item_type,
            'notes': self.notes,
            'tags': self.tags.split(',') if self.tags else [],
            'locations': [il.to_dict() for il in self.item_locations],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class ItemLocation(db.Model):
    """Many-to-many relationship between items and locations"""
    __tablename__ = 'item_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)  # Quantity at this specific location
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    item = db.relationship('Item', back_populates='item_locations')
    location = db.relationship('Location', back_populates='item_locations')
    
    # Unique constraint: one item per location
    __table_args__ = (
        db.UniqueConstraint('item_id', 'location_id', name='unique_item_location'),
    )
    
    def __repr__(self):
        return f'<ItemLocation Item:{self.item_id} @ Location:{self.location_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'location_id': self.location_id,
            'quantity': self.quantity,
            'notes': self.notes,
            'location': self.location.to_dict() if self.location else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
