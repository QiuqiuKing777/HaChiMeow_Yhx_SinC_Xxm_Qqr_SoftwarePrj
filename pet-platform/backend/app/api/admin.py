from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models import (
    User,
    Pet,
    Product,
    Service,
    Order,
    Booking,
    AdoptionApplication,
    OperationLog,
    Complaint,
)
from app.utils import role_required, paginate_query

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def build_full_image_url(path):
    if not path:
        return None

    base = request.host_url.rstrip('/')

    if path.startswith('http://') or path.startswith('https://'):
        return path
    if path in ('NKU.png', '/NKU.png'):
        return f'{base}/NKU.png'
    if path.startswith('/static/'):
        return f'{base}{path}'
    if path.startswith('uploads/'):
        return f'{base}/static/{path}'
    if path.startswith('/'):
        return f'{base}{path}'
    return f'{base}/{path}'


def serialize_admin_pet(pet):
    data = pet.to_dict()
    data['cover_image'] = build_full_image_url(data.get('cover_image'))
    images = data.get('images') or []
    for img in images:
        img['image_url'] = build_full_image_url(img.get('image_url'))
    return data


def serialize_admin_product(product):
    data = product.to_dict()
    data['cover_image'] = build_full_image_url(data.get('cover_image'))
    images = data.get('images') or []
    for img in images:
        img['image_url'] = build_full_image_url(img.get('image_url'))
    data['publisher'] = product.publisher.to_public_dict() if product.publisher else None
    return data


def serialize_admin_service(service):
    data = service.to_dict()
    data['cover_image'] = build_full_image_url(data.get('cover_image'))
    return data


@admin_bp.route('/users', methods=['GET'])
@role_required('admin')
def list_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    role_type = request.args.get('role_type', '')
    keyword = request.args.get('keyword', '')
    status = request.args.get('status', '')

    query = User.query
    if role_type:
        query = query.filter(User.role_type == role_type)
    if status:
        query = query.filter(User.status == status)
    if keyword:
        query = query.filter(
            User.username.ilike(f'%{keyword}%') | User.nickname.ilike(f'%{keyword}%')
        )
    query = query.order_by(User.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [user.to_dict() for user in result['items']]
    return jsonify(result), 200


@admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@role_required('admin')
def set_user_status(user_id):
    operator_id = int(get_jwt_identity())
    data = request.get_json() or {}
    status = data.get('status')
    if status not in ('active', 'disabled'):
        return jsonify({'error': 'status must be active or disabled'}), 400

    user = User.query.get_or_404(user_id)
    if user.role_type == 'admin':
        return jsonify({'error': 'cannot modify admin status'}), 403

    user.status = status
    db.session.add(OperationLog(
        operator_id=operator_id,
        action='set_user_status',
        target_type='user',
        target_id=user_id,
        detail=f'status={status}',
        ip_address=request.remote_addr,
    ))
    db.session.commit()
    return jsonify({'message': 'user status updated', 'user': user.to_dict()}), 200


@admin_bp.route('/pets', methods=['GET'])
@role_required('admin')
def admin_list_pets():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')
    keyword = request.args.get('keyword', '')

    query = Pet.query
    if status:
        query = query.filter(Pet.status == status)
    else:
        query = query.filter(Pet.status != 'offline')
    if keyword:
        query = query.filter(
            Pet.pet_name.ilike(f'%{keyword}%') |
            Pet.species.ilike(f'%{keyword}%') |
            Pet.breed.ilike(f'%{keyword}%')
        )
    query = query.order_by(Pet.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [serialize_admin_pet(pet) for pet in result['items']]
    return jsonify(result), 200


@admin_bp.route('/pets/<int:pet_id>/status', methods=['PUT'])
@role_required('admin')
def set_pet_status(pet_id):
    operator_id = int(get_jwt_identity())
    data = request.get_json() or {}
    status = data.get('status')
    if status not in ('online', 'offline', 'pending'):
        return jsonify({'error': 'invalid status'}), 400

    pet = Pet.query.get_or_404(pet_id)
    pet.status = status
    db.session.add(OperationLog(
        operator_id=operator_id,
        action='set_pet_status',
        target_type='pet',
        target_id=pet_id,
        detail=f'status={status}',
        ip_address=request.remote_addr,
    ))
    db.session.commit()
    return jsonify({'message': 'pet status updated', 'pet': serialize_admin_pet(pet)}), 200


@admin_bp.route('/products', methods=['GET'])
@role_required('admin')
def admin_list_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')
    keyword = request.args.get('keyword', '')

    query = Product.query
    if status:
        query = query.filter(Product.status == status)
    else:
        query = query.filter(Product.status != 'offline')
    if keyword:
        query = query.filter(
            Product.product_name.ilike(f'%{keyword}%') |
            Product.category.ilike(f'%{keyword}%')
        )
    query = query.order_by(Product.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [serialize_admin_product(product) for product in result['items']]
    return jsonify(result), 200


@admin_bp.route('/products/<int:product_id>/status', methods=['PUT'])
@role_required('admin')
def set_product_status(product_id):
    operator_id = int(get_jwt_identity())
    data = request.get_json() or {}
    status = data.get('status')
    if status not in ('online', 'offline', 'pending'):
        return jsonify({'error': 'invalid status'}), 400

    product = Product.query.get_or_404(product_id)
    product.status = status
    db.session.add(OperationLog(
        operator_id=operator_id,
        action='set_product_status',
        target_type='product',
        target_id=product_id,
        detail=f'status={status}',
        ip_address=request.remote_addr,
    ))
    db.session.commit()
    return jsonify({'message': 'product status updated', 'product': serialize_admin_product(product)}), 200


@admin_bp.route('/services', methods=['GET'])
@role_required('admin')
def admin_list_services():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')
    keyword = request.args.get('keyword', '')

    query = Service.query
    if status:
        query = query.filter(Service.status == status)
    else:
        query = query.filter(Service.status != 'offline')
    if keyword:
        query = query.filter(
            Service.service_name.ilike(f'%{keyword}%') |
            Service.category.ilike(f'%{keyword}%') |
            Service.location.ilike(f'%{keyword}%')
        )
    query = query.order_by(Service.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [serialize_admin_service(service) for service in result['items']]
    return jsonify(result), 200


@admin_bp.route('/services/<int:service_id>/status', methods=['PUT'])
@role_required('admin')
def set_service_status(service_id):
    operator_id = int(get_jwt_identity())
    data = request.get_json() or {}
    status = data.get('status')
    if status not in ('online', 'offline', 'pending'):
        return jsonify({'error': 'invalid status'}), 400

    service = Service.query.get_or_404(service_id)
    service.status = status
    db.session.add(OperationLog(
        operator_id=operator_id,
        action='set_service_status',
        target_type='service',
        target_id=service_id,
        detail=f'status={status}',
        ip_address=request.remote_addr,
    ))
    db.session.commit()
    return jsonify({'message': 'service status updated', 'service': serialize_admin_service(service)}), 200


@admin_bp.route('/orders', methods=['GET'])
@role_required('admin')
def admin_list_orders():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pay_status = request.args.get('pay_status', '')
    keyword = request.args.get('keyword', '')

    query = Order.query
    if pay_status:
        query = query.filter(Order.pay_status == pay_status)
    if keyword:
        query = query.join(User, Order.buyer_id == User.user_id).filter(
            User.username.ilike(f'%{keyword}%') | User.nickname.ilike(f'%{keyword}%')
        )
    query = query.order_by(Order.created_at.desc())
    result = paginate_query(query, page, per_page)
    items = []
    for order in result['items']:
        data = order.to_dict()
        data['buyer'] = order.buyer.to_public_dict() if order.buyer else None
        items.append(data)
    result['items'] = items
    return jsonify(result), 200


@admin_bp.route('/bookings', methods=['GET'])
@role_required('admin')
def admin_list_bookings():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')

    query = Booking.query
    if status:
        query = query.filter(Booking.booking_status == status)
    query = query.order_by(Booking.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [booking.to_dict() for booking in result['items']]
    return jsonify(result), 200


@admin_bp.route('/adoptions', methods=['GET'])
@role_required('admin')
def admin_list_adoptions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')

    query = AdoptionApplication.query
    if status:
        query = query.filter(AdoptionApplication.review_status == status)
    query = query.order_by(AdoptionApplication.submitted_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [application.to_dict() for application in result['items']]
    return jsonify(result), 200


@admin_bp.route('/complaints', methods=['GET'])
@role_required('admin')
def admin_list_complaints():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')

    query = Complaint.query
    if status:
        query = query.filter(Complaint.status == status)
    query = query.order_by(Complaint.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [complaint.to_dict() for complaint in result['items']]
    return jsonify(result), 200


@admin_bp.route('/complaints/<int:complaint_id>/handle', methods=['PUT'])
@role_required('admin')
def handle_complaint(complaint_id):
    operator_id = int(get_jwt_identity())
    data = request.get_json() or {}
    status = data.get('status')
    admin_reply = data.get('admin_reply', '')

    if status not in ('handling', 'resolved', 'closed'):
        return jsonify({'error': 'status must be handling/resolved/closed'}), 400

    complaint = Complaint.query.get_or_404(complaint_id)
    complaint.status = status
    complaint.admin_reply = admin_reply
    complaint.handled_by = operator_id
    complaint.handled_at = datetime.utcnow()
    db.session.add(OperationLog(
        operator_id=operator_id,
        action='handle_complaint',
        target_type='complaint',
        target_id=complaint_id,
        detail=f'status={status}',
        ip_address=request.remote_addr,
    ))
    db.session.commit()
    return jsonify({'message': 'complaint handled', 'complaint': complaint.to_dict()}), 200


@admin_bp.route('/stats', methods=['GET'])
@role_required('admin')
def get_stats():
    from sqlalchemy import func, cast, Date as SADate, text

    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')

    start_dt = None
    end_dt = None
    try:
        if start_date_str:
            start_dt = datetime.strptime(start_date_str, '%Y-%m-%d')
        if end_date_str:
            end_dt = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
    except ValueError:
        return jsonify({'error': 'invalid date format, use YYYY-MM-DD'}), 400

    def date_filter(query, col):
        if start_dt:
            query = query.filter(col >= start_dt)
        if end_dt:
            query = query.filter(col <= end_dt)
        return query

    stats = {
        'date_range': {
            'start_date': start_date_str or None,
            'end_date': end_date_str or None,
        },
        'users': {
            'total': User.query.count(),
            'user': User.query.filter_by(role_type='user').count(),
            'publisher': User.query.filter_by(role_type='publisher').count(),
            'disabled': User.query.filter_by(status='disabled').count(),
        },
        'pets': {
            'total': Pet.query.count(),
            'online': Pet.query.filter_by(status='online').count(),
            'adopted': Pet.query.filter_by(status='adopted').count(),
            'pending': Pet.query.filter_by(status='pending').count(),
            'offline': Pet.query.filter_by(status='offline').count(),
        },
        'products': {
            'total': Product.query.count(),
            'online': Product.query.filter_by(status='online').count(),
            'offline': Product.query.filter_by(status='offline').count(),
            'pending': Product.query.filter_by(status='pending').count(),
        },
        'services': {
            'total': Service.query.count(),
            'online': Service.query.filter_by(status='online').count(),
            'offline': Service.query.filter_by(status='offline').count(),
            'pending': Service.query.filter_by(status='pending').count(),
        },
        'orders': {
            'total': date_filter(Order.query, Order.created_at).count(),
            'pending': date_filter(Order.query.filter_by(pay_status='pending'), Order.created_at).count(),
            'paid': date_filter(Order.query.filter_by(pay_status='paid'), Order.created_at).count(),
            'refunded': date_filter(Order.query.filter_by(pay_status='refunded'), Order.created_at).count(),
            'cancelled': date_filter(Order.query.filter_by(pay_status='cancelled'), Order.created_at).count(),
            'total_amount': float(
                date_filter(
                    db.session.query(func.sum(Order.total_amount)).filter(Order.pay_status == 'paid'),
                    Order.created_at,
                ).scalar() or 0
            ),
        },
        'adoptions': {
            'total': date_filter(AdoptionApplication.query, AdoptionApplication.submitted_at).count(),
            'pending': date_filter(AdoptionApplication.query.filter_by(review_status='pending'), AdoptionApplication.submitted_at).count(),
            'approved': date_filter(AdoptionApplication.query.filter_by(review_status='approved'), AdoptionApplication.submitted_at).count(),
            'rejected': date_filter(AdoptionApplication.query.filter_by(review_status='rejected'), AdoptionApplication.submitted_at).count(),
        },
        'bookings': {
            'total': date_filter(Booking.query, Booking.created_at).count(),
            'pending': date_filter(Booking.query.filter_by(booking_status='pending'), Booking.created_at).count(),
            'confirmed': date_filter(Booking.query.filter_by(booking_status='confirmed'), Booking.created_at).count(),
            'finished': date_filter(Booking.query.filter_by(booking_status='finished'), Booking.created_at).count(),
            'cancelled': date_filter(Booking.query.filter_by(booking_status='cancelled'), Booking.created_at).count(),
        },
    }

    trend_days = 30
    if start_dt and end_dt:
        trend_days = min((end_dt - start_dt).days + 1, 90)

    daily_orders = db.session.query(
        cast(Order.created_at, SADate).label('day'),
        func.count(Order.order_id).label('cnt'),
    ).filter(
        Order.created_at >= db.session.query(func.date_sub(func.now(), text(f'interval {trend_days} day'))).scalar_subquery()
        if not start_dt else Order.created_at >= start_dt
    )
    if end_dt:
        daily_orders = daily_orders.filter(Order.created_at <= end_dt)
    daily_orders = daily_orders.group_by('day').order_by('day').all()

    daily_adoptions = db.session.query(
        cast(AdoptionApplication.submitted_at, SADate).label('day'),
        func.count(AdoptionApplication.application_id).label('cnt'),
    ).filter(
        AdoptionApplication.submitted_at >= db.session.query(
            func.date_sub(func.now(), text(f'interval {trend_days} day'))
        ).scalar_subquery()
        if not start_dt else AdoptionApplication.submitted_at >= start_dt
    )
    if end_dt:
        daily_adoptions = daily_adoptions.filter(AdoptionApplication.submitted_at <= end_dt)
    daily_adoptions = daily_adoptions.group_by('day').order_by('day').all()

    stats['trend'] = {
        'orders': [{'date': str(row.day), 'count': row.cnt} for row in daily_orders],
        'adoptions': [{'date': str(row.day), 'count': row.cnt} for row in daily_adoptions],
    }

    return jsonify(stats), 200


@admin_bp.route('/logs', methods=['GET'])
@role_required('admin')
def list_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 30, type=int)

    query = OperationLog.query.order_by(OperationLog.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [{
        'log_id': log.log_id,
        'operator': log.operator.to_public_dict() if log.operator else None,
        'action': log.action,
        'target_type': log.target_type,
        'target_id': log.target_id,
        'detail': log.detail,
        'ip_address': log.ip_address,
        'created_at': log.created_at.isoformat() if log.created_at else None,
    } for log in result['items']]
    return jsonify(result), 200
