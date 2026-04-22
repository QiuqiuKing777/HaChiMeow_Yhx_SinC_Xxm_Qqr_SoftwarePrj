import uuid
from pathlib import Path

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Product, ProductImage, User
from app.utils import role_required, paginate_query

products_bp = Blueprint('products', __name__, url_prefix='/api/products')

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


def serialize_product(product):
    data = product.to_dict()

    data['cover_image'] = build_full_image_url(data.get('cover_image'))

    images = data.get('images') or []
    for img in images:
        img['image_url'] = build_full_image_url(img.get('image_url'))

    return data


def save_uploaded_product_image(file_storage):
    if not file_storage or not file_storage.filename:
        return None

    filename = secure_filename(file_storage.filename)
    if not filename:
        return None

    if not allowed_image_file(filename):
        raise ValueError('仅支持 PNG、JPG、JPEG、SVG 格式图片')

    ext = filename.rsplit('.', 1)[1].lower()
    new_filename = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = Path(current_app.static_folder) / 'uploads' / 'products'
    upload_dir.mkdir(parents=True, exist_ok=True)

    save_path = upload_dir / new_filename
    file_storage.save(save_path)

    return f"/static/uploads/products/{new_filename}"


def get_request_data():
    if request.content_type and 'multipart/form-data' in request.content_type:
        return request.form.to_dict()
    return request.get_json(silent=True) or {}


@products_bp.route('', methods=['GET'])
def list_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    category = request.args.get('category', '')
    keyword = request.args.get('keyword', '')

    query = Product.query.filter_by(status='online')
    if category:
        query = query.filter(Product.category == category)
    if keyword:
        query = query.filter(Product.product_name.ilike(f'%{keyword}%'))

    query = query.order_by(Product.sales_count.desc(), Product.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [serialize_product(p) for p in result['items']]
    return jsonify(result), 200


@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(serialize_product(product)), 200


@products_bp.route('/my', methods=['GET'])
@role_required('publisher')
def my_products():
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    status = request.args.get('status', '')

    query = Product.query.filter_by(publisher_id=user_id)
    if status:
        query = query.filter(Product.status == status)

    query = query.order_by(Product.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [serialize_product(p) for p in result['items']]
    return jsonify(result), 200


@products_bp.route('', methods=['POST'])
@role_required('publisher')
def create_product():
    user_id = int(get_jwt_identity())
    data = get_request_data()

    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400

    required = ['product_name', 'price', 'stock']
    for f in required:
        if str(data.get(f, '')).strip() == '':
            return jsonify({'error': f'{f} 不能为空'}), 400

    try:
        price = float(data['price'])
        stock = int(data['stock'])
    except (TypeError, ValueError):
        return jsonify({'error': '价格或库存格式不正确'}), 400

    if price <= 0:
        return jsonify({'error': '价格必须大于0'}), 400
    if stock < 0:
        return jsonify({'error': '库存不能为负数'}), 400

    image_file = request.files.get('image')
    cover_image = data.get('cover_image')

    try:
        if image_file:
            cover_image = save_uploaded_product_image(image_file)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    product = Product(
        publisher_id=user_id,
        product_name=data['product_name'].strip(),
        category=data.get('category'),
        description=data.get('description'),
        cover_image=cover_image,
        price=price,
        stock=stock,
        status='online',
    )
    db.session.add(product)
    db.session.flush()

    if cover_image:
        db.session.add(ProductImage(product_id=product.product_id, image_url=cover_image))

    images = request.form.getlist('images') if request.form else data.get('images', [])
    if isinstance(images, list):
        existing_urls = {cover_image} if cover_image else set()
        for img_url in images:
            if img_url and img_url not in existing_urls:
                db.session.add(ProductImage(product_id=product.product_id, image_url=img_url))

    db.session.commit()
    return jsonify({'message': '商品创建成功', 'product': serialize_product(product)}), 201


@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    product = Product.query.get_or_404(product_id)

    if product.publisher_id != user_id and user.role_type != 'admin':
        return jsonify({'error': '无权操作'}), 403

    data = get_request_data()
    image_file = request.files.get('image')

    updatable = ['product_name', 'category', 'description', 'cover_image', 'status']
    for field in updatable:
        if field in data and data[field] is not None:
            setattr(product, field, data[field])

    if 'price' in data:
        try:
            price = float(data['price'])
            if price <= 0:
                return jsonify({'error': '价格必须大于0'}), 400
            product.price = price
        except (TypeError, ValueError):
            return jsonify({'error': '价格格式不正确'}), 400

    if 'stock' in data:
        try:
            stock = int(data['stock'])
            if stock < 0:
                return jsonify({'error': '库存不能为负数'}), 400
            product.stock = stock
        except (TypeError, ValueError):
            return jsonify({'error': '库存格式不正确'}), 400

    try:
        if image_file:
            new_cover = save_uploaded_product_image(image_file)
            product.cover_image = new_cover

            ProductImage.query.filter_by(product_id=product_id).delete()
            db.session.add(ProductImage(product_id=product_id, image_url=new_cover))
        elif request.form and 'images' in request.form:
            ProductImage.query.filter_by(product_id=product_id).delete()
            for img_url in request.form.getlist('images'):
                if img_url:
                    db.session.add(ProductImage(product_id=product_id, image_url=img_url))
        elif isinstance(data.get('images'), list):
            ProductImage.query.filter_by(product_id=product_id).delete()
            for img_url in data['images']:
                if img_url:
                    db.session.add(ProductImage(product_id=product_id, image_url=img_url))
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    db.session.commit()
    return jsonify({'message': '更新成功', 'product': serialize_product(product)}), 200


@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    product = Product.query.get_or_404(product_id)

    if product.publisher_id != user_id and user.role_type != 'admin':
        return jsonify({'error': '无权操作'}), 403

    product.status = 'offline'
    db.session.commit()
    return jsonify({'message': '商品已下架'}), 200
