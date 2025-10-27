from flask import Blueprint, render_template, request, jsonify
from app.models import db, Item

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
