from flask import Blueprint, render_template, request, jsonify
from app.models import db, Item
from app.services import embedding_service

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


@bp.route('/semantic')
def semantic_search():
    """Semantic search page using natural language"""
    query = request.args.get('q', '')
    results = []
    message = None

    if query:
        try:
            # Find similar items using embedding similarity
            # Lower threshold (0.3) to get more results
            similar_items = embedding_service.find_similar_items(
                query_text=query,
                threshold=0.3,
                limit=20
            )

            results = [
                {
                    'item': item,
                    'similarity': round(similarity * 100, 1)  # Convert to percentage
                }
                for item, similarity in similar_items
            ]

            if not results:
                message = 'No items found matching your search'
            elif len(results) == 1:
                message = f'Found 1 item'
            else:
                message = f'Found {len(results)} items'

        except Exception as e:
            message = f'Error performing search: {str(e)}'
            results = []

    return render_template('search/semantic.html', query=query, results=results, message=message)


@bp.route('/api/semantic', methods=['GET'])
def api_semantic_search():
    """API endpoint for semantic search"""
    query = request.args.get('q')
    threshold = request.args.get('threshold', 0.3, type=float)
    limit = request.args.get('limit', 20, type=int)

    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400

    try:
        similar_items = embedding_service.find_similar_items(
            query_text=query,
            threshold=threshold,
            limit=limit
        )

        results = [
            {
                'item': item.to_dict(),
                'similarity_score': similarity,
                'similarity_percent': round(similarity * 100, 1)
            }
            for item, similarity in similar_items
        ]

        return jsonify({
            'query': query,
            'count': len(results),
            'results': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
