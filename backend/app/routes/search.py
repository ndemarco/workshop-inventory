from flask import Blueprint, render_template, request, jsonify
from app.models import db, Item, Location, Level, Module
from sqlalchemy.orm import joinedload

bp = Blueprint('search', __name__)


@bp.route('/')
def search():
    """Search page"""
    query = request.args.get('q', '')
    results = []
    
    if query:
        search_term = f"%{query}%"
        results = Item.query.filter(
            db.or_(
                Item.name.ilike(search_term),
                Item.description.ilike(search_term),
                Item.tags.ilike(search_term),
                Item.notes.ilike(search_term)
            )
        ).order_by(Item.name).all()
    
    return render_template('search/results.html', query=query, results=results)


@bp.route('/api', methods=['GET'])
def api_search():
    """API endpoint for search"""
    query = request.args.get('q', '')

    if not query:
        return jsonify({'results': []})

    search_term = f"%{query}%"
    items = Item.query.filter(
        db.or_(
            Item.name.ilike(search_term),
            Item.description.ilike(search_term),
            Item.tags.ilike(search_term)
        )
    ).order_by(Item.name).limit(20).all()

    return jsonify({
        'query': query,
        'count': len(items),
        'results': [i.to_dict() for i in items]
    })


@bp.route('/api/live', methods=['GET'])
def live_search():
    """
    Live search API with location context and breadcrumbs
    Query params: ?q=<query>&limit=<num>
    Returns: List of items with location breadcrumbs and IDs for highlighting
    """
    query = request.args.get('q', '').strip()
    limit = request.args.get('limit', 5, type=int)

    # Validate limit (default 5, max 20)
    limit = max(1, min(limit, 20))

    # Return empty results for empty or very short queries
    if len(query) < 2:
        return jsonify({
            'query': query,
            'count': 0,
            'limit': limit,
            'results': []
        })

    # Search items with eager-loaded location relationships
    search_term = f"%{query}%"
    items = Item.query.options(
        joinedload(Item.location).joinedload(Location.level).joinedload(Level.module)
    ).filter(
        db.or_(
            Item.name.ilike(search_term),
            Item.description.ilike(search_term),
            Item.tags.ilike(search_term),
            Item.notes.ilike(search_term)
        )
    ).order_by(Item.name).limit(limit).all()

    # Build results with location context
    results = []
    for item in items:
        result = {
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'category': item.category,
            'location_id': item.location_id,
            'module_id': None,
            'level_id': None,
            'location_address': None,
            'location_breadcrumb': None
        }

        # Add location information if item has a location
        if item.location:
            location = item.location
            result['location_id'] = location.id
            result['location_address'] = location.full_address()

            if location.level:
                level = location.level
                result['level_id'] = level.id

                if level.module:
                    module = level.module
                    result['module_id'] = module.id

                    # Generate formatted breadcrumb: "Module Name → Level X → A1"
                    level_name = level.name or f"Level {level.level_number}"
                    result['location_breadcrumb'] = f"{module.name} → {level_name} → {location.row}{location.column}"
        else:
            result['location_breadcrumb'] = "No location assigned"

        results.append(result)

    return jsonify({
        'query': query,
        'count': len(results),
        'limit': limit,
        'results': results
    })
