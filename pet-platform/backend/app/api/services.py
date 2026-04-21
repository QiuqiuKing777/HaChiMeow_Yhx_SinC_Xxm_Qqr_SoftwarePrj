from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import Service, ServiceSlot, User
from app.utils import role_required, paginate_query

services_bp = Blueprint('services', __name__, url_prefix='/api/services')


@services_bp.route('', methods=['GET'])
def list_services():
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    category = request.args.get('category', '')
    keyword  = request.args.get('keyword', '')

    query = Service.query.filter_by(status='online')
    if category:
        query = query.filter(Service.category == category)
    if keyword:
        query = query.filter(Service.service_name.ilike(f'%{keyword}%'))

    query = query.order_by(Service.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [s.to_dict() for s in result['items']]
    return jsonify(result), 200


@services_bp.route('/<int:service_id>', methods=['GET'])
def get_service(service_id):
    service = Service.query.get_or_404(service_id)
    data = service.to_dict()
    return jsonify(data), 200


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
    user_id  = get_jwt_identity()
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)

    query  = Service.query.filter_by(publisher_id=user_id).order_by(Service.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [s.to_dict() for s in result['items']]
    return jsonify(result), 200


@services_bp.route('', methods=['POST'])
@role_required('publisher')
def create_service():
    user_id = get_jwt_identity()
    data    = request.get_json() or {}

    if not data.get('service_name') or data.get('price') is None:
        return jsonify({'error': 'service_name 和 price 不能为空'}), 400

    service = Service(
        publisher_id=user_id,
        service_name=data['service_name'],
        category=data.get('category'),
        description=data.get('description'),
        price=data['price'],
        cover_image=data.get('cover_image'),
        duration=data.get('duration'),
        location=data.get('location'),
        status='online',
    )
    db.session.add(service)
    db.session.flush()

    for slot in data.get('slots', []):
        db.session.add(ServiceSlot(
            service_id=service.service_id,
            slot_date=slot.get('slot_date'),
            slot_time=slot.get('slot_time'),
            capacity=slot.get('capacity', 5),
        ))

    db.session.commit()
    return jsonify({'message': '服务发布成功', 'service': service.to_dict()}), 201


@services_bp.route('/<int:service_id>', methods=['PUT'])
@jwt_required()
def update_service(service_id):
    user_id = get_jwt_identity()
    user    = User.query.get(user_id)
    service = Service.query.get_or_404(service_id)

    if service.publisher_id != user_id and user.role_type != 'admin':
        return jsonify({'error': '无权操作'}), 403

    data = request.get_json() or {}
    for field in ['service_name', 'category', 'description', 'price', 'cover_image', 'duration', 'location', 'status']:
        if field in data:
            setattr(service, field, data[field])
    db.session.commit()
    return jsonify({'message': '更新成功', 'service': service.to_dict()}), 200


@services_bp.route('/<int:service_id>/slots', methods=['POST'])
@role_required('publisher')
def add_slot(service_id):
    user_id = get_jwt_identity()
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
