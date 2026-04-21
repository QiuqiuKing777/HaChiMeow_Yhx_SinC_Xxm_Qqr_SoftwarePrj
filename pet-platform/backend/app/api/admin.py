from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models import User, Pet, Product, Service, Order, Booking, AdoptionApplication, OperationLog, Review
from app.utils import role_required, paginate_query

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# ---- 用户管理 ----

@admin_bp.route('/users', methods=['GET'])
@role_required('admin')
def list_users():
    page      = request.args.get('page', 1, type=int)
    per_page  = request.args.get('per_page', 20, type=int)
    role_type = request.args.get('role_type', '')
    keyword   = request.args.get('keyword', '')
    status    = request.args.get('status', '')

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
    result['items'] = [u.to_dict() for u in result['items']]
    return jsonify(result), 200


@admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@role_required('admin')
def set_user_status(user_id):
    operator_id = get_jwt_identity()
    data    = request.get_json() or {}
    status  = data.get('status')
    if status not in ('active', 'disabled'):
        return jsonify({'error': 'status 必须为 active 或 disabled'}), 400

    user = User.query.get_or_404(user_id)
    if user.role_type == 'admin':
        return jsonify({'error': '不能修改管理员账号状态'}), 403

    user.status = status
    db.session.add(OperationLog(
        operator_id=operator_id,
        action='set_user_status',
        target_type='user',
        target_id=user_id,
        detail=f'status={status}',
    ))
    db.session.commit()
    return jsonify({'message': f'用户状态已设置为 {status}', 'user': user.to_dict()}), 200


# ---- 宠物审核 ----

@admin_bp.route('/pets', methods=['GET'])
@role_required('admin')
def admin_list_pets():
    page   = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')

    query = Pet.query
    if status:
        query = query.filter(Pet.status == status)
    query = query.order_by(Pet.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [p.to_dict() for p in result['items']]
    return jsonify(result), 200


@admin_bp.route('/pets/<int:pet_id>/status', methods=['PUT'])
@role_required('admin')
def set_pet_status(pet_id):
    operator_id = get_jwt_identity()
    data   = request.get_json() or {}
    status = data.get('status')
    if status not in ('online', 'offline', 'pending'):
        return jsonify({'error': '无效 status'}), 400

    pet = Pet.query.get_or_404(pet_id)
    pet.status = status
    db.session.add(OperationLog(
        operator_id=operator_id, action='set_pet_status',
        target_type='pet', target_id=pet_id, detail=f'status={status}'
    ))
    db.session.commit()
    return jsonify({'message': '宠物状态已更新', 'pet': pet.to_dict()}), 200


# ---- 商品审核 ----

@admin_bp.route('/products', methods=['GET'])
@role_required('admin')
def admin_list_products():
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status   = request.args.get('status', '')

    query = Product.query
    if status:
        query = query.filter(Product.status == status)
    query = query.order_by(Product.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [p.to_dict() for p in result['items']]
    return jsonify(result), 200


@admin_bp.route('/products/<int:product_id>/status', methods=['PUT'])
@role_required('admin')
def set_product_status(product_id):
    operator_id = get_jwt_identity()
    data   = request.get_json() or {}
    status = data.get('status')
    if status not in ('online', 'offline', 'pending'):
        return jsonify({'error': '无效 status'}), 400

    product = Product.query.get_or_404(product_id)
    product.status = status
    db.session.add(OperationLog(
        operator_id=operator_id, action='set_product_status',
        target_type='product', target_id=product_id, detail=f'status={status}'
    ))
    db.session.commit()
    return jsonify({'message': '商品状态已更新'}), 200


# ---- 服务审核 ----

@admin_bp.route('/services', methods=['GET'])
@role_required('admin')
def admin_list_services():
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status   = request.args.get('status', '')

    query = Service.query
    if status:
        query = query.filter(Service.status == status)
    query = query.order_by(Service.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [s.to_dict() for s in result['items']]
    return jsonify(result), 200


@admin_bp.route('/services/<int:service_id>/status', methods=['PUT'])
@role_required('admin')
def set_service_status(service_id):
    operator_id = get_jwt_identity()
    data   = request.get_json() or {}
    status = data.get('status')
    if status not in ('online', 'offline', 'pending'):
        return jsonify({'error': '无效 status'}), 400

    service = Service.query.get_or_404(service_id)
    service.status = status
    db.session.add(OperationLog(
        operator_id=operator_id, action='set_service_status',
        target_type='service', target_id=service_id, detail=f'status={status}'
    ))
    db.session.commit()
    return jsonify({'message': '服务状态已更新'}), 200


# ---- 统计数据 ----

@admin_bp.route('/stats', methods=['GET'])
@role_required('admin')
def get_stats():
    from sqlalchemy import func
    stats = {
        'users': {
            'total':     User.query.count(),
            'user':      User.query.filter_by(role_type='user').count(),
            'publisher': User.query.filter_by(role_type='publisher').count(),
            'disabled':  User.query.filter_by(status='disabled').count(),
        },
        'pets': {
            'total':   Pet.query.count(),
            'online':  Pet.query.filter_by(status='online').count(),
            'adopted': Pet.query.filter_by(status='adopted').count(),
            'pending': Pet.query.filter_by(status='pending').count(),
        },
        'products': {
            'total':  Product.query.count(),
            'online': Product.query.filter_by(status='online').count(),
        },
        'orders': {
            'total':   Order.query.count(),
            'pending': Order.query.filter_by(pay_status='pending').count(),
            'paid':    Order.query.filter_by(pay_status='paid').count(),
            'total_amount': float(
                db.session.query(func.sum(Order.total_amount))
                .filter(Order.pay_status == 'paid')
                .scalar() or 0
            ),
        },
        'adoptions': {
            'total':    AdoptionApplication.query.count(),
            'pending':  AdoptionApplication.query.filter_by(review_status='pending').count(),
            'approved': AdoptionApplication.query.filter_by(review_status='approved').count(),
        },
        'bookings': {
            'total':    Booking.query.count(),
            'pending':  Booking.query.filter_by(booking_status='pending').count(),
            'finished': Booking.query.filter_by(booking_status='finished').count(),
        },
    }
    return jsonify(stats), 200


# ---- 操作日志 ----

@admin_bp.route('/logs', methods=['GET'])
@role_required('admin')
def list_logs():
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 30, type=int)

    query  = OperationLog.query.order_by(OperationLog.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [{
        'log_id':      log.log_id,
        'operator':    log.operator.to_public_dict() if log.operator else None,
        'action':      log.action,
        'target_type': log.target_type,
        'target_id':   log.target_id,
        'detail':      log.detail,
        'created_at':  log.created_at.isoformat() if log.created_at else None,
    } for log in result['items']]
    return jsonify(result), 200
