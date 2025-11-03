from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from app.models import db, Item, ItemLocation, Location, Level, Module
from app.services.location_suggestions import LocationSuggestionService
from app.services.duplicate_detector import DuplicateDetector
import qrcode
from io import BytesIO
import secrets

bp = Blueprint('items', __name__)


@bp.route('/')
def list_items():
    """List all items"""
    # Get filter parameters
    category = request.args.get('category')
    search = request.args.get('search')
    location_id = request.args.get('location_id', type=int)
    
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
    
    if location_id:
        # Filter items that have this location
        query = query.join(ItemLocation).filter(ItemLocation.location_id == location_id)
    
    items = query.order_by(Item.name).all()
    
    # Get unique categories for filter dropdown
    categories = db.session.query(Item.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    # Get location info if filtering by location
    filtered_location = None
    if location_id:
        filtered_location = Location.query.get(location_id)
    
    return render_template('items/list.html', items=items, categories=categories, filtered_location=filtered_location)


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
        quantity = request.form.get('quantity', type=int, default=0)
        unit = request.form.get('unit', default='pieces')

        # Location information
        location_id = request.form.get('location_id', type=int)

        if not name or not description:
            flash('Name and description are required', 'error')
            return render_template('items/form.html', modules=Module.query.all())

        item = Item(
            name=name,
            description=description,
            category=category,
            item_type=item_type,
            tags=tags,
            notes=notes,
            quantity=quantity,
            unit=unit
        )

        db.session.add(item)
        db.session.flush()  # Get the item ID

        # Add location if provided
        if location_id:
            item_location = ItemLocation(
                item_id=item.id,
                location_id=location_id
            )
            db.session.add(item_location)
        
        db.session.commit()
        
        flash(f'Item "{name}" created successfully', 'success')
        return redirect(url_for('items.view_item', item_id=item.id))
    
    # For GET request, load modules for location selection
    modules = Module.query.order_by(Module.name).all()
    
    # Get existing categories, item types, and units for autocomplete
    categories = db.session.query(Item.category).distinct().filter(Item.category.isnot(None)).all()
    categories = sorted([c[0] for c in categories if c[0]])
    
    item_types = db.session.query(Item.item_type).distinct().filter(Item.item_type.isnot(None)).all()
    item_types = sorted([t[0] for t in item_types if t[0]])
    
    units = db.session.query(Item.unit).distinct().filter(Item.unit.isnot(None)).all()
    units = sorted([u[0] for u in units if u[0]])
    
    return render_template('items/form.html', modules=modules, 
                         existing_categories=categories,
                         existing_item_types=item_types,
                         existing_units=units)


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
        item.quantity = request.form.get('quantity', type=int, default=0)
        item.unit = request.form.get('unit', default='pieces')
        
        if not item.name or not item.description:
            flash('Name and description are required', 'error')
            return render_template('items/form.html', item=item, modules=Module.query.all())
        
        db.session.commit()
        
        flash(f'Item "{item.name}" updated successfully', 'success')
        return redirect(url_for('items.view_item', item_id=item.id))
    
    modules = Module.query.order_by(Module.name).all()
    
    # Get existing categories, item types, and units for autocomplete
    categories = db.session.query(Item.category).distinct().filter(Item.category.isnot(None)).all()
    categories = sorted([c[0] for c in categories if c[0]])
    
    item_types = db.session.query(Item.item_type).distinct().filter(Item.item_type.isnot(None)).all()
    item_types = sorted([t[0] for t in item_types if t[0]])
    
    units = db.session.query(Item.unit).distinct().filter(Item.unit.isnot(None)).all()
    units = sorted([u[0] for u in units if u[0]])
    
    return render_template('items/form.html', item=item, modules=modules,
                         existing_categories=categories,
                         existing_item_types=item_types,
                         existing_units=units)


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


@bp.route('/api/suggest-location', methods=['POST'])
def api_suggest_location():
    """API endpoint to suggest locations for an item"""
    data = request.get_json()
    
    # Extract item characteristics from request
    category = data.get('category')
    item_type = data.get('item_type')
    tags = data.get('tags', [])
    
    # Handle tags as comma-separated string or list
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(',') if t.strip()]
    
    # Optional dimensions
    width_mm = data.get('width_mm')
    height_mm = data.get('height_mm')
    depth_mm = data.get('depth_mm')
    limit = data.get('limit', 5)
    
    # Get suggestions
    suggestions = LocationSuggestionService.suggest_locations(
        item_category=category,
        item_type=item_type,
        item_tags=tags,
        width_mm=width_mm,
        height_mm=height_mm,
        depth_mm=depth_mm,
        limit=limit
    )
    
    return jsonify([s.to_dict() for s in suggestions])


@bp.route('/api/items/<int:item_id>/suggest-location', methods=['GET'])
def api_suggest_location_for_item(item_id):
    """API endpoint to suggest locations for an existing item"""
    item = Item.query.get_or_404(item_id)
    limit = request.args.get('limit', 5, type=int)
    
    suggestions = LocationSuggestionService.suggest_for_item(item, limit=limit)
    
    return jsonify([s.to_dict() for s in suggestions])


@bp.route('/api/check-duplicates', methods=['POST'])
def api_check_duplicates():
    """
    API endpoint to check for potential duplicate items
    
    Request JSON:
    {
        "name": "Item name",
        "description": "Item description",
        "category": "Category",
        "tags": "tag1, tag2, tag3",
        "threshold": 0.7  // Optional, defaults to 0.7
    }
    
    Returns:
    {
        "has_duplicates": true/false,
        "matches": [
            {
                "item_id": 123,
                "item_name": "Similar item",
                "similarity_score": 0.85,
                "match_reasons": ["Similar name", "Same category"],
                "differences": ["Different quantity"],
                "locations": [{"module": "Zeus", "level": 1, "location": "A3"}],
                "quantity": 50,
                "unit": "pieces"
            }
        ]
    }
    """
    data = request.get_json()
    
    name = data.get('name', '')
    description = data.get('description', '')
    category = data.get('category')
    tags = data.get('tags', '')
    threshold = data.get('threshold', 0.7)
    
    if not name or not description:
        return jsonify({
            'error': 'Name and description are required'
        }), 400
    
    # Get all existing items with their locations
    items = Item.query.all()
    items_data = []
    for item in items:
        item_dict = item.to_dict()
        # Add location information
        item_dict['locations'] = []
        for item_loc in item.item_locations:
            loc = item_loc.location
            item_dict['locations'].append({
                'module': loc.level.module.name,
                'level': loc.level.level_number,
                'location': f"{loc.row}{loc.column}",
                'quantity': item_loc.quantity
            })
        items_data.append(item_dict)
    
    # Find duplicates
    detector = DuplicateDetector()
    matches = detector.find_similar(
        name=name,
        description=description,
        category=category,
        tags=tags,
        existing_items=items_data,
        threshold=threshold
    )
    
    return jsonify({
        'has_duplicates': len(matches) > 0,
        'match_count': len(matches),
        'matches': [match.to_dict() for match in matches]
    })


@bp.route('/api/extract-specs', methods=['POST'])
def api_extract_specs():
    """
    API endpoint to extract specifications from item description
    
    Request JSON:
    {
        "name": "Item name",
        "description": "M6x50 pan head phillips screw, stainless steel"
    }
    
    Returns:
    {
        "category": "fastener",
        "specs": {
            "thread_size": "M6",
            "length_mm": 50,
            "head_type": "pan head",
            "drive": "phillips"
        },
        "tags": ["M6", "50mm", "pan-head", "phillips", "stainless"],
        "confidence": 0.9
    }
    """
    from app.services.spec_parser import SpecificationParser
    
    data = request.get_json()
    
    name = data.get('name', '')
    description = data.get('description', '')
    
    if not description:
        return jsonify({
            'error': 'Description is required'
        }), 400
    
    # Parse specifications
    parser = SpecificationParser()
    parsed = parser.parse(description, name)
    
    return jsonify({
        'category': parsed.category,
        'specs': parsed.specs,
        'tags': parsed.tags,
        'confidence': parsed.confidence
    })


@bp.route('/<int:item_id>/qr/generate', methods=['POST'])
def generate_qr_code(item_id):
    """Generate a new QR code for an item"""
    item = Item.query.get_or_404(item_id)
    
    # Generate a unique QR code if not exists
    if not item.qr_code:
        # Generate a unique code: INV-{random_string}
        while True:
            code = f"INV-{secrets.token_urlsafe(12)}"
            # Check if code already exists
            existing = Item.query.filter_by(qr_code=code).first()
            if not existing:
                item.qr_code = code
                break
        
        db.session.commit()
        flash(f'QR code generated for "{item.name}"', 'success')
    else:
        flash(f'QR code already exists for "{item.name}"', 'info')
    
    return redirect(url_for('items.view_item', item_id=item_id))


@bp.route('/<int:item_id>/qr/download')
def download_qr_code(item_id):
    """Download QR code image for an item"""
    item = Item.query.get_or_404(item_id)
    
    if not item.qr_code:
        flash('No QR code exists for this item. Generate one first.', 'error')
        return redirect(url_for('items.view_item', item_id=item_id))
    
    # Generate QR code image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(item.qr_code)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    # Safe filename
    safe_name = "".join(c for c in item.name if c.isalnum() or c in (' ', '-', '_')).strip()
    filename = f"QR_{safe_name}_{item.id}.png"
    
    return send_file(
        img_io,
        mimetype='image/png',
        as_attachment=True,
        download_name=filename
    )


@bp.route('/qr/scan/<qr_code>')
def scan_qr_code(qr_code):
    """Redirect to item page from scanned QR code"""
    item = Item.query.filter_by(qr_code=qr_code).first()
    
    if not item:
        flash(f'No item found with QR code: {qr_code}', 'error')
        return redirect(url_for('items.list_items'))
    
    flash(f'Found item from QR code!', 'success')
    return redirect(url_for('items.view_item', item_id=item.id))


@bp.route('/qr/scanner')
def qr_scanner():
    """QR Code scanner page"""
    return render_template('items/scanner.html')
