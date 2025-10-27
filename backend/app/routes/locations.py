from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import db, Location, Level, Item, Module
from sqlalchemy.orm import joinedload

bp = Blueprint('locations', __name__)


@bp.route('/')
def list_locations():
    """List all locations"""
    # Get filter parameters
    module_id = request.args.get('module_id', type=int)
    level_id = request.args.get('level_id', type=int)
    location_type = request.args.get('location_type')
    occupied = request.args.get('occupied')  # 'yes', 'no', or None
    
    query = Location.query.join(Level)
    
    if level_id:
        query = query.filter(Location.level_id == level_id)
    elif module_id:
        query = query.filter(Level.module_id == module_id)
    
    if location_type:
        query = query.filter(Location.location_type == location_type)
    
    if occupied == 'yes':
        query = query.join(Item).distinct()
    elif occupied == 'no':
        query = query.outerjoin(Item).filter(Item.id == None)
    
    locations = query.order_by(Level.module_id, Level.level_number, Location.row, Location.column).all()
    
    # Get unique location types for filter dropdown
    location_types = db.session.query(Location.location_type).distinct().all()
    location_types = [lt[0] for lt in location_types if lt[0]]
    
    return render_template('locations/list.html', 
                         locations=locations, 
                         location_types=location_types)


@bp.route('/<int:location_id>')
def view_location(location_id):
    """View location details and item stored there"""
    location = Location.query.get_or_404(location_id)
    # Get the item stored at this location (if any)
    item = Item.query.filter_by(location_id=location_id).first()
    
    return render_template('locations/view.html', 
                         location=location, 
                         item=item)


@bp.route('/<int:location_id>/edit', methods=['GET', 'POST'])
def edit_location(location_id):
    """Edit location properties"""
    location = Location.query.get_or_404(location_id)
    
    if request.method == 'POST':
        location.location_type = request.form.get('location_type', 'general')
        location.width_mm = request.form.get('width_mm', type=float)
        location.height_mm = request.form.get('height_mm', type=float)
        location.depth_mm = request.form.get('depth_mm', type=float)
        location.notes = request.form.get('notes')
        
        db.session.commit()
        
        flash(f'Location {location.full_address()} updated successfully', 'success')
        return redirect(url_for('locations.view_location', location_id=location.id))
    
    return render_template('locations/form.html', location=location)


# API endpoints

@bp.route('/api/locations', methods=['GET'])
def api_list_locations():
    """API endpoint to list locations with filters"""
    level_id = request.args.get('level_id', type=int)
    location_type = request.args.get('location_type')
    available = request.args.get('available', type=bool)
    
    query = Location.query
    
    if level_id:
        query = query.filter(Location.level_id == level_id)
    
    if location_type:
        query = query.filter(Location.location_type == location_type)
    
    if available:
        # Only return locations with no items
        query = query.outerjoin(Item).filter(Item.id == None)
    
    locations = query.all()
    return jsonify([l.to_dict() for l in locations])


@bp.route('/api/locations/<int:location_id>', methods=['GET'])
def api_get_location(location_id):
    """API endpoint to get a single location"""
    location = Location.query.get_or_404(location_id)
    return jsonify(location.to_dict())


@bp.route('/api/locations/<int:location_id>/detail', methods=['GET'])
def location_detail(location_id):
    """
    Location detail API for drill-down view
    Returns:
    - Full location information (address, dimensions, type)
    - Item in location (if any) with all metadata
    - Breadcrumb context (module → level → location)
    - Adjacent locations (same level, nearby rows/columns)
    """
    # Get location with all relationships eager-loaded
    location = Location.query.options(
        joinedload(Location.level).joinedload(Level.module),
        joinedload(Location.items)
    ).get_or_404(location_id)

    # Build breadcrumb
    breadcrumb = "Unknown location"
    module_name = None
    level_name = None

    if location.level:
        level = location.level
        level_name = level.name or f"Level {level.level_number}"

        if level.module:
            module = level.module
            module_name = module.name
            breadcrumb = f"{module_name} → {level_name} → {location.row}{location.column}"

    # Get the item in this location (if any)
    item_data = None
    if location.items:
        item = location.items[0]  # One location = one item max
        item_data = {
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'category': item.category,
            'item_type': item.item_type,
            'item_metadata': item.item_metadata,
            'notes': item.notes,
            'tags': item.tags.split(',') if item.tags else [],
            'created_at': item.created_at.isoformat() if item.created_at else None,
            'updated_at': item.updated_at.isoformat() if item.updated_at else None
        }

    # Calculate adjacent locations (same level, nearby rows/columns)
    adjacent_locations = []
    if location.level:
        # Get all locations in the same level
        all_locations = Location.query.filter_by(level_id=location.level_id).all()

        # Create a map of (row, col) -> location for quick lookup
        location_map = {(loc.row, loc.column): loc for loc in all_locations}

        # Define row letter to number conversion for adjacency calculation
        def row_to_num(row):
            """Convert row letter/number to numeric value for comparison"""
            if row.isdigit():
                return int(row)
            else:
                # Assume alphabetic: A=1, B=2, etc.
                return ord(row.upper()) - ord('A') + 1

        def num_to_row(num, reference_row):
            """Convert numeric value back to row format (letter or number)"""
            if reference_row.isdigit():
                return str(num)
            else:
                # Convert back to letter
                return chr(ord('A') + num - 1)

        def col_to_num(col):
            """Convert column to numeric value"""
            return int(col) if col.isdigit() else ord(col.upper()) - ord('A') + 1

        def num_to_col(num, reference_col):
            """Convert numeric value back to column format"""
            if reference_col.isdigit():
                return str(num)
            else:
                return chr(ord('A') + num - 1)

        # Get current position
        current_row_num = row_to_num(location.row)
        current_col_num = col_to_num(location.column)

        # Check all 8 adjacent positions (N, NE, E, SE, S, SW, W, NW)
        offsets = [
            (-1, 0),  # North
            (-1, 1),  # Northeast
            (0, 1),   # East
            (1, 1),   # Southeast
            (1, 0),   # South
            (1, -1),  # Southwest
            (0, -1),  # West
            (-1, -1)  # Northwest
        ]

        for row_offset, col_offset in offsets:
            adj_row_num = current_row_num + row_offset
            adj_col_num = current_col_num + col_offset

            # Skip if out of bounds
            if adj_row_num < 1 or adj_col_num < 1:
                continue

            # Convert back to row/col format
            try:
                adj_row = num_to_row(adj_row_num, location.row)
                adj_col = num_to_col(adj_col_num, location.column)

                # Check if this location exists
                if (adj_row, adj_col) in location_map:
                    adj_location = location_map[(adj_row, adj_col)]
                    adjacent_locations.append({
                        'id': adj_location.id,
                        'address': f"{adj_row}{adj_col}",
                        'full_address': adj_location.full_address(),
                        'is_occupied': bool(adj_location.items),
                        'item_name': adj_location.items[0].name if adj_location.items else None
                    })
            except (ValueError, IndexError):
                # Skip if conversion fails
                continue

    # Build response
    return jsonify({
        'id': location.id,
        'full_address': location.full_address(),
        'breadcrumb': breadcrumb,
        'module_id': location.level.module_id if location.level else None,
        'module_name': module_name,
        'level_id': location.level_id,
        'level_name': level_name,
        'row': location.row,
        'column': location.column,
        'location_type': location.location_type,
        'dimensions': {
            'width_mm': location.width_mm,
            'height_mm': location.height_mm,
            'depth_mm': location.depth_mm
        } if location.width_mm or location.height_mm or location.depth_mm else None,
        'notes': location.notes,
        'is_occupied': bool(location.items),
        'item': item_data,
        'adjacent_locations': adjacent_locations,
        'created_at': location.created_at.isoformat() if location.created_at else None,
        'updated_at': location.updated_at.isoformat() if location.updated_at else None
    })
