from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import Product, ProductImage, User
from app.utils import role_required, paginate_query

products_bp = Blueprint('products', __name__, url_prefix='/api/products')


@products_bp.route('', methods=['GET'])
def list_products():
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    category = request.args.get('category', '')
    keyword  = request.args.get('keyword', '')

    query = Product.query.filter_by(status='online')
    if category:
        query = query.filter(Product.category == category)
    if keyword:
        query = query.filter(Product.product_name.ilike(f'%{keyword}%'))
    query = query.order_by(Product.sales_count.desc(), Product.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [p.to_dict() for p in result['items']]
    return jsonify(result), 200


@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict()), 200


@products_bp.route('/my', methods=['GET'])
@role_required('publisher')
def my_products():
    user_id  = get_jwt_identity()
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    status   = request.args.get('status', '')

    query = Product.query.filter_by(publisher_id=user_id)
    if status:
        query = query.filter(Product.status == status)
    query = query.order_by(Product.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [p.to_dict() for p in result['items']]
    return jsonify(result), 200


@products_bp.route('', methods=['POST'])
@role_required('publisher')
def create_product():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400

    required = ['product_name', 'price', 'stock']
    for f in required:
        if data.get(f) is None:
            return jsonify({'error': f'{f} 不能为空'}), 400
    if float(data['price']) <= 0:
        return jsonify({'error': '价格必须大于0'}), 400
    if int(data['stock']) < 0:
        return jsonify({'error': '库存不能为负数'}), 400

    product = Product(
        publisher_id=user_id,
        product_name=data['product_name'],
        category=data.get('category'),
        description=data.get('description'),
        cover_image=data.get('cover_image'),
        price=data['price'],
        stock=data['stock'],
        status='online',
    )
    db.session.add(product)
    db.session.flush()

    for img_url in data.get('images', []):
        db.session.add(ProductImage(product_id=product.product_id, image_url=img_url))

    db.session.commit()
    return jsonify({'message': '商品创建成功', 'product': product.to_dict()}), 201


@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    user_id = get_jwt_identity()
    user    = User.query.get(user_id)
    product = Product.query.get_or_404(product_id)

    if product.publisher_id != user_id and user.role_type != 'admin':
        return jsonify({'error': '无权操作'}), 403

    data = request.get_json() or {}
    updatable = ['product_name', 'category', 'description', 'cover_image',
                 'price', 'stock', 'status']
    for field in updatable:
        if field in data:
            setattr(product, field, data[field])

    if 'images' in data:
        ProductImage.query.filter_by(product_id=product_id).delete()
        for img_url in data['images']:
            db.session.add(ProductImage(product_id=product_id, image_url=img_url))

    db.session.commit()
    return jsonify({'message': '更新成功', 'product': product.to_dict()}), 200


@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    user_id = get_jwt_identity()
    user    = User.query.get(user_id)
    product = Product.query.get_or_404(product_id)

    if product.publisher_id != user_id and user.role_type != 'admin':
        return jsonify({'error': '无权操作'}), 403

    product.status = 'offline'
    db.session.commit()
    return jsonify({'message': '商品已下架'}), 200
