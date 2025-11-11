from flask import Blueprint, jsonify
from app.models import Module, Level, Location, Item

bp = Blueprint('main', __name__)


@bp.route('/stats')
def get_stats():
    """Get dashboard statistics"""
    stats = {
        'modules': Module.query.count(),
        'levels': Level.query.count(),
        'locations': Location.query.count(),
        'items': Item.query.count(),
    }
    return jsonify(stats)


@bp.route('/recent-items')
def get_recent_items():
    """Get recent items"""
    recent_items = Item.query.order_by(Item.created_at.desc()).limit(10).all()
    return jsonify({
        'items': [item.to_dict() for item in recent_items]
    })


@bp.route('/modules-summary')
def get_modules_summary():
    """Get modules summary"""
    modules = Module.query.order_by(Module.name).all()
    return jsonify({
        'modules': [module.to_dict() for module in modules]
    })
