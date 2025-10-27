from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import db, Item, ItemLocation, Location, Level, Module

bp = Blueprint('items', __name__)


@bp.route('/')
def list_items():
    """List all items"""
    # Get filter parameters
    category = request.args.get('category')
    search = request.args.get('search')
    
    query = Item.query
    
    if category:
        query = query.filter(Item.category == category)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Item.name.ilike(search_term),
                Item.description.ilike(search_term),
                Item.tags.ilike(search_term)
            )
        )
    
    items = query.order_by(Item.name).all()
    
    # Get unique categories for filter dropdown
    categories = db.session.query(Item.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    return render_template('items/list.html', items=items, categories=categories)


@bp.route('/new', methods=['GET', 'POST'])
def new_item():
    """Create a new item"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        item_type = request.form.get('item_type')
        quantity = request.form.get('quantity', type=int, default=1)
        unit = request.form.get('unit')
        min_quantity = request.form.get('min_quantity', type=int)
        tags = request.form.get('tags')
        notes = request.form.get('notes')
        
        # Location information
        location_id = request.form.get('location_id', type=int)
        location_quantity = request.form.get('location_quantity', type=int, default=quantity)
        
        if not name or not description:
            flash('Name and description are required', 'error')
            return render_template('items/form.html', modules=Module.query.all())
        
        item = Item(
            name=name,
            description=description,
            category=category,
            item_type=item_type,
            quantity=quantity,
            unit=unit,
            min_quantity=min_quantity,
            tags=tags,
            notes=notes
        )
        
        db.session.add(item)
        db.session.flush()  # Get the item ID
        
        # Add location if provided
        if location_id:
            item_location = ItemLocation(
                item_id=item.id,
                location_id=location_id,
                quantity=location_quantity
            )
            db.session.add(item_location)
        
        db.session.commit()
        
        flash(f'Item "{name}" created successfully', 'success')
        return redirect(url_for('items.view_item', item_id=item.id))
    
    # For GET request, load modules for location selection
    modules = Module.query.order_by(Module.name).all()
    return render_template('items/form.html', modules=modules)


@bp.route('/<int:item_id>')
def view_item(item_id):
    """View item details"""
    item = Item.query.get_or_404(item_id)
    modules = Module.query.order_by(Module.name).all()
    return render_template('items/view.html', item=item, modules=modules)


@bp.route('/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_item(item_id):
    """Edit an item"""
    item = Item.query.get_or_404(item_id)
    
    if request.method == 'POST':
        item.name = request.form.get('name')
        item.description = request.form.get('description')
        item.category = request.form.get('category')
        item.item_type = request.form.get('item_type')
        item.quantity = request.form.get('quantity', type=int, default=1)
        item.unit = request.form.get('unit')
        item.min_quantity = request.form.get('min_quantity', type=int)
        item.tags = request.form.get('tags')
        item.notes = request.form.get('notes')
        
        if not item.name or not item.description:
            flash('Name and description are required', 'error')
            return render_template('items/form.html', item=item, modules=Module.query.all())
        
        db.session.commit()
        
        flash(f'Item "{item.name}" updated successfully', 'success')
        return redirect(url_for('items.view_item', item_id=item.id))
    
    modules = Module.query.order_by(Module.name).all()
    return render_template('items/form.html', item=item, modules=modules)


@bp.route('/<int:item_id>/delete', methods=['POST'])
def delete_item(item_id):
    """Delete an item"""
    item = Item.query.get_or_404(item_id)
    name = item.name
    
    db.session.delete(item)
    db.session.commit()
    
    flash(f'Item "{name}" deleted successfully', 'success')
    return redirect(url_for('items.list_items'))


@bp.route('/<int:item_id>/locations/add', methods=['POST'])
def add_location(item_id):
    """Add a location to an item"""
    item = Item.query.get_or_404(item_id)
    
    location_id = request.form.get('location_id', type=int)
    quantity = request.form.get('quantity', type=int, default=1)
    notes = request.form.get('notes')
    
    if not location_id:
        flash('Location is required', 'error')
        return redirect(url_for('items.view_item', item_id=item_id))
    
    # Check if this item-location combination already exists
    existing = ItemLocation.query.filter_by(item_id=item_id, location_id=location_id).first()
    if existing:
        flash('Item is already stored at this location', 'error')
        return redirect(url_for('items.view_item', item_id=item_id))
    
    item_location = ItemLocation(
        item_id=item_id,
        location_id=location_id,
        quantity=quantity,
        notes=notes
    )
    
    db.session.add(item_location)
    db.session.commit()
    
    location = Location.query.get(location_id)
    flash(f'Location {location.full_address()} added successfully', 'success')
    return redirect(url_for('items.view_item', item_id=item_id))


@bp.route('/<int:item_id>/locations/<int:item_location_id>/remove', methods=['POST'])
def remove_location(item_id, item_location_id):
    """Remove a location from an item"""
    item_location = ItemLocation.query.get_or_404(item_location_id)
    
    if item_location.item_id != item_id:
        flash('Invalid item-location combination', 'error')
        return redirect(url_for('items.view_item', item_id=item_id))
    
    location_address = item_location.location.full_address()
    
    db.session.delete(item_location)
    db.session.commit()
    
    flash(f'Location {location_address} removed successfully', 'success')
    return redirect(url_for('items.view_item', item_id=item_id))


# API endpoints

@bp.route('/api/items', methods=['GET'])
def api_list_items():
    """API endpoint to list items"""
    search = request.args.get('search')
    category = request.args.get('category')
    
    query = Item.query
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Item.name.ilike(search_term),
                Item.description.ilike(search_term)
            )
        )
    
    if category:
        query = query.filter(Item.category == category)
    
    items = query.order_by(Item.name).limit(50).all()
    return jsonify([i.to_dict() for i in items])


@bp.route('/api/items/<int:item_id>', methods=['GET'])
def api_get_item(item_id):
    """API endpoint to get a single item"""
    item = Item.query.get_or_404(item_id)
    return jsonify(item.to_dict())
