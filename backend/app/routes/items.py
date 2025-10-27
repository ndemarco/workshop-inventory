from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import db, Item, Location, Level, Module

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
        tags = request.form.get('tags')
        notes = request.form.get('notes')
        location_id = request.form.get('location_id', type=int)

        if not name or not description:
            flash('Name and description are required', 'error')
            return render_template('items/form.html', modules=Module.query.all())

        # Check if location is already occupied
        if location_id:
            existing_item = Item.query.filter_by(location_id=location_id).first()
            if existing_item:
                flash(f'Location is already occupied by "{existing_item.name}". Please choose another location.', 'error')
                return render_template('items/form.html', modules=Module.query.all())

        item = Item(
            name=name,
            description=description,
            category=category,
            item_type=item_type,
            tags=tags,
            notes=notes,
            location_id=location_id
        )

        db.session.add(item)
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
        item.tags = request.form.get('tags')
        item.notes = request.form.get('notes')
        
        # Handle location change
        new_location_id = request.form.get('location_id', type=int)
        if new_location_id != item.location_id:
            # Check if new location is already occupied
            if new_location_id:
                existing_item = Item.query.filter_by(location_id=new_location_id).first()
                if existing_item and existing_item.id != item.id:
                    flash(f'Location is already occupied by "{existing_item.name}". Please choose another location.', 'error')
                    return render_template('items/form.html', item=item, modules=Module.query.all())
            item.location_id = new_location_id
        
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


@bp.route('/<int:item_id>/move', methods=['POST'])
def move_item(item_id):
    """Move an item to a different location"""
    item = Item.query.get_or_404(item_id)
    
    new_location_id = request.form.get('location_id', type=int)
    
    if not new_location_id:
        item.location_id = None
        db.session.commit()
        flash('Item removed from location', 'success')
        return redirect(url_for('items.view_item', item_id=item_id))
    
    # Check if location is already occupied
    existing_item = Item.query.filter_by(location_id=new_location_id).first()
    if existing_item and existing_item.id != item.id:
        flash(f'Location is already occupied by "{existing_item.name}"', 'error')
        return redirect(url_for('items.view_item', item_id=item_id))
    
    old_location = item.location.full_address() if item.location else "no location"
    item.location_id = new_location_id
    db.session.commit()
    
    new_location = Location.query.get(new_location_id)
    flash(f'Item moved from {old_location} to {new_location.full_address()}', 'success')
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
