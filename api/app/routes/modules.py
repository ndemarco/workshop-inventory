from flask import Blueprint, request, jsonify
from app.models import db, Module, Level, Location, Item, ItemLocation

bp = Blueprint('modules', __name__)


# ============ LIST ============

@bp.route('', methods=['GET'])
def list_modules():
    """List all modules"""
    modules = Module.query.order_by(Module.name).all()
    return jsonify({
        'modules': [m.to_dict() for m in modules],
        'total': len(modules)
    })


@bp.route('/count', methods=['GET'])
def count_modules():
    """Get total module count"""
    return jsonify({'count': Module.query.count()})


# ============ SUMMARY ============

@bp.route('/summary', methods=['GET'])
def get_module_summary():
    """Get summary of modules including item and location counts"""
    modules = Module.query.order_by(Module.name).all()
    summary = []
    
    for module in modules:
        locations = Location.query.filter(Location.level_id.in_(
            Level.query.filter_by(module_id=module.id).with_entities(Level.id)
        )).all()
        
        total_items = ItemLocation.query.filter(
            ItemLocation.location_id.in_([l.id for l in locations])
        ).count()
        
        summary.append({
            'id': module.id,
            'name': module.name,
            'description': module.description,
            'location_count': len(locations),
            'item_count': total_items
        })
    
    return jsonify({
        'modules': summary,
        'total': len(summary)
    })

# ============ CREATE ============

@bp.route('/', methods=['POST'])
def create_module():
    """Create a new module"""
    data = request.get_json() or request.form
    
    name = data.get('name')
    description = data.get('description', '')
    location_description = data.get('location_description', '')
    
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    
    # Check if name already exists
    existing = Module.query.filter_by(name=name).first()
    if existing:
        return jsonify({'error': f'Module with name "{name}" already exists'}), 400
    
    module = Module(
        name=name,
        description=description,
        location_description=location_description
    )
    
    db.session.add(module)
    db.session.commit()
    
    return jsonify({
        'id': module.id,
        'message': f'Module "{name}" created successfully',
        'module': module.to_dict()
    }), 201


# ============ READ ============

@bp.route('/<int:module_id>', methods=['GET'])
def get_module(module_id):
    """Get module details with levels"""
    module = Module.query.get_or_404(module_id)
    levels = Level.query.filter_by(module_id=module_id).order_by(Level.level_number).all()
    
    result = module.to_dict()
    result['levels'] = [l.to_dict() for l in levels]
    result['level_count'] = len(levels)
    
    return jsonify(result)


# ============ UPDATE ============

@bp.route('/<int:module_id>', methods=['POST', 'PUT'])
def update_module(module_id):
    """Update a module"""
    module = Module.query.get_or_404(module_id)
    data = request.get_json() or request.form
    
    name = data.get('name', module.name)
    
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    
    # Check if name already exists (excluding current module)
    if name != module.name:
        existing = Module.query.filter_by(name=name).first()
        if existing:
            return jsonify({'error': f'Module with name "{name}" already exists'}), 400
    
    module.name = name
    module.description = data.get('description', module.description)
    module.location_description = data.get('location_description', module.location_description)
    
    db.session.commit()
    
    return jsonify({
        'message': f'Module "{module.name}" updated successfully',
        'module': module.to_dict()
    })


# ============ DELETE ============

@bp.route('/<int:module_id>', methods=['DELETE'])
def delete_module(module_id):
    """Delete a module (and all its levels, locations, and item associations)"""
    module = Module.query.get_or_404(module_id)
    name = module.name
    
    # Cascade delete levels and their locations
    levels = Level.query.filter_by(module_id=module_id).all()
    for level in levels:
        locations = Location.query.filter_by(level_id=level.id).all()
        for location in locations:
            # Delete all item-location associations for this location
            ItemLocation.query.filter_by(location_id=location.id).delete()
            db.session.delete(location)
        db.session.delete(level)
    
    db.session.delete(module)
    db.session.commit()
    
    return jsonify({'message': f'Module "{name}" deleted successfully'})


# ============ SUMMARY ============

@bp.route('/summary', methods=['GET'])
def modules_summary():
    """Get summary of all modules (useful for dashboard/stats)"""
    modules = Module.query.order_by(Module.name).all()
    
    summary = []
    for module in modules:
        levels = Level.query.filter_by(module_id=module.id).all()
        total_locations = 0
        total_items = 0
        
        for level in levels:
            locations = Location.query.filter_by(level_id=level.id).all()
            total_locations += len(locations)
            for location in locations:
                total_items += ItemLocation.query.filter_by(location_id=location.id).count()
        
        summary.append({
            'id': module.id,
            'name': module.name,
            'description': module.description,
            'level_count': len(levels),
            'location_count': total_locations,
            'item_count': total_items
        })
    
    return jsonify({
        'modules': summary,
        'total_modules': len(modules)
    })


# ============ LEVELS ============

@bp.route('/<int:module_id>/levels', methods=['GET'])
def list_module_levels(module_id):
    """List all levels in a module"""
    module = Module.query.get_or_404(module_id)
    levels = Level.query.filter_by(module_id=module_id).order_by(Level.level_number).all()
    
    return jsonify({
        'module_id': module_id,
        'module_name': module.name,
        'levels': [l.to_dict() for l in levels],
        'total': len(levels)
    })


@bp.route('/<int:module_id>/levels', methods=['POST'])
def create_level(module_id):
    """Create a new level in a module"""
    module = Module.query.get_or_404(module_id)
    data = request.get_json() or request.form
    
    level_number = int(data.get('level_number'))
    description = data.get('description', '')
    
    # Check if level already exists
    existing = Level.query.filter_by(module_id=module_id, level_number=level_number).first()
    if existing:
        return jsonify({'error': f'Level {level_number} already exists in this module'}), 400
    
    level = Level(
        module_id=module_id,
        level_number=level_number,
        description=description
    )
    
    db.session.add(level)
    db.session.commit()
    
    return jsonify({
        'id': level.id,
        'message': f'Level {level_number} created successfully',
        'level': level.to_dict()
    }), 201


@bp.route('/<int:module_id>/levels/<int:level_id>', methods=['GET'])
def get_level(module_id, level_id):
    """Get level details"""
    module = Module.query.get_or_404(module_id)
    level = Level.query.get_or_404(level_id)
    
    if level.module_id != module_id:
        return jsonify({'error': 'Level does not belong to this module'}), 400
    
    locations = Location.query.filter_by(level_id=level_id).all()
    
    result = level.to_dict()
    result['locations'] = [loc.to_dict() for loc in locations]
    result['location_count'] = len(locations)
    
    return jsonify(result)


@bp.route('/<int:module_id>/levels/<int:level_id>', methods=['POST', 'PUT'])
def update_level(module_id, level_id):
    """Update a level"""
    module = Module.query.get_or_404(module_id)
    level = Level.query.get_or_404(level_id)
    
    if level.module_id != module_id:
        return jsonify({'error': 'Level does not belong to this module'}), 400
    
    data = request.get_json() or request.form
    
    level_number = int(data.get('level_number', level.level_number))
    
    # Check if new level number conflicts
    if level_number != level.level_number:
        existing = Level.query.filter_by(module_id=module_id, level_number=level_number).first()
        if existing:
            return jsonify({'error': f'Level {level_number} already exists in this module'}), 400
    
    level.level_number = level_number
    level.description = data.get('description', level.description)
    
    db.session.commit()
    
    return jsonify({
        'message': f'Level updated successfully',
        'level': level.to_dict()
    })


@bp.route('/<int:module_id>/levels/<int:level_id>', methods=['DELETE'])
def delete_level(module_id, level_id):
    """Delete a level"""
    module = Module.query.get_or_404(module_id)
    level = Level.query.get_or_404(level_id)
    
    if level.module_id != module_id:
        return jsonify({'error': 'Level does not belong to this module'}), 400
    
    level_number = level.level_number
    
    # Delete all locations in this level (cascade)
    locations = Location.query.filter_by(level_id=level_id).all()
    for location in locations:
        ItemLocation.query.filter_by(location_id=location.id).delete()
        db.session.delete(location)
    
    db.session.delete(level)
    db.session.commit()
    
    return jsonify({'message': f'Level {level_number} deleted successfully'})
