"""
Admin routes for system maintenance and data processing
"""
from flask import Blueprint, render_template, flash, redirect, url_for, jsonify
from app.models import db, Item, DuplicateCandidate
from app.services.embedding_service import embedding_service
from datetime import datetime

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
def index():
    """Admin dashboard with system maintenance controls"""

    # Get statistics
    total_items = Item.query.count()
    items_with_embeddings = Item.query.filter(Item.embedding.isnot(None)).count()
    items_without_embeddings = total_items - items_with_embeddings

    pending_duplicates = DuplicateCandidate.query.filter_by(status='pending').count()

    stats = {
        'total_items': total_items,
        'items_with_embeddings': items_with_embeddings,
        'items_without_embeddings': items_without_embeddings,
        'pending_duplicates': pending_duplicates
    }

    return render_template('admin/index.html', stats=stats)


@bp.route('/process-embeddings', methods=['POST'])
def process_embeddings():
    """Generate embeddings for all items that don't have them"""

    try:
        # Get all items without embeddings
        items_without_embeddings = Item.query.filter(Item.embedding.is_(None)).all()

        if not items_without_embeddings:
            flash('All items already have embeddings!', 'info')
            return redirect(url_for('admin.index'))

        processed_count = 0
        error_count = 0

        for item in items_without_embeddings:
            try:
                # Generate embedding from description
                if item.description:
                    embedding = embedding_service.generate_embedding(item.description)
                    item.embedding = embedding
                    processed_count += 1
                else:
                    error_count += 1
            except Exception as e:
                print(f"Error generating embedding for item {item.id}: {str(e)}")
                error_count += 1

        # Commit all changes
        db.session.commit()

        flash(f'Successfully generated embeddings for {processed_count} items. {error_count} errors.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error processing embeddings: {str(e)}', 'error')

    return redirect(url_for('admin.index'))


@bp.route('/detect-duplicates', methods=['POST'])
def detect_duplicates():
    """Scan all items and detect potential duplicates"""

    try:
        # Get all items with embeddings
        items_with_embeddings = Item.query.filter(Item.embedding.isnot(None)).all()

        if len(items_with_embeddings) < 2:
            flash('Need at least 2 items with embeddings to detect duplicates.', 'warning')
            return redirect(url_for('admin.index'))

        # Clear existing pending duplicate candidates to avoid re-processing
        DuplicateCandidate.query.filter_by(status='pending').delete()

        duplicate_count = 0

        for item in items_with_embeddings:
            try:
                # Find similar items (threshold 0.85)
                similar_items = embedding_service.find_duplicates_for_item(item, threshold=0.85)

                print(f"DEBUG: Item {item.id} ({item.name[:50]}...) found {len(similar_items)} similar items")
                for similar_item, similarity in similar_items:
                    print(f"  - Similar to item {similar_item.id} with similarity {similarity:.3f}")

                for similar_item, similarity in similar_items:
                    # Check if this pair already exists (in either direction)
                    existing = DuplicateCandidate.query.filter(
                        db.or_(
                            db.and_(
                                DuplicateCandidate.item1_id == item.id,
                                DuplicateCandidate.item2_id == similar_item.id
                            ),
                            db.and_(
                                DuplicateCandidate.item1_id == similar_item.id,
                                DuplicateCandidate.item2_id == item.id
                            )
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
                print(f"Error detecting duplicates for item {item.id}: {str(e)}")
                import traceback
                traceback.print_exc()

        db.session.commit()

        flash(f'Duplicate detection complete! Found {duplicate_count} potential duplicate pairs.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error detecting duplicates: {str(e)}', 'error')
        import traceback
        traceback.print_exc()

    return redirect(url_for('admin.index'))


@bp.route('/clear-embeddings', methods=['POST'])
def clear_embeddings():
    """Clear all embeddings (for testing/debugging)"""

    try:
        Item.query.update({Item.embedding: None})
        db.session.commit()

        flash('All embeddings have been cleared.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error clearing embeddings: {str(e)}', 'error')

    return redirect(url_for('admin.index'))
