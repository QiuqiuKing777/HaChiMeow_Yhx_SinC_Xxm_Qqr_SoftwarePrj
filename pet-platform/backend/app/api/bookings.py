from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import Booking, Service, ServiceSlot, User
from app.utils import role_required, paginate_query, send_notification

bookings_bp = Blueprint('bookings', __name__, url_prefix='/api/bookings')


@bookings_bp.route('', methods=['POST'])
@role_required('user')
def create_booking():
    user_id = get_jwt_identity()
    data    = request.get_json() or {}

    slot_id = data.get('slot_id')
    if not slot_id:
        return jsonify({'error': '请选择预约时段'}), 400

    slot = ServiceSlot.query.get_or_404(slot_id)
    if slot.booked_count >= slot.capacity:
        return jsonify({'error': '该时段已约满，请选择其他时段'}), 400

    service = Service.query.get(slot.service_id)
    if not service or service.status != 'online':
        return jsonify({'error': '服务不可用'}), 400

    booking = Booking(
        service_id=slot.service_id,
        user_id=user_id,
        slot_id=slot_id,
        pet_name=data.get('pet_name'),
        pet_breed=data.get('pet_breed'),
        remark=data.get('remark'),
    )
    slot.booked_count += 1
    db.session.add(booking)
    db.session.commit()

    send_notification(
        service.publisher_id, 'booking',
        f'服务「{service.service_name}」收到新预约',
        f'预约日期：{slot.slot_date} {slot.slot_time}'
    )
    return jsonify({'message': '预约成功，等待商家确认', 'booking': booking.to_dict()}), 201


@bookings_bp.route('/my', methods=['GET'])
@role_required('user')
def my_bookings():
    user_id  = get_jwt_identity()
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status   = request.args.get('status', '')

    query = Booking.query.filter_by(user_id=user_id)
    if status:
        query = query.filter(Booking.booking_status == status)
    query = query.order_by(Booking.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [b.to_dict() for b in result['items']]
    return jsonify(result), 200


@bookings_bp.route('/publisher', methods=['GET'])
@role_required('publisher')
def publisher_bookings():
    user_id  = get_jwt_identity()
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status   = request.args.get('status', '')

    service_ids = [s.service_id for s in Service.query.filter_by(publisher_id=user_id).all()]
    if not service_ids:
        return jsonify({'items': [], 'total': 0, 'page': 1, 'pages': 0, 'per_page': per_page}), 200

    query = Booking.query.filter(Booking.service_id.in_(service_ids))
    if status:
        query = query.filter(Booking.booking_status == status)
    query = query.order_by(Booking.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [b.to_dict() for b in result['items']]
    return jsonify(result), 200


@bookings_bp.route('/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    user_id = get_jwt_identity()
    user    = User.query.get(user_id)
    booking = Booking.query.get_or_404(booking_id)

    is_owner     = (booking.user_id == user_id)
    is_publisher = (booking.service.publisher_id == user_id)
    is_admin     = (user.role_type == 'admin')
    if not (is_owner or is_publisher or is_admin):
        return jsonify({'error': '无权查看'}), 403

    return jsonify(booking.to_dict()), 200


@bookings_bp.route('/<int:booking_id>/confirm', methods=['PUT'])
@role_required('publisher')
def confirm_booking(booking_id):
    user_id = get_jwt_identity()
    booking = Booking.query.get_or_404(booking_id)

    if booking.service.publisher_id != user_id:
        return jsonify({'error': '无权操作'}), 403
    if booking.booking_status != 'pending':
        return jsonify({'error': '该预约不处于待确认状态'}), 400

    booking.booking_status = 'confirmed'
    db.session.commit()

    send_notification(booking.user_id, 'booking', f'预约已确认',
                      f'您在{booking.slot.slot_date}的{booking.service.service_name}预约已确认，请准时到店。')
    return jsonify({'message': '预约已确认', 'booking': booking.to_dict()}), 200


@bookings_bp.route('/<int:booking_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_booking(booking_id):
    user_id = get_jwt_identity()
    user    = User.query.get(user_id)
    booking = Booking.query.get_or_404(booking_id)

    is_owner     = (booking.user_id == user_id)
    is_publisher = (booking.service.publisher_id == user_id)
    if not (is_owner or is_publisher or user.role_type == 'admin'):
        return jsonify({'error': '无权操作'}), 403
    if booking.booking_status in ('cancelled', 'finished'):
        return jsonify({'error': '该预约已结束，无法取消'}), 400

    booking.booking_status = 'cancelled'
    # 恢复时段余量
    slot = booking.slot
    if slot and slot.booked_count > 0:
        slot.booked_count -= 1
    db.session.commit()
    return jsonify({'message': '预约已取消', 'booking': booking.to_dict()}), 200


@bookings_bp.route('/<int:booking_id>/finish', methods=['PUT'])
@role_required('publisher')
def finish_booking(booking_id):
    user_id = get_jwt_identity()
    booking = Booking.query.get_or_404(booking_id)

    if booking.service.publisher_id != user_id:
        return jsonify({'error': '无权操作'}), 403
    if booking.booking_status != 'confirmed':
        return jsonify({'error': '预约尚未确认'}), 400

    booking.booking_status = 'finished'
    db.session.commit()

    send_notification(booking.user_id, 'booking', f'服务已完成',
                      f'您的{booking.service.service_name}服务已完成，欢迎评价。')
    return jsonify({'message': '服务已完成', 'booking': booking.to_dict()}), 200
