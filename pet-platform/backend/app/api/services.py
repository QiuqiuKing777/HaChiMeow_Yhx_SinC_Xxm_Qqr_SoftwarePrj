import uuid
from pathlib import Path

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Service, ServiceSlot, User
from app.utils import role_required, paginate_query

services_bp = Blueprint('services', __name__, url_prefix='/api/services')

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg'}


def allowed_image_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def build_full_image_url(path):
    if not path:
        return None

    base = request.host_url.rstrip('/')

    if path.startswith('http://') or path.startswith('https://'):
        return path

    if path == 'NKU.png':
        return f'{base}/NKU.png'

    if path == '/NKU.png':
        return f'{base}/NKU.png'

    if path.startswith('/static/'):
        return f'{base}{path}'

    if path.startswith('uploads/'):
        return f'{base}/static/{path}'

    if path.startswith('/'):
        return f'{base}{path}'

    return f'{base}/{path}'


def serialize_service(service):
    data = service.to_dict()
    data['cover_image'] = build_full_image_url(data.get('cover_image'))
    return data


def save_uploaded_service_image(file_storage):
    if not file_storage or not file_storage.filename:
        return None

    filename = secure_filename(file_storage.filename)
    if not filename:
        return None

    if not allowed_image_file(filename):
        raise ValueError('仅支持 PNG、JPG、JPEG、SVG 格式图片')

    ext = filename.rsplit('.', 1)[1].lower()
    new_filename = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = Path(current_app.static_folder) / 'uploads' / 'services'
    upload_dir.mkdir(parents=True, exist_ok=True)

    save_path = upload_dir / new_filename
    file_storage.save(save_path)

    return f"/static/uploads/services/{new_filename}"


def get_request_data():
    if request.content_type and 'multipart/form-data' in request.content_type:
        return request.form.to_dict()
    return request.get_json(silent=True) or {}


@services_bp.route('', methods=['GET'])
def list_services():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    category = request.args.get('category', '')
    keyword = request.args.get('keyword', '')

    query = Service.query.filter_by(status='online')
    if category:
        query = query.filter(Service.category == category)
    if keyword:
        query = query.filter(Service.service_name.ilike(f'%{keyword}%'))

    query = query.order_by(Service.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [serialize_service(s) for s in result['items']]
    return jsonify(result), 200


@services_bp.route('/<int:service_id>', methods=['GET'])
def get_service(service_id):
    service = Service.query.get_or_404(service_id)
    return jsonify(serialize_service(service)), 200


@services_bp.route('/<int:service_id>/slots', methods=['GET'])
def get_slots(service_id):
    Service.query.get_or_404(service_id)
    slots = ServiceSlot.query.filter_by(service_id=service_id).order_by(
        ServiceSlot.slot_date, ServiceSlot.slot_time
    ).all()
    return jsonify([s.to_dict() for s in slots]), 200


@services_bp.route('/my', methods=['GET'])
@role_required('publisher')
def my_services():
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)

    query = Service.query.filter_by(publisher_id=user_id).order_by(Service.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [serialize_service(s) for s in result['items']]
    return jsonify(result), 200


@services_bp.route('', methods=['POST'])
@role_required('publisher')
def create_service():
    user_id = int(get_jwt_identity())
    data = get_request_data()

    if not str(data.get('service_name', '')).strip() or str(data.get('price', '')).strip() == '':
        return jsonify({'error': 'service_name 和 price 不能为空'}), 400

    try:
        price = float(data['price'])
    except (TypeError, ValueError):
        return jsonify({'error': 'price 格式不正确'}), 400

    if price < 0:
        return jsonify({'error': 'price 不能小于0'}), 400

    image_file = request.files.get('image')
    cover_image = data.get('cover_image')

    try:
        if image_file:
            cover_image = save_uploaded_service_image(image_file)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    service = Service(
        publisher_id=user_id,
        service_name=data['service_name'].strip(),
        category=data.get('category'),
        description=data.get('description'),
        price=price,
        cover_image=cover_image,
        duration=data.get('duration'),
        location=data.get('location'),
        status='online',
    )
    db.session.add(service)
    db.session.flush()

    slots = request.form.getlist('slots') if request.form else data.get('slots', [])
    if isinstance(slots, list):
        for slot in slots:
            if isinstance(slot, dict):
                db.session.add(ServiceSlot(
                    service_id=service.service_id,
                    slot_date=slot.get('slot_date'),
                    slot_time=slot.get('slot_time'),
                    capacity=slot.get('capacity', 5),
                ))

    db.session.commit()
    return jsonify({'message': '服务发布成功', 'service': serialize_service(service)}), 201


@services_bp.route('/<int:service_id>', methods=['PUT'])
@jwt_required()
def update_service(service_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    service = Service.query.get_or_404(service_id)

    if service.publisher_id != user_id and user.role_type != 'admin':
        return jsonify({'error': '无权操作'}), 403

    data = get_request_data()
    image_file = request.files.get('image')

    for field in ['service_name', 'category', 'description', 'cover_image', 'duration', 'location', 'status']:
        if field in data and data[field] is not None:
            setattr(service, field, data[field])

    if 'price' in data:
        try:
            price = float(data['price'])
            if price < 0:
                return jsonify({'error': 'price 不能小于0'}), 400
            service.price = price
        except (TypeError, ValueError):
            return jsonify({'error': 'price 格式不正确'}), 400

    try:
        if image_file:
            new_cover = save_uploaded_service_image(image_file)
            service.cover_image = new_cover
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    db.session.commit()
    return jsonify({'message': '更新成功', 'service': serialize_service(service)}), 200


@services_bp.route('/<int:service_id>/slots', methods=['POST'])
@role_required('publisher')
def add_slot(service_id):
    user_id = int(get_jwt_identity())
    service = Service.query.get_or_404(service_id)

    if service.publisher_id != user_id:
        return jsonify({'error': '无权操作'}), 403

    data = request.get_json() or {}
    slot = ServiceSlot(
        service_id=service_id,
        slot_date=data.get('slot_date'),
        slot_time=data.get('slot_time'),
        capacity=data.get('capacity', 5),
    )
    db.session.add(slot)
    db.session.commit()
    return jsonify({'message': '时段已添加', 'slot': slot.to_dict()}), 201
