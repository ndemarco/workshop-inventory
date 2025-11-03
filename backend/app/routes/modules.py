from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import db, Module, Level, Location

bp = Blueprint('modules', __name__)


@bp.route('/')
def list_modules():
    """List all modules"""
    modules = Module.query.order_by(Module.name).all()
    return render_template('modules/list.html', modules=modules)


@bp.route('/new', methods=['GET', 'POST'])
def new_module():
    """Create a new module"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        location_description = request.form.get('location_description')
        
        if not name:
            flash('Name is required', 'error')
            return render_template('modules/form.html')
        
        # Check if name already exists
        existing = Module.query.filter_by(name=name).first()
        if existing:
            flash(f'Module with name "{name}" already exists', 'error')
            return render_template('modules/form.html')
        
        module = Module(
            name=name,
            description=description,
            location_description=location_description
        )
        
        db.session.add(module)
        db.session.commit()
        
        flash(f'Module "{name}" created successfully', 'success')
        return redirect(url_for('modules.view_module', module_id=module.id))
    
    return render_template('modules/form.html')


@bp.route('/<int:module_id>')
def view_module(module_id):
    """View module details and its levels"""
    module = Module.query.get_or_404(module_id)
    levels = Level.query.filter_by(module_id=module_id).order_by(Level.level_number).all()
    return render_template('modules/view.html', module=module, levels=levels)


@bp.route('/<int:module_id>/edit', methods=['GET', 'POST'])
def edit_module(module_id):
    """Edit a module"""
    module = Module.query.get_or_404(module_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        location_description = request.form.get('location_description')
        
        if not name:
            flash('Name is required', 'error')
            return render_template('modules/form.html', module=module)
        
        # Check if name already exists (excluding current module)
        existing = Module.query.filter(Module.name == name, Module.id != module_id).first()
        if existing:
            flash(f'Module with name "{name}" already exists', 'error')
            return render_template('modules/form.html', module=module)
        
        module.name = name
        module.description = description
        module.location_description = location_description
        
        db.session.commit()
        
        flash(f'Module "{name}" updated successfully', 'success')
        return redirect(url_for('modules.view_module', module_id=module.id))
    
    return render_template('modules/form.html', module=module)


@bp.route('/<int:module_id>/delete', methods=['POST'])
def delete_module(module_id):
    """Delete a module"""
    module = Module.query.get_or_404(module_id)
    name = module.name
    
    db.session.delete(module)
    db.session.commit()
    
    flash(f'Module "{name}" deleted successfully', 'success')
    return redirect(url_for('modules.list_modules'))


@bp.route('/<int:module_id>/levels/new', methods=['GET', 'POST'])
def new_level(module_id):
    """Add a new level to a module"""
    module = Module.query.get_or_404(module_id)
    
    if request.method == 'POST':
        level_number = request.form.get('level_number', type=int)
        name = request.form.get('name')
        rows = request.form.get('rows', type=int, default=1)
        columns = request.form.get('columns', type=int, default=1)
        description = request.form.get('description')
        
        if not level_number:
            flash('Level number is required', 'error')
            return render_template('levels/form.html', module=module)
        
        # Check if level number already exists for this module
        existing = Level.query.filter_by(module_id=module_id, level_number=level_number).first()
        if existing:
            flash(f'Level {level_number} already exists in this module', 'error')
            return render_template('levels/form.html', module=module)
        
        level = Level(
            module_id=module_id,
            level_number=level_number,
            name=name,
            rows=rows,
            columns=columns,
            description=description
        )
        
        db.session.add(level)
        db.session.commit()
        
        # Create locations for this level
        create_locations_for_level(level)
        
        flash(f'Level {level_number} created with {rows}x{columns} locations', 'success')
        return redirect(url_for('modules.view_module', module_id=module_id))
    
    return render_template('levels/form.html', module=module)


@bp.route('/levels/<int:level_id>')
def view_level(level_id):
    """View level details with its locations"""
    level = Level.query.get_or_404(level_id)

    # Organize locations by row and column
    locations = Location.query.filter_by(level_id=level_id).all()
    location_grid = {}
    for loc in locations:
        if loc.row not in location_grid:
            location_grid[loc.row] = {}
        location_grid[loc.row][loc.column] = loc

    return render_template('levels/view.html', level=level, location_grid=location_grid, chr=chr)


@bp.route('/levels/<int:level_id>/edit', methods=['GET', 'POST'])
def edit_level(level_id):
    """Edit a level"""
    level = Level.query.get_or_404(level_id)
    module = level.module
    
    if request.method == 'POST':
        level_number = request.form.get('level_number', type=int)
        name = request.form.get('name')
        rows = request.form.get('rows', type=int, default=1)
        columns = request.form.get('columns', type=int, default=1)
        description = request.form.get('description')
        
        if not level_number:
            flash('Level number is required', 'error')
            return render_template('levels/form.html', module=module, level=level)
        
        # Check if level number already exists (excluding current level)
        existing = Level.query.filter(
            Level.module_id == level.module_id,
            Level.level_number == level_number,
            Level.id != level_id
        ).first()
        if existing:
            flash(f'Level {level_number} already exists in this module', 'error')
            return render_template('levels/form.html', module=module, level=level)
        
        # Check if grid size changed
        old_rows = level.rows
        old_columns = level.columns
        
        level.level_number = level_number
        level.name = name
        level.rows = rows
        level.columns = columns
        level.description = description
        
        db.session.commit()
        
        # If grid size changed, recreate locations
        if old_rows != rows or old_columns != columns:
            # Delete old locations (cascade will handle item_locations)
            Location.query.filter_by(level_id=level_id).delete()
            db.session.commit()
            
            # Create new locations
            create_locations_for_level(level)
            flash(f'Level updated and locations regenerated ({rows}x{columns})', 'success')
        else:
            flash(f'Level {level_number} updated successfully', 'success')
        
        return redirect(url_for('modules.view_level', level_id=level.id))
    
    return render_template('levels/form.html', module=module, level=level)


@bp.route('/levels/<int:level_id>/delete', methods=['POST'])
def delete_level(level_id):
    """Delete a level"""
    level = Level.query.get_or_404(level_id)
    module_id = level.module_id
    level_num = level.level_number
    
    db.session.delete(level)
    db.session.commit()
    
    flash(f'Level {level_num} deleted successfully', 'success')
    return redirect(url_for('modules.view_module', module_id=module_id))


def create_locations_for_level(level):
    """Helper function to create locations for a level based on its grid"""
    rows = level.rows
    columns = level.columns
    
    # Generate row labels (A, B, C... or 1, 2, 3...)
    row_labels = [chr(65 + i) for i in range(rows)] if rows <= 26 else [str(i+1) for i in range(rows)]
    
    # Generate column labels (1, 2, 3...)
    col_labels = [str(i+1) for i in range(columns)]
    
    locations = []
    for row_label in row_labels:
        for col_label in col_labels:
            location = Location(
                level_id=level.id,
                row=row_label,
                column=col_label,
                location_type='general'
            )
            locations.append(location)
    
    db.session.add_all(locations)
    db.session.commit()


# API endpoints for AJAX requests

@bp.route('/api/modules', methods=['GET'])
def api_list_modules():
    """API endpoint to list all modules"""
    modules = Module.query.order_by(Module.name).all()
    return jsonify([m.to_dict() for m in modules])


@bp.route('/api/modules/<int:module_id>', methods=['GET'])
def api_get_module(module_id):
    """API endpoint to get a single module"""
    module = Module.query.get_or_404(module_id)
    return jsonify(module.to_dict())


@bp.route('/api/modules/<int:module_id>/levels', methods=['GET'])
def api_list_levels(module_id):
    """API endpoint to list levels for a module"""
    levels = Level.query.filter_by(module_id=module_id).order_by(Level.level_number).all()
    return jsonify([l.to_dict() for l in levels])
