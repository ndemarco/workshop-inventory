from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import db, DuplicateCandidate, Item, ItemLocation
from datetime import datetime

bp = Blueprint('duplicates', __name__, url_prefix='/duplicates')


@bp.route('/')
def list_duplicates():
    """List all pending duplicate candidates"""
    status_filter = request.args.get('status', 'pending')

    query = DuplicateCandidate.query

    if status_filter and status_filter != 'all':
        query = query.filter(DuplicateCandidate.status == status_filter)

    duplicates = query.order_by(
        DuplicateCandidate.similarity_score.desc(),
        DuplicateCandidate.created_at.desc()
    ).all()

    # Count by status
    stats = {
        'pending': DuplicateCandidate.query.filter_by(status='pending').count(),
        'merged': DuplicateCandidate.query.filter_by(status='merged').count(),
        'dismissed': DuplicateCandidate.query.filter_by(status='dismissed').count(),
        'total': DuplicateCandidate.query.count()
    }

    return render_template('duplicates/list.html', duplicates=duplicates, stats=stats, status_filter=status_filter)


@bp.route('/<int:duplicate_id>')
def view_duplicate(duplicate_id):
    """View details of a duplicate candidate pair"""
    duplicate = DuplicateCandidate.query.get_or_404(duplicate_id)

    # Check if both items still exist
    if not duplicate.item1 or not duplicate.item2:
        # One or both items were deleted - auto-delete this orphaned duplicate candidate
        missing_items = []
        if not duplicate.item1:
            missing_items.append(f"item {duplicate.item1_id}")
        if not duplicate.item2:
            missing_items.append(f"item {duplicate.item2_id}")

        db.session.delete(duplicate)
        db.session.commit()

        flash(f'This duplicate candidate was deleted because {" and ".join(missing_items)} no longer exist(s).', 'warning')
        return redirect(url_for('duplicates.list_duplicates'))

    return render_template('duplicates/view.html', duplicate=duplicate)


@bp.route('/<int:duplicate_id>/merge', methods=['POST'])
def merge_duplicate(duplicate_id):
    """Merge duplicate items - keep one, delete the other"""
    duplicate = DuplicateCandidate.query.get_or_404(duplicate_id)

    if duplicate.status != 'pending':
        flash('This duplicate has already been resolved', 'warning')
        return redirect(url_for('duplicates.list_duplicates'))

    # Get which item to keep
    keep_id = request.form.get('keep_id', type=int)

    # Validate that the selected item is one of the two in this duplicate
    if keep_id not in [duplicate.item1_id, duplicate.item2_id]:
        flash('Invalid item selection', 'error')
        return redirect(url_for('duplicates.view_duplicate', duplicate_id=duplicate_id))

    # Calculate which item to delete (the one that wasn't selected to keep)
    if keep_id == duplicate.item1_id:
        delete_id = duplicate.item2_id
    else:
        delete_id = duplicate.item1_id

    keep_item = Item.query.get(keep_id)
    delete_item = Item.query.get(delete_id)

    if not keep_item or not delete_item:
        flash('Item not found', 'error')
        return redirect(url_for('duplicates.view_duplicate', duplicate_id=duplicate_id))

    # Transfer locations from deleted item to kept item
    for item_location in delete_item.item_locations:
        # Check if kept item already has this location
        existing = ItemLocation.query.filter_by(
            item_id=keep_id,
            location_id=item_location.location_id
        ).first()

        if not existing:
            # Transfer the location
            item_location.item_id = keep_id
        else:
            # Location already exists, just delete this one
            db.session.delete(item_location)

    # Delete the duplicate item
    deleted_name = delete_item.name

    # Delete ALL duplicate candidates involving the deleted item (including the current one)
    # We need to delete them (not just update status) to avoid foreign key constraint violations
    all_duplicates = DuplicateCandidate.query.filter(
        db.or_(
            DuplicateCandidate.item1_id == delete_id,
            DuplicateCandidate.item2_id == delete_id
        )
    ).all()

    print(f"DEBUG: Deleting item {delete_id} ({deleted_name})")
    print(f"DEBUG: Found {len(all_duplicates)} duplicate candidates to delete:")
    for dup in all_duplicates:
        print(f"  - Duplicate #{dup.id}: item {dup.item1_id} <-> item {dup.item2_id}")
        db.session.delete(dup)

    # Now we can safely delete the item
    db.session.delete(delete_item)

    db.session.commit()

    flash(f'Items merged successfully. Kept "{keep_item.name}", deleted "{deleted_name}"', 'success')
    return redirect(url_for('duplicates.list_duplicates'))


@bp.route('/<int:duplicate_id>/dismiss', methods=['POST'])
def dismiss_duplicate(duplicate_id):
    """Dismiss a duplicate candidate (not actually duplicates)"""
    duplicate = DuplicateCandidate.query.get_or_404(duplicate_id)

    if duplicate.status != 'pending':
        flash('This duplicate has already been resolved', 'warning')
        return redirect(url_for('duplicates.list_duplicates'))

    notes = request.form.get('notes', '')

    duplicate.status = 'dismissed'
    duplicate.resolved_at = datetime.utcnow()
    duplicate.notes = notes

    db.session.commit()

    flash('Duplicate dismissed successfully', 'success')
    return redirect(url_for('duplicates.list_duplicates'))


@bp.route('/<int:duplicate_id>/reopen', methods=['POST'])
def reopen_duplicate(duplicate_id):
    """Reopen a resolved duplicate candidate"""
    duplicate = DuplicateCandidate.query.get_or_404(duplicate_id)

    if duplicate.status == 'pending':
        flash('This duplicate is already pending', 'warning')
        return redirect(url_for('duplicates.list_duplicates'))

    duplicate.status = 'pending'
    duplicate.resolved_at = None

    db.session.commit()

    flash('Duplicate reopened successfully', 'success')
    return redirect(url_for('duplicates.view_duplicate', duplicate_id=duplicate_id))


# API endpoints

@bp.route('/api/list', methods=['GET'])
def api_list_duplicates():
    """API endpoint to list duplicate candidates"""
    status = request.args.get('status', 'pending')

    query = DuplicateCandidate.query

    if status and status != 'all':
        query = query.filter(DuplicateCandidate.status == status)

    duplicates = query.order_by(
        DuplicateCandidate.similarity_score.desc()
    ).all()

    return jsonify({
        'count': len(duplicates),
        'duplicates': [d.to_dict() for d in duplicates]
    })


@bp.route('/api/<int:duplicate_id>', methods=['GET'])
def api_get_duplicate(duplicate_id):
    """API endpoint to get a single duplicate candidate"""
    duplicate = DuplicateCandidate.query.get_or_404(duplicate_id)
    return jsonify(duplicate.to_dict())
