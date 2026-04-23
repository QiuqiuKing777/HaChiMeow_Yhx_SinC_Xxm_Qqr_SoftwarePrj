from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import User, UserAddress, Favorite, Notification, Message
from app.utils import role_required

user_bp = Blueprint('user', __name__, url_prefix='/api/user')


# ---- 个人信息 ----

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user    = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user    = User.query.get_or_404(user_id)
    data    = request.get_json() or {}

    for field in ['nickname', 'phone', 'email', 'avatar']:
        if field in data:
            setattr(user, field, data[field])

    if 'new_password' in data and data['new_password']:
        if len(data['new_password']) < 6:
            return jsonify({'error': '新密码长度不能少于6位'}), 400
        user.password_hash = generate_password_hash(data['new_password'])

    db.session.commit()
    return jsonify({'message': '更新成功', 'user': user.to_dict()}), 200


# ---- 收货地址 ----

@user_bp.route('/addresses', methods=['GET'])
@jwt_required()
def list_addresses():
    user_id   = get_jwt_identity()
    addresses = UserAddress.query.filter_by(user_id=user_id).all()
    return jsonify([a.to_dict() for a in addresses]), 200


@user_bp.route('/addresses', methods=['POST'])
@jwt_required()
def create_address():
    user_id = get_jwt_identity()
    data    = request.get_json() or {}

    phone = data.get('phone') or data.get('receiver_phone')

    if not data.get('receiver_name'):
        return jsonify({'error': 'receiver_name 不能为空'}), 400
    if not phone:
        return jsonify({'error': 'phone 不能为空'}), 400
    if not data.get('detail'):
        return jsonify({'error': 'detail 不能为空'}), 400

    is_default = bool(data.get('is_default', False))
    if is_default:
        UserAddress.query.filter_by(user_id=user_id).update({'is_default': False})

    address = UserAddress(
        user_id=user_id,
        receiver_name=data['receiver_name'],
        phone=phone,
        province=data.get('province'),
        city=data.get('city'),
        district=data.get('district'),
        detail=data['detail'],
        is_default=is_default,
    )
    db.session.add(address)
    db.session.commit()
    return jsonify({'message': '地址已添加', 'address': address.to_dict()}), 201


@user_bp.route('/addresses/<int:address_id>', methods=['PUT'])
@jwt_required()
def update_address(address_id):
    user_id = get_jwt_identity()
    address = UserAddress.query.filter_by(address_id=address_id, user_id=user_id).first_or_404()
    data    = request.get_json() or {}

    if 'receiver_phone' in data and 'phone' not in data:
        data['phone'] = data.get('receiver_phone')

    is_default = data.get('is_default')
    if is_default:
        UserAddress.query.filter_by(user_id=user_id).update({'is_default': False})

    for field in ['receiver_name', 'phone', 'province', 'city', 'district', 'detail', 'is_default']:
        if field in data:
            setattr(address, field, data[field])
    db.session.commit()
    return jsonify({'message': '更新成功', 'address': address.to_dict()}), 200


@user_bp.route('/addresses/<int:address_id>', methods=['DELETE'])
@jwt_required()
def delete_address(address_id):
    user_id = get_jwt_identity()
    address = UserAddress.query.filter_by(address_id=address_id, user_id=user_id).first_or_404()
    db.session.delete(address)
    db.session.commit()
    return jsonify({'message': '地址已删除'}), 200


# ---- 收藏 ----

@user_bp.route('/favorites', methods=['GET'])
@jwt_required()
def list_favorites():
    user_id     = get_jwt_identity()
    target_type = request.args.get('target_type', '').strip() or request.args.get('type', '').strip()
    query       = Favorite.query.filter_by(user_id=user_id)
    if target_type:
        query = query.filter(Favorite.target_type == target_type)
    favorites = query.order_by(Favorite.created_at.desc()).all()
    return jsonify([f.to_dict() for f in favorites]), 200


@user_bp.route('/favorites', methods=['POST'])
@jwt_required()
def add_favorite():
    user_id = get_jwt_identity()
    data    = request.get_json() or {}
    target_type = data.get('target_type')
    target_id   = data.get('target_id')

    if not target_type or not target_id:
        return jsonify({'error': 'target_type 和 target_id 不能为空'}), 400

    existing = Favorite.query.filter_by(
        user_id=user_id, target_type=target_type, target_id=target_id
    ).first()
    if existing:
        return jsonify({'message': '已收藏'}), 200

    fav = Favorite(user_id=user_id, target_type=target_type, target_id=target_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({'message': '收藏成功', 'favorite': fav.to_dict()}), 201


@user_bp.route('/favorites/<string:target_type>/<int:target_id>', methods=['DELETE'])
@jwt_required()
def remove_favorite(target_type, target_id):
    user_id = get_jwt_identity()
    fav = Favorite.query.filter_by(
        user_id=user_id, target_type=target_type, target_id=target_id
    ).first()
    if not fav:
        return jsonify({'error': '收藏不存在'}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({'message': '已取消收藏'}), 200


@user_bp.route('/favorites/<int:favorite_id>', methods=['DELETE'])
@jwt_required()
def remove_favorite_by_id(favorite_id):
    user_id = get_jwt_identity()
    fav = Favorite.query.filter_by(favorite_id=favorite_id, user_id=user_id).first()
    if not fav:
        return jsonify({'error': '收藏不存在'}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({'message': '已取消收藏'}), 200


# ---- 通知 ----

@user_bp.route('/notifications', methods=['GET'])
@jwt_required()
def list_notifications():
    user_id   = get_jwt_identity()
    page      = request.args.get('page', 1, type=int)
    per_page  = request.args.get('per_page', 20, type=int)
    is_read   = request.args.get('is_read', None)

    query = Notification.query.filter_by(user_id=user_id)
    if is_read is not None:
        query = query.filter(Notification.is_read == (is_read == '1'))
    query = query.order_by(Notification.created_at.desc())
    from app.utils import paginate_query
    result = paginate_query(query, page, per_page)
    result['items'] = [n.to_dict() for n in result['items']]
    unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
    result['unread_count'] = unread_count
    return jsonify(result), 200


@user_bp.route('/notifications/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_read(notification_id):
    user_id = get_jwt_identity()
    note = Notification.query.filter_by(notification_id=notification_id, user_id=user_id).first_or_404()
    note.is_read = True
    db.session.commit()
    return jsonify({'message': '已标记为已读'}), 200


@user_bp.route('/notifications/read-all', methods=['PUT'])
@jwt_required()
def read_all():
    user_id = get_jwt_identity()
    Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'message': '全部已读'}), 200


# ---- 站内消息 ----

@user_bp.route('/messages', methods=['GET'])
@jwt_required()
def list_messages():
    user_id = get_jwt_identity()
    messages = Message.query.filter(
        (Message.receiver_id == user_id) | (Message.sender_id == user_id)
    ).order_by(Message.created_at.desc()).limit(100).all()
    return jsonify([m.to_dict() for m in messages]), 200


@user_bp.route('/messages', methods=['POST'])
@jwt_required()
def send_message():
    user_id = get_jwt_identity()
    data    = request.get_json() or {}

    receiver_id = data.get('receiver_id')
    content     = data.get('content', '').strip()
    pet_id      = data.get('pet_id')

    if not receiver_id or not content:
        return jsonify({'error': 'receiver_id 和 content 不能为空'}), 400

    msg = Message(sender_id=user_id, receiver_id=receiver_id, pet_id=pet_id, content=content)
    db.session.add(msg)
    db.session.commit()
    return jsonify({'message': '发送成功', 'data': msg.to_dict()}), 201
