from flask import Blueprint, request, jsonify
from app.models import db, Item

bp = Blueprint('search', __name__)


@bp.route('', methods=['GET'])
def search_items():
    """Search items by name, description, tags, or notes"""
    query = request.args.get('q', '')
    limit = request.args.get('limit', 50, type=int)
    
    if not query or len(query) < 2:
        return jsonify({'results': [], 'total': 0})
    
    search_term = f"%{query}%"
    items = Item.query.filter(
        db.or_(
            Item.name.ilike(search_term),
            Item.description.ilike(search_term),
            Item.tags.ilike(search_term),
            Item.notes.ilike(search_term)
        )
    ).order_by(Item.name).limit(limit).all()
    
    return jsonify({
        'query': query,
        'total': len(items),
        'results': [i.to_dict() for i in items]
    })


@bp.route('/advanced', methods=['POST'])
def advanced_search():
    """Advanced search with multiple filters"""
    data = request.get_json() or request.form
    
    query = data.get('q', '')
    category = data.get('category')
    item_type = data.get('item_type')
    tags = data.get('tags', [])
    min_quantity = data.get('min_quantity', type=int)
    max_quantity = data.get('max_quantity', type=int)
    location_id = data.get('location_id', type=int)
    limit = data.get('limit', 50, type=int)
    
    items_query = Item.query
    
    if query:
        search_term = f"%{query}%"
        items_query = items_query.filter(
            db.or_(
                Item.name.ilike(search_term),
                Item.description.ilike(search_term),
                Item.tags.ilike(search_term),
                Item.notes.ilike(search_term)
            )
        )
    
    if category:
        items_query = items_query.filter(Item.category == category)
    
    if item_type:
        items_query = items_query.filter(Item.item_type == item_type)
    
    if tags:
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',')]
        for tag in tags:
            items_query = items_query.filter(Item.tags.ilike(f"%{tag}%"))
    
    if min_quantity is not None:
        items_query = items_query.filter(Item.quantity >= min_quantity)
    
    if max_quantity is not None:
        items_query = items_query.filter(Item.quantity <= max_quantity)
    
    if location_id:
        from app.models import ItemLocation
        items_query = items_query.join(ItemLocation).filter(ItemLocation.location_id == location_id)
    
    items = items_query.order_by(Item.name).limit(limit).all()
    
    return jsonify({
        'query': query,
        'filters': {
            'category': category,
            'item_type': item_type,
            'tags': tags,
            'min_quantity': min_quantity,
            'max_quantity': max_quantity,
            'location_id': location_id
        },
        'total': len(items),
        'results': [i.to_dict() for i in items]
    })
