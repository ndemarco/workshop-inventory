from flask import Blueprint, request, jsonify
from app.models import db, Location, Level, Item, ItemLocation

bp = Blueprint('locations', __name__)


# ============ LIST & SEARCH ============

@bp.route('', methods=['GET'])
def list_locations():
    """List all locations with optional filtering"""
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
        query = query.join(ItemLocation).distinct()
    elif occupied == 'no':
        query = query.outerjoin(ItemLocation).filter(ItemLocation.id == None)
    
    locations = query.order_by(Level.module_id, Level.level_number, Location.row, Location.column).all()
    
    # Get unique location types for filter dropdown
    location_types = db.session.query(Location.location_type).distinct().all()
    location_types = [lt[0] for lt in location_types if lt[0]]
    
    return jsonify({
        'locations': [loc.to_dict() for loc in locations],
        'location_types': location_types,
        'total': len(locations)
    })


@bp.route('/count', methods=['GET'])
def count_locations():
    """Get total location count"""
    return jsonify({'count': Location.query.count()})

@bp.route('/types', methods=['GET'])
def get_location_types():
    """Get all unique location types"""
    types = db.session.query(Location.location_type).distinct().all()
    types = [t[0] for t in types if t[0]]
    return jsonify({
        'types': types
    })

@bp.route('/vacant', methods=['GET'])
def get_vacant_locations():
    """Get all vacant locations"""
    vacant = Location.query.outerjoin(ItemLocation).filter(ItemLocation.id == None).all()
    return jsonify({
        'locations': [loc.to_dict() for loc in vacant],
        'total': len(vacant)
    })

@bp.route('/occupied', methods=['GET'])
def get_occupied_locations():
    """Get all occupied locations with their items"""
    occupied = Location.query.join(ItemLocation).distinct().all()
    result = []
    
    for location in occupied:
        loc_dict = location.to_dict()
        items = Item.query.join(ItemLocation).filter(ItemLocation.location_id == location.id).all()
        loc_dict['items'] = [item.to_dict() for item in items]
        result.append(loc_dict)
    
    return jsonify({
        'locations': result,
        'total': len(result)
    })


# ============ READ ============

@bp.route('/<int:location_id>', methods=['GET'])
def get_location(location_id):
    """Get location details and items stored there"""
    location = Location.query.get_or_404(location_id)
    item_locations = ItemLocation.query.filter_by(location_id=location_id).all()
    
    result = location.to_dict()
    result['items'] = [il.to_dict() for il in item_locations]
    result['item_count'] = len(item_locations)
    
    return jsonify(result)


# ============ UPDATE ============

@bp.route('/<int:location_id>', methods=['POST', 'PUT'])
def update_location(location_id):
    """Update location properties"""
    location = Location.query.get_or_404(location_id)
    data = request.get_json() or request.form
    
    location.location_type = data.get('location_type', location.location_type)
    location.width_mm = float(data.get('width_mm', location.width_mm or 0)) or None
    location.height_mm = float(data.get('height_mm', location.height_mm or 0)) or None
    location.depth_mm = float(data.get('depth_mm', location.depth_mm or 0)) or None
    
    color_val = data.get('color')
    if color_val:
        location.color = color_val
    
    location.notes = data.get('notes', location.notes)
    
    db.session.commit()
    
    return jsonify({
        'message': f'Location {location.full_address()} updated successfully',
        'location': location.to_dict()
    })


# ============ DELETE ============

@bp.route('/<int:location_id>', methods=['DELETE'])
def delete_location(location_id):
    """Delete a location"""
    location = Location.query.get_or_404(location_id)
    address = location.full_address()
    
    # Delete all item-location associations
    ItemLocation.query.filter_by(location_id=location_id).delete()
    
    db.session.delete(location)
    db.session.commit()
    
    return jsonify({'message': f'Location {address} deleted successfully'})


# ============ ITEMS AT LOCATION ============

@bp.route('/<int:location_id>/items', methods=['GET'])
def get_location_items(location_id):
    """Get all items stored at a specific location"""
    location = Location.query.get_or_404(location_id)
    item_locations = ItemLocation.query.filter_by(location_id=location_id).all()
    
    items = []
    for il in item_locations:
        item_dict = il.item.to_dict()
        item_dict['location_notes'] = il.notes
        items.append(item_dict)
    
    return jsonify({
        'location': location.to_dict(),
        'items': items,
        'total': len(items)
    })


# ============ UTILITY ============

@bp.route('/by-level/<int:level_id>', methods=['GET'])
def get_level_locations(level_id):
    """Get all locations in a specific level"""
    level = db.session.query(db.func.count(Location.id)).filter_by(level_id=level_id).scalar()
    if level is None:
        return jsonify({'error': 'Level not found'}), 404
    
    locations = Location.query.filter_by(level_id=level_id).order_by(Location.row, Location.column).all()
    
    return jsonify({
        'level_id': level_id,
        'locations': [loc.to_dict() for loc in locations],
        'total': len(locations)
    })


@bp.route('/by-module/<int:module_id>', methods=['GET'])
def get_module_locations(module_id):
    """Get all locations in a specific module"""
    from app.models import Level
    
    levels = Level.query.filter_by(module_id=module_id).all()
    if not levels:
        return jsonify({'error': 'Module not found or has no levels'}), 404
    
    level_ids = [l.id for l in levels]
    locations = Location.query.filter(Location.level_id.in_(level_ids)).order_by(Location.row, Location.column).all()
    
    return jsonify({
        'module_id': module_id,
        'locations': [loc.to_dict() for loc in locations],
        'total': len(locations)
    })



