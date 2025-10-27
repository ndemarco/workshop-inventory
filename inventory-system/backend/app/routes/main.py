from flask import Blueprint, render_template
from app.models import Module, Level, Location, Item

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Main dashboard"""
    stats = {
        'modules': Module.query.count(),
        'levels': Level.query.count(),
        'locations': Location.query.count(),
        'items': Item.query.count(),
    }
    
    recent_items = Item.query.order_by(Item.created_at.desc()).limit(10).all()
    modules = Module.query.order_by(Module.name).all()
    
    return render_template('index.html', stats=stats, recent_items=recent_items, modules=modules)


@bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')
