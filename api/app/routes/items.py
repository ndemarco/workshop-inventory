from flask import Blueprint, request, jsonify, send_file
from app.models import db, Item, ItemLocation, Location
from app.services.duplicate_detector import DuplicateDetector
from app.services.spec_parser import SpecificationParser
import qrcode
from io import BytesIO
import secrets

bp = Blueprint('items', __name__)

def sanitize_tags(tags):
    if isinstance(tags, str):
        return [t.strip() for t in tags.split(',') if t.strip()]
    if isinstance(tags, list):
        return [str(t).strip() for t in tags if str(t).strip()]
    return []

@bp.route('', methods=['GET'])
def list_items():
    category = request.args.get('category')
    search = request.args.get('search')
    location_id = request.args.get('location_id', type=int)

    query = Item.query
    if category:
        query = query.filter(Item.category == category)
    if search:
        term = f"%{search}%"
        query = query.filter(
            db.or_(
                Item.name.ilike(term),
                Item.description.ilike(term),
                Item.tags.cast(db.String).ilike(term)
            )
        )
    if location_id:
        query = query.join(ItemLocation).filter(ItemLocation.location_id == location_id)

    items = query.order_by(Item.name).all()
    categories = [c[0] for c in db.session.query(Item.category).distinct().filter(Item.category.isnot(None)).all()]
    return jsonify({'items':[i.to_dict() for i in items],'categories':categories,'total':len(items)})

@bp.route('/count', methods=['GET'])
def get_item_count():
    return jsonify({'count': Item.query.count()})

@bp.route('/existing-values', methods=['GET'])
def get_existing_values():
    categories = [c[0] for c in db.session.query(Item.category).distinct().filter(Item.category.isnot(None)).all()]
    item_types = [t[0] for t in db.session.query(Item.item_type).distinct().filter(Item.item_type.isnot(None)).all()]
    units = [u[0] for u in db.session.query(Item.unit).distinct().filter(Item.unit.isnot(None)).all()]

    # defaults if empty
    if not categories: categories = ['Hardware','Electronics','Chemicals']
    if not item_types: item_types = ['Raw Material','Finished Product']
    if not units: units = ['pieces','meters','kg','liters']

    return jsonify({'success':True,'data':{'categories':categories,'itemTypes':item_types,'units':units}})

@bp.route('', methods=['POST'])
def create_item():
    data = request.get_json() or request.form
    item = Item(
        name=data.get('name'),
        description=data.get('description'),
        category=data.get('category'),
        item_type=data.get('item_type'),
        tags=sanitize_tags(data.get('tags','')),
        notes=data.get('notes',''),
        quantity=int(data.get('quantity',0)),
        unit=data.get('unit','pieces')
    )
    db.session.add(item)
    db.session.flush()
    location_id = int(data.get('location_id') or 0)
    if location_id:
        db.session.add(ItemLocation(item_id=item.id, location_id=location_id))
    db.session.commit()
    return jsonify({'id':item.id,'message':f'Item "{item.name}" created successfully','item':item.to_dict()}),201

@bp.route('/<int:item_id>', methods=['GET'])
def get_item(item_id):
    return jsonify(Item.query.get_or_404(item_id).to_dict())

@bp.route('/<int:item_id>', methods=['POST','PUT'])
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    data = request.get_json() or request.form
    item.name = data.get('name', item.name)
    item.description = data.get('description', item.description)
    item.category = data.get('category', item.category)
    item.item_type = data.get('item_type', item.item_type)
    item.notes = data.get('notes', item.notes)
    item.quantity = int(data.get('quantity', item.quantity))
    item.unit = data.get('unit', item.unit)
    item.tags = sanitize_tags(data.get('tags', item.tags))
    db.session.commit()
    return jsonify({'message':f'Item "{item.name}" updated successfully','item':item.to_dict()})

@bp.route('/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message':f'Item "{item.name}" deleted successfully'})

@bp.route('/<int:item_id>/locations/add', methods=['POST'])
def add_location(item_id):
    item = Item.query.get_or_404(item_id)
    data = request.get_json() or request.form
    location_id = int(data.get('location_id'))
    if ItemLocation.query.filter_by(item_id=item_id, location_id=location_id).first():
        return jsonify({'error':'Item already stored at this location'}),400
    il = ItemLocation(item_id=item_id, location_id=location_id, notes=data.get('notes',''))
    db.session.add(il)
    db.session.commit()
    return jsonify({'message':f'Location {Location.query.get(location_id).full_address()} added','item_location':il.to_dict()}),201

@bp.route('/<int:item_id>/locations/<int:item_location_id>', methods=['DELETE'])
def remove_location(item_id,item_location_id):
    il = ItemLocation.query.get_or_404(item_location_id)
    if il.item_id!=item_id: return jsonify({'error':'Item location mismatch'}),400
    addr = il.location.full_address()
    db.session.delete(il)
    db.session.commit()
    return jsonify({'message':f'Location {addr} removed successfully'})

@bp.route('/check-duplicates', methods=['POST'])
def check_duplicates():
    data = request.get_json()
    detector = DuplicateDetector()
    tags = sanitize_tags(data.get('tags',''))
    matches = detector.find_similar(
        name=data.get('name',''),
        description=data.get('description',''),
        category=data.get('category',''),
        tags=tags,
        threshold=float(data.get('threshold',0.7))
    ) if data.get('name') and data.get('description') else []
    return jsonify({'has_duplicates':len(matches)>0,'matches':[m.to_dict() for m in matches],'total':len(matches)})

@bp.route('/extract-specs', methods=['POST'])
def extract_specs():
    data = request.get_json()
    if not data.get('description'): return jsonify({'error':'Description is required'}),400
    parsed = SpecificationParser().parse(data.get('description'), data.get('name',''))
    return jsonify({'category':parsed.category,'specs':parsed.specs,'tags':parsed.tags,'confidence':parsed.confidence})

@bp.route('/<int:item_id>/qr/generate', methods=['POST'])
def generate_qr_code(item_id):
    item = Item.query.get_or_404(item_id)
    if not item.qr_code:
        while True:
            code=f"INV-{secrets.token_urlsafe(12)}"
            if not Item.query.filter_by(qr_code=code).first():
                item.qr_code=code
                break
        db.session.commit()
        return jsonify({'message':f'QR code generated for "{item.name}"','qr_code':item.qr_code}),201
    return jsonify({'message':f'QR code already exists for "{item.name}"','qr_code':item.qr_code})

@bp.route('/<int:item_id>/qr/download')
def download_qr_code(item_id):
    item = Item.query.get_or_404(item_id)
    if not item.qr_code: return jsonify({'error':'No QR code exists'}),400
    qr=qrcode.QRCode(version=1,error_correction=qrcode.constants.ERROR_CORRECT_L,box_size=10,border=4)
    qr.add_data(f"/item/{item.id}"); qr.make(fit=True)
    img=qr.make_image(fill_color="black",back_color="white")
    bio=BytesIO(); img.save(bio,'PNG'); bio.seek(0)
    safe_name="".join(c for c in item.name if c.isalnum() or c in (' ','-','_')).strip()
    return send_file(bio,mimetype='image/png',as_attachment=True,download_name=f"QR_{safe_name}_{item.id}.png")

@bp.route('/qr/scan/<qr_code>')
def scan_qr_code(qr_code):
    item = Item.query.filter_by(qr_code=qr_code).first()
    if not item: return jsonify({'error':f'No item found with QR code: {qr_code}'}),404
    return jsonify({'message':'Found item from QR code!','item':item.to_dict()})
