from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import CartItem, Product
from app.utils import role_required

cart_bp = Blueprint('cart', __name__, url_prefix='/api/cart')


@cart_bp.route('', methods=['GET'])
@role_required('user', 'publisher')
def get_cart():
    user_id = get_jwt_identity()
    items   = CartItem.query.filter_by(user_id=user_id).all()
    return jsonify([item.to_dict() for item in items]), 200


@cart_bp.route('', methods=['POST'])
@role_required('user', 'publisher')
def add_to_cart():
    user_id    = get_jwt_identity()
    data       = request.get_json() or {}
    product_id = data.get('product_id')
    quantity   = data.get('quantity', 1)

    if not product_id:
        return jsonify({'error': '请选择商品'}), 400

    product = Product.query.get_or_404(product_id)
    if product.status != 'online':
        return jsonify({'error': '商品已下架'}), 400
    if quantity < 1:
        return jsonify({'error': '数量不能小于1'}), 400
    if product.stock < quantity:
        return jsonify({'error': '库存不足'}), 400

    existing = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing:
        new_qty = existing.quantity + quantity
        if product.stock < new_qty:
            return jsonify({'error': '超出库存上限'}), 400
        existing.quantity = new_qty
        db.session.commit()
        return jsonify({'message': '数量已更新', 'cart_item': existing.to_dict()}), 200

    item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
    db.session.add(item)
    db.session.commit()
    return jsonify({'message': '已加入购物车', 'cart_item': item.to_dict()}), 201


@cart_bp.route('/<int:cart_id>', methods=['PUT'])
@role_required('user', 'publisher')
def update_cart(cart_id):
    user_id  = get_jwt_identity()
    cart_item = CartItem.query.filter_by(cart_id=cart_id, user_id=user_id).first()
    if not cart_item:
        return jsonify({'error': '购物车项不存在'}), 404

    data     = request.get_json() or {}
    quantity = data.get('quantity')
    if quantity is None or quantity < 1:
        return jsonify({'error': '数量不合法'}), 400
    if cart_item.product.stock < quantity:
        return jsonify({'error': '超出库存上限'}), 400

    cart_item.quantity = quantity
    db.session.commit()
    return jsonify({'message': '已更新', 'cart_item': cart_item.to_dict()}), 200


@cart_bp.route('/<int:cart_id>', methods=['DELETE'])
@role_required('user', 'publisher')
def remove_cart(cart_id):
    user_id   = get_jwt_identity()
    cart_item = CartItem.query.filter_by(cart_id=cart_id, user_id=user_id).first()
    if not cart_item:
        return jsonify({'error': '购物车项不存在'}), 404

    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': '已移除'}), 200


@cart_bp.route('/clear', methods=['DELETE'])
@role_required('user', 'publisher')
def clear_cart():
    user_id = get_jwt_identity()
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return jsonify({'message': '购物车已清空'}), 200
