from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import db, Location, Level, Item, ItemLocation

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
        query = query.join(ItemLocation).distinct()
    elif occupied == 'no':
        query = query.outerjoin(ItemLocation).filter(ItemLocation.id == None)
    
    locations = query.order_by(Level.module_id, Level.level_number, Location.row, Location.column).all()
    
    # Get unique location types for filter dropdown
    location_types = db.session.query(Location.location_type).distinct().all()
    location_types = [lt[0] for lt in location_types if lt[0]]
    
    return render_template('locations/list.html', 
                         locations=locations, 
                         location_types=location_types)


@bp.route('/<int:location_id>')
def view_location(location_id):
    """View location details and items stored there"""
    location = Location.query.get_or_404(location_id)
    item_locations = ItemLocation.query.filter_by(location_id=location_id).all()
    
    return render_template('locations/view.html', 
                         location=location, 
                         item_locations=item_locations)


@bp.route('/<int:location_id>/edit', methods=['GET', 'POST'])
def edit_location(location_id):
    """Edit location properties"""
    location = Location.query.get_or_404(location_id)
    
    if request.method == 'POST':
        location.location_type = request.form.get('location_type', 'general')
        location.width_mm = request.form.get('width_mm', type=float)
        location.height_mm = request.form.get('height_mm', type=float)
        location.depth_mm = request.form.get('depth_mm', type=float)
        # Color (hex string like #RRGGBB)
        color_val = request.form.get('color')
        if color_val:
            location.color = color_val
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
        query = query.outerjoin(ItemLocation).filter(ItemLocation.id == None)
    
    locations = query.all()
    return jsonify([l.to_dict() for l in locations])


@bp.route('/api/locations/<int:location_id>', methods=['GET'])
def api_get_location(location_id):
    """API endpoint to get a single location"""
    location = Location.query.get_or_404(location_id)
    return jsonify(location.to_dict())
