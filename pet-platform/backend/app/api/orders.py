import json
from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import Order, OrderItem, CartItem, Product, UserAddress
from app.utils import role_required, paginate_query, send_notification
from app.api.products import build_full_image_url

orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')


def _generate_order_no():
    import time
    import random
    return f"PO{int(time.time())}{random.randint(1000, 9999)}"


def serialize_order_item(item):
    data = item.to_dict()
    data['image_url'] = build_full_image_url(data.get('image_url'))
    return data


def serialize_order(order):
    data = order.to_dict()
    data['items'] = [serialize_order_item(item) for item in order.items]
    return data


@orders_bp.route('', methods=['POST'])
@role_required('user', 'publisher')
def create_order():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    address_id = data.get('address_id')
    cart_ids = data.get('cart_ids', [])
    items_raw = data.get('items', [])
    remark = data.get('remark', '')

    if not address_id:
        return jsonify({'error': '请选择收货地址'}), 400

    address = UserAddress.query.filter_by(address_id=address_id, user_id=user_id).first()
    if not address:
        return jsonify({'error': '收货地址不存在'}), 404

    order_items_data = []
    if cart_ids:
        carts = CartItem.query.filter(CartItem.cart_id.in_(cart_ids), CartItem.user_id == user_id).all()
        for cart in carts:
            order_items_data.append({'product': cart.product, 'quantity': cart.quantity})
    elif items_raw:
        for item in items_raw:
            product = Product.query.get(item.get('product_id'))
            if product and product.status == 'online':
                order_items_data.append({'product': product, 'quantity': item.get('quantity', 1)})

    if not order_items_data:
        return jsonify({'error': '下单商品不能为空'}), 400

    for item in order_items_data:
        product, qty = item['product'], item['quantity']
        if product.stock < qty:
            return jsonify({'error': f'商品「{product.product_name}」库存不足'}), 400

    total = sum(float(item['product'].price) * item['quantity'] for item in order_items_data)

    order = Order(
        order_no=_generate_order_no(),
        buyer_id=user_id,
        total_amount=total,
        address_snapshot=json.dumps(address.to_dict(), ensure_ascii=False),
        remark=remark,
    )
    db.session.add(order)
    db.session.flush()

    for item in order_items_data:
        product, qty = item['product'], item['quantity']
        db.session.add(OrderItem(
            order_id=order.order_id,
            product_id=product.product_id,
            product_name=product.product_name,
            price=product.price,
            quantity=qty,
            image_url=product.cover_image,
        ))
        product.stock -= qty

    if cart_ids:
        CartItem.query.filter(CartItem.cart_id.in_(cart_ids), CartItem.user_id == user_id).delete()

    db.session.commit()
    return jsonify({'message': '订单创建成功', 'order': serialize_order(order)}), 201


@orders_bp.route('', methods=['GET'])
@role_required('user', 'publisher')
def my_orders():
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pay_status = request.args.get('pay_status', '')

    query = Order.query.filter_by(buyer_id=user_id)
    if pay_status:
        query = query.filter(Order.pay_status == pay_status)
    query = query.order_by(Order.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [serialize_order(order) for order in result['items']]
    return jsonify(result), 200


@orders_bp.route('/publisher', methods=['GET'])
@role_required('publisher')
def publisher_orders():
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    delivery_status = request.args.get('delivery_status', '')

    product_ids = [product.product_id for product in Product.query.filter_by(publisher_id=user_id).all()]
    if not product_ids:
        return jsonify({'items': [], 'total': 0, 'page': 1, 'pages': 0, 'per_page': per_page}), 200

    from sqlalchemy import exists
    query = Order.query.filter(
        exists().where(
            (OrderItem.order_id == Order.order_id) &
            (OrderItem.product_id.in_(product_ids))
        )
    ).filter(Order.pay_status != 'cancelled').order_by(Order.created_at.desc())
    if delivery_status:
        query = query.filter(Order.delivery_status == delivery_status)
    result = paginate_query(query, page, per_page)
    result['items'] = [serialize_order(order) for order in result['items']]
    return jsonify(result), 200


@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    user_id = int(get_jwt_identity())
    from app.models import User
    user = User.query.get(user_id)
    order = Order.query.get_or_404(order_id)

    if order.buyer_id != user_id and user.role_type not in ('publisher', 'admin'):
        return jsonify({'error': '无权查看'}), 403

    return jsonify(serialize_order(order)), 200


@orders_bp.route('/<int:order_id>/pay', methods=['PUT'])
@role_required('user', 'publisher')
def pay_order(order_id):
    user_id = int(get_jwt_identity())
    order = Order.query.get_or_404(order_id)

    if order.buyer_id != user_id:
        return jsonify({'error': '无权操作'}), 403
    if order.pay_status != 'pending':
        return jsonify({'error': '订单状态不允许付款'}), 400

    order.pay_status = 'paid'
    order.paid_at = datetime.utcnow()
    db.session.commit()

    send_notification(user_id, 'order', f'订单 {order.order_no} 支付成功', '感谢您的购买，等待商家发货。')
    return jsonify({'message': '支付成功', 'order': serialize_order(order)}), 200


@orders_bp.route('/<int:order_id>/ship', methods=['PUT'])
@role_required('publisher')
def ship_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.pay_status != 'paid':
        return jsonify({'error': '订单未付款，无法发货'}), 400
    if order.delivery_status != 'pending':
        return jsonify({'error': '订单已发货'}), 400

    order.delivery_status = 'shipped'
    db.session.commit()

    send_notification(order.buyer_id, 'order', f'订单 {order.order_no} 已发货', '请注意查收，收到货后请确认收货。')
    return jsonify({'message': '发货成功', 'order': serialize_order(order)}), 200


@orders_bp.route('/<int:order_id>/receive', methods=['PUT'])
@role_required('user', 'publisher')
def receive_order(order_id):
    user_id = int(get_jwt_identity())
    order = Order.query.get_or_404(order_id)

    if order.buyer_id != user_id:
        return jsonify({'error': '无权操作'}), 403
    if order.delivery_status != 'shipped':
        return jsonify({'error': '商品尚未发货'}), 400

    order.delivery_status = 'delivered'
    order.receive_status = 'received'
    for item in order.items:
        product = Product.query.get(item.product_id)
        if product:
            product.sales_count += item.quantity
    db.session.commit()
    return jsonify({'message': '确认收货成功', 'order': serialize_order(order)}), 200


@orders_bp.route('/<int:order_id>/cancel', methods=['PUT'])
@role_required('user', 'publisher')
def cancel_order(order_id):
    user_id = int(get_jwt_identity())
    order = Order.query.get_or_404(order_id)

    if order.buyer_id != user_id:
        return jsonify({'error': '无权操作'}), 403
    if order.pay_status not in ('pending',):
        return jsonify({'error': '已付款订单无法直接取消，请申请退款'}), 400

    for item in order.items:
        product = Product.query.get(item.product_id)
        if product:
            product.stock += item.quantity
    order.pay_status = 'cancelled'
    db.session.commit()
    return jsonify({'message': '订单已取消', 'order': serialize_order(order)}), 200
