from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models import User, Pet, Product, Service, Order, Booking, AdoptionApplication, OperationLog, Review, Complaint
from app.utils import role_required, paginate_query

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def build_full_image_url(path):
    if not path:
        return None

    base = request.host_url.rstrip('/')

    if path.startswith('http://') or path.startswith('https://'):
        return path

    if path.startswith('/static/'):
        return f'{base}{path}'
    else:
        return f'{path}'

def serialize_admin_pet(pet):
    data = pet.to_dict()

    data['cover_image'] = build_full_image_url(data.get('cover_image'))

    images = data.get('images') or []
    for img in images:
        img['image_url'] = build_full_image_url(img.get('image_url'))

    return data

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
        ip_address=request.remote_addr,
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
    else:
        query = query.filter(Pet.status != 'offline')
    query = query.order_by(Pet.created_at.desc())
    result = paginate_query(query, page, per_page)
    # result['items'] = [p.to_dict() for p in result['items']]
    result['items'] = [serialize_admin_pet(p) for p in result['items']]
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
        target_type='pet', target_id=pet_id, detail=f'status={status}',
        ip_address=request.remote_addr,
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
    else:
        query = query.filter(Product.status != 'offline')
    query = query.order_by(Product.created_at.desc())
    result = paginate_query(query, page, per_page)
    items = []
    for p in result['items']:
        d = p.to_dict()
        d['publisher'] = p.publisher.to_public_dict() if p.publisher else None
        items.append(d)
    result['items'] = items
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
        target_type='product', target_id=product_id, detail=f'status={status}',
        ip_address=request.remote_addr,
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
    else:
        query = query.filter(Service.status != 'offline')
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
        target_type='service', target_id=service_id, detail=f'status={status}',
        ip_address=request.remote_addr,
    ))
    db.session.commit()
    return jsonify({'message': '服务状态已更新'}), 200


# ---- 订单监管 ----

@admin_bp.route('/orders', methods=['GET'])
@role_required('admin')
def admin_list_orders():
    page       = request.args.get('page', 1, type=int)
    per_page   = request.args.get('per_page', 20, type=int)
    pay_status = request.args.get('pay_status', '')
    keyword    = request.args.get('keyword', '')

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
    for o in result['items']:
        d = o.to_dict()
        d['buyer'] = o.buyer.to_public_dict() if o.buyer else None
        items.append(d)
    result['items'] = items
    return jsonify(result), 200


# ---- 预约监管 ----

@admin_bp.route('/bookings', methods=['GET'])
@role_required('admin')
def admin_list_bookings():
    page   = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')

    query = Booking.query
    if status:
        query = query.filter(Booking.booking_status == status)
    query = query.order_by(Booking.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [b.to_dict() for b in result['items']]
    return jsonify(result), 200


# ---- 领养申请监管 ----

@admin_bp.route('/adoptions', methods=['GET'])
@role_required('admin')
def admin_list_adoptions():
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status   = request.args.get('status', '')

    query = AdoptionApplication.query
    if status:
        query = query.filter(AdoptionApplication.review_status == status)
    query = query.order_by(AdoptionApplication.submitted_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [a.to_dict() for a in result['items']]
    return jsonify(result), 200


# ---- 投诉管理 ----

@admin_bp.route('/complaints', methods=['GET'])
@role_required('admin')
def admin_list_complaints():
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status   = request.args.get('status', '')

    query = Complaint.query
    if status:
        query = query.filter(Complaint.status == status)
    query = query.order_by(Complaint.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [c.to_dict() for c in result['items']]
    return jsonify(result), 200


@admin_bp.route('/complaints/<int:complaint_id>/handle', methods=['PUT'])
@role_required('admin')
def handle_complaint(complaint_id):
    operator_id = get_jwt_identity()
    data        = request.get_json() or {}
    status      = data.get('status')
    admin_reply = data.get('admin_reply', '')

    if status not in ('handling', 'resolved', 'closed'):
        return jsonify({'error': 'status 可选值: handling/resolved/closed'}), 400

    complaint = Complaint.query.get_or_404(complaint_id)
    complaint.status       = status
    complaint.admin_reply  = admin_reply
    complaint.handled_by   = operator_id
    complaint.handled_at   = datetime.utcnow()
    db.session.add(OperationLog(
        operator_id=operator_id, action='handle_complaint',
        target_type='complaint', target_id=complaint_id,
        detail=f'status={status}',
        ip_address=request.remote_addr,
    ))
    db.session.commit()
    return jsonify({'message': '投诉已处理', 'complaint': complaint.to_dict()}), 200


# ---- 统计数据 ----

@admin_bp.route('/stats', methods=['GET'])
@role_required('admin')
def get_stats():
    from sqlalchemy import func
    from datetime import date as date_type

    start_date_str = request.args.get('start_date', '')
    end_date_str   = request.args.get('end_date', '')

    # 解析日期范围
    start_dt = None
    end_dt   = None
    try:
        if start_date_str:
            start_dt = datetime.strptime(start_date_str, '%Y-%m-%d')
        if end_date_str:
            # end_date 取当天结束（次日零点前）
            end_dt = datetime.strptime(end_date_str, '%Y-%m-%d').replace(
                hour=23, minute=59, second=59
            )
    except ValueError:
        return jsonify({'error': '日期格式错误，请使用 YYYY-MM-DD'}), 400

    def date_filter(q, col):
        if start_dt:
            q = q.filter(col >= start_dt)
        if end_dt:
            q = q.filter(col <= end_dt)
        return q

    # 基础统计（不受日期过滤影响，始终反映全量数据）
    stats = {
        'date_range': {
            'start_date': start_date_str or None,
            'end_date':   end_date_str or None,
        },
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
            'offline': Pet.query.filter_by(status='offline').count(),
        },
        'products': {
            'total':   Product.query.count(),
            'online':  Product.query.filter_by(status='online').count(),
            'offline': Product.query.filter_by(status='offline').count(),
            'pending': Product.query.filter_by(status='pending').count(),
        },
        'services': {
            'total':   Service.query.count(),
            'online':  Service.query.filter_by(status='online').count(),
            'offline': Service.query.filter_by(status='offline').count(),
            'pending': Service.query.filter_by(status='pending').count(),
        },
        'orders': {
            'total':     date_filter(Order.query, Order.created_at).count(),
            'pending':   date_filter(Order.query.filter_by(pay_status='pending'), Order.created_at).count(),
            'paid':      date_filter(Order.query.filter_by(pay_status='paid'), Order.created_at).count(),
            'refunded':  date_filter(Order.query.filter_by(pay_status='refunded'), Order.created_at).count(),
            'cancelled': date_filter(Order.query.filter_by(pay_status='cancelled'), Order.created_at).count(),
            'total_amount': float(
                date_filter(
                    db.session.query(func.sum(Order.total_amount)).filter(Order.pay_status == 'paid'),
                    Order.created_at
                ).scalar() or 0
            ),
        },
        'adoptions': {
            'total':    date_filter(AdoptionApplication.query, AdoptionApplication.submitted_at).count(),
            'pending':  date_filter(AdoptionApplication.query.filter_by(review_status='pending'), AdoptionApplication.submitted_at).count(),
            'approved': date_filter(AdoptionApplication.query.filter_by(review_status='approved'), AdoptionApplication.submitted_at).count(),
            'rejected': date_filter(AdoptionApplication.query.filter_by(review_status='rejected'), AdoptionApplication.submitted_at).count(),
        },
        'bookings': {
            'total':     date_filter(Booking.query, Booking.created_at).count(),
            'pending':   date_filter(Booking.query.filter_by(booking_status='pending'), Booking.created_at).count(),
            'confirmed': date_filter(Booking.query.filter_by(booking_status='confirmed'), Booking.created_at).count(),
            'finished':  date_filter(Booking.query.filter_by(booking_status='finished'), Booking.created_at).count(),
            'cancelled': date_filter(Booking.query.filter_by(booking_status='cancelled'), Booking.created_at).count(),
        },
    }

    # 近 30 天每日新增趋势（订单量 + 领养申请量），用于前端折线图
    from sqlalchemy import cast, Date as SADate, text
    import calendar

    trend_days = 30
    if start_dt and end_dt:
        delta = (end_dt - start_dt).days + 1
        trend_days = min(delta, 90)

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
        'orders':    [{'date': str(r.day), 'count': r.cnt} for r in daily_orders],
        'adoptions': [{'date': str(r.day), 'count': r.cnt} for r in daily_adoptions],
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
        'ip_address':  log.ip_address,
        'created_at':  log.created_at.isoformat() if log.created_at else None,
    } for log in result['items']]
    return jsonify(result), 200
