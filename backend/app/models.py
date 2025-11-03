from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON
from pgvector.sqlalchemy import Vector

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


class Bin(db.Model):
    """Movable bins/containers that hold items"""
    __tablename__ = 'bins'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "Blue small bin", "Bin-042"

    # Physical properties
    width_mm = db.Column(db.Float)
    height_mm = db.Column(db.Float)
    depth_mm = db.Column(db.Float)

    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bin_locations = db.relationship('BinLocation', back_populates='bin', cascade='all, delete-orphan')
    items = db.relationship('Item', back_populates='bin')

    def __repr__(self):
        return f'<Bin {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'dimensions': {
                'width_mm': self.width_mm,
                'height_mm': self.height_mm,
                'depth_mm': self.depth_mm,
            } if self.width_mm or self.height_mm or self.depth_mm else None,
            'notes': self.notes,
            'locations': [bl.location.full_address() for bl in self.bin_locations],
            'item_count': len(self.items),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Item(db.Model):
    """Inventory items"""
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)  # AI-generated detailed description
    category = db.Column(db.String(100))  # electronics, fasteners, tools, paints, etc.

    # User's original input (stored for reference, analysis, future improvements)
    raw_input = db.Column(db.Text)  # User's original freeform description

    # AI/ML - Semantic search embedding (384 dimensions for sentence-transformers/all-MiniLM-L6-v2)
    embedding = db.Column(Vector(384))

    # Structured metadata (parsed from description or manually entered)
    item_metadata = db.Column(JSON)  # Flexible storage for specs, dimensions, etc.

    # Item characteristics
    item_type = db.Column(db.String(50))  # solid, liquid, smd_component, bulk, etc.
    notes = db.Column(db.Text)
    tags = db.Column(db.String(500))  # Comma-separated tags

    # Link to bin (optional - items can exist without being in a bin yet)
    bin_id = db.Column(db.Integer, db.ForeignKey('bins.id'), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bin = db.relationship('Bin', back_populates='items')
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
            'item_type': self.item_type,
            'notes': self.notes,
            'tags': self.tags.split(',') if self.tags else [],
            'bin': self.bin.to_dict() if self.bin else None,
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
            'notes': self.notes,
            'location': self.location.to_dict() if self.location else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class BinLocation(db.Model):
    """Many-to-many relationship between bins and locations - bins can span multiple location slots"""
    __tablename__ = 'bin_locations'

    id = db.Column(db.Integer, primary_key=True)
    bin_id = db.Column(db.Integer, db.ForeignKey('bins.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bin = db.relationship('Bin', back_populates='bin_locations')
    location = db.relationship('Location')

    # Unique constraint: one bin per location slot
    __table_args__ = (
        db.UniqueConstraint('bin_id', 'location_id', name='unique_bin_location'),
    )

    def __repr__(self):
        return f'<BinLocation Bin:{self.bin_id} @ Location:{self.location_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'bin_id': self.bin_id,
            'location_id': self.location_id,
            'notes': self.notes,
            'location': self.location.to_dict() if self.location else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class DuplicateCandidate(db.Model):
    """Tracks potential duplicate items for offline resolution"""
    __tablename__ = 'duplicate_candidates'

    id = db.Column(db.Integer, primary_key=True)
    item1_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    item2_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    similarity_score = db.Column(db.Float, nullable=False)  # Cosine similarity 0.0-1.0
    status = db.Column(db.String(20), default='pending')  # pending, merged, dismissed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

    # Relationships
    item1 = db.relationship('Item', foreign_keys=[item1_id])
    item2 = db.relationship('Item', foreign_keys=[item2_id])

    # Unique constraint: don't create duplicate pairs
    __table_args__ = (
        db.UniqueConstraint('item1_id', 'item2_id', name='unique_duplicate_pair'),
    )

    def __repr__(self):
        return f'<DuplicateCandidate Item:{self.item1_id} <-> Item:{self.item2_id} ({self.similarity_score:.2f})>'

    def to_dict(self):
        return {
            'id': self.id,
            'item1': self.item1.to_dict() if self.item1 else None,
            'item2': self.item2.to_dict() if self.item2 else None,
            'similarity_score': self.similarity_score,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
        }
