from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from markupsafe import Markup
from app.models import db, Item, ItemLocation, Location, Level, Module, DuplicateCandidate
from app.services.embedding_service import embedding_service
from app.services.ai_description_service import ai_description_service

bp = Blueprint('items', __name__)


@bp.route('/')
def list_items():
    """Redirect to search - items list is superfluous with search-first UI"""
    # If there's a search query, pass it to search page
    search = request.args.get('search')
    if search:
        return redirect(url_for('search.search', q=search))

    # Otherwise redirect to main search page
    return redirect(url_for('search.search'))


@bp.route('/new', methods=['GET', 'POST'])
def new_item():
    """Create a new item"""
    if request.method == 'POST':
        # Form now submits AI-generated fields directly (populated by JS)
        name = request.form.get('name')
        description = request.form.get('description')
        raw_input = request.form.get('raw_input')  # User's original description
        category = request.form.get('category')
        item_type = request.form.get('item_type')
        tags = request.form.get('tags')
        notes = request.form.get('notes')

        # Location information
        location_id = request.form.get('location_id', type=int)

        if not name or not description:
            flash('Name and description are required. Did you click "Generate Description"?', 'error')
            return render_template('items/form.html', modules=Module.query.all())

        # Generate embedding from description
        try:
            embedding = embedding_service.generate_embedding(description)
        except Exception as e:
            flash(f'Warning: Could not generate embedding: {str(e)}', 'warning')
            embedding = None

        item = Item(
            name=name,
            description=description,
            raw_input=raw_input,  # Store user's original input
            category=category,
            item_type=item_type,
            tags=tags,
            notes=notes,
            embedding=embedding
        )

        db.session.add(item)
        db.session.flush()  # Get the item ID

        # Check for potential duplicates (don't block creation)
        duplicate_count = 0
        if embedding:
            try:
                similar_items = embedding_service.find_duplicates_for_item(item, threshold=0.85)
                for similar_item, similarity in similar_items:
                    # Create duplicate candidate record
                    duplicate = DuplicateCandidate(
                        item1_id=item.id,
                        item2_id=similar_item.id,
                        similarity_score=similarity,
                        status='pending'
                    )
                    db.session.add(duplicate)
                    duplicate_count += 1
            except Exception as e:
                flash(f'Warning: Could not check for duplicates: {str(e)}', 'warning')

        # Assign location if provided
        if location_id:
            # Check if the location is already occupied
            location_occupied = ItemLocation.query.filter_by(location_id=location_id).first()
            if location_occupied:
                location = Location.query.get(location_id)
                occupied_item = location_occupied.item
                flash(f'Warning: Location {location.full_address()} is already occupied by "{occupied_item.name}". Item created without location.', 'warning')
            else:
                item_location = ItemLocation(
                    item_id=item.id,
                    location_id=location_id
                )
                db.session.add(item_location)

        db.session.commit()

        flash(f'Item "{name}" created successfully', 'success')
        if duplicate_count > 0:
            duplicates_url = url_for('duplicates.list_duplicates')
            flash(Markup(f'Found {duplicate_count} potential duplicate(s). Review them in the <a href="{duplicates_url}">Duplicates</a> section.'), 'warning')
        return redirect(url_for('items.view_item', item_id=item.id))
    
    # For GET request, load modules for location selection
    modules = Module.query.order_by(Module.name).all()
    return render_template('items/form.html', modules=modules)


@bp.route('/generate-description', methods=['POST'])
def generate_description():
    """AJAX endpoint to generate item description from raw input"""
    raw_input = request.json.get('raw_input', '').strip()

    if not raw_input:
        return jsonify({'error': 'No input provided'}), 400

    try:
        print(f"[AI Generation] Input: {raw_input}")
        result = ai_description_service.generate_item_details(raw_input)
        print(f"[AI Generation] Output: {result}")
        return jsonify(result), 200
    except Exception as e:
        print(f"[AI Generation] Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


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
        old_description = item.description

        item.name = request.form.get('name')
        item.description = request.form.get('description')
        item.category = request.form.get('category')
        item.item_type = request.form.get('item_type')
        item.tags = request.form.get('tags')
        item.notes = request.form.get('notes')

        if not item.name or not item.description:
            flash('Name and description are required', 'error')
            return render_template('items/form.html', item=item, modules=Module.query.all())

        # Regenerate embedding if description changed
        duplicate_count = 0
        if item.description != old_description:
            try:
                item.embedding = embedding_service.generate_embedding(item.description)

                # Check for new duplicates
                similar_items = embedding_service.find_duplicates_for_item(item, threshold=0.85)
                for similar_item, similarity in similar_items:
                    # Check if this duplicate pair already exists
                    existing = DuplicateCandidate.query.filter(
                        db.or_(
                            db.and_(DuplicateCandidate.item1_id == item.id, DuplicateCandidate.item2_id == similar_item.id),
                            db.and_(DuplicateCandidate.item1_id == similar_item.id, DuplicateCandidate.item2_id == item.id)
                        )
                    ).first()

                    if not existing:
                        duplicate = DuplicateCandidate(
                            item1_id=item.id,
                            item2_id=similar_item.id,
                            similarity_score=similarity,
                            status='pending'
                        )
                        db.session.add(duplicate)
                        duplicate_count += 1
            except Exception as e:
                flash(f'Warning: Could not update embedding: {str(e)}', 'warning')

        db.session.commit()

        flash(f'Item "{item.name}" updated successfully', 'success')
        if duplicate_count > 0:
            duplicates_url = url_for('duplicates.list_duplicates')
            flash(Markup(f'Found {duplicate_count} new potential duplicate(s). Review them in the <a href="{duplicates_url}">Duplicates</a> section.'), 'warning')
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
    """Assign a location to an item"""
    item = Item.query.get_or_404(item_id)
    
    location_id = request.form.get('location_id', type=int)
    notes = request.form.get('notes')

    if not location_id:
        flash('Location is required', 'error')
        return redirect(url_for('items.view_item', item_id=item_id))

    # Check if this item-location combination already exists
    existing = ItemLocation.query.filter_by(item_id=item_id, location_id=location_id).first()
    if existing:
        flash('Item is already assigned to this location', 'error')
        return redirect(url_for('items.view_item', item_id=item_id))

    # Check if the location already has an item (one item per location limit)
    location_occupied = ItemLocation.query.filter_by(location_id=location_id).first()
    if location_occupied:
        location = Location.query.get(location_id)
        occupied_item = location_occupied.item
        flash(f'Location {location.full_address()} is already occupied by "{occupied_item.name}"', 'error')
        return redirect(url_for('items.view_item', item_id=item_id))

    item_location = ItemLocation(
        item_id=item_id,
        location_id=location_id,
        notes=notes
    )
    
    db.session.add(item_location)
    db.session.commit()

    location = Location.query.get(location_id)
    flash(f'Location {location.full_address()} assigned successfully', 'success')
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
