import uuid
from pathlib import Path

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Pet, PetImage, User
from app.utils import role_required, paginate_query

pets_bp = Blueprint('pets', __name__, url_prefix='/api/pets')

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


def serialize_pet(pet):
    data = pet.to_dict()

    data['cover_image'] = build_full_image_url(data.get('cover_image'))

    images = data.get('images') or []
    for img in images:
        img['image_url'] = build_full_image_url(img.get('image_url'))

    return data


def save_uploaded_pet_image(file_storage):
    if not file_storage or not file_storage.filename:
        return None

    filename = secure_filename(file_storage.filename)
    if not filename:
        return None

    if not allowed_image_file(filename):
        raise ValueError('仅支持 PNG、JPG、JPEG、SVG 格式图片')

    ext = filename.rsplit('.', 1)[1].lower()
    new_filename = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = Path(current_app.static_folder) / 'uploads' / 'pets'
    upload_dir.mkdir(parents=True, exist_ok=True)

    save_path = upload_dir / new_filename
    file_storage.save(save_path)

    return f"/static/uploads/pets/{new_filename}"


def get_request_data():
    if request.content_type and 'multipart/form-data' in request.content_type:
        return request.form.to_dict()
    return request.get_json(silent=True) or {}


@pets_bp.route('', methods=['GET'])
def list_pets():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    species = request.args.get('species', '')
    breed = request.args.get('breed', '')
    gender = request.args.get('gender', '')
    location = request.args.get('location', '')
    keyword = request.args.get('keyword', '')

    query = Pet.query.filter_by(status='online')
    if species:
        query = query.filter(Pet.species == species)
    if breed:
        query = query.filter(Pet.breed.ilike(f'%{breed}%'))
    if gender:
        query = query.filter(Pet.gender == gender)
    if location:
        query = query.filter(Pet.location.ilike(f'%{location}%'))
    if keyword:
        query = query.filter(
            Pet.pet_name.ilike(f'%{keyword}%') | Pet.description.ilike(f'%{keyword}%')
        )

    query = query.order_by(Pet.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [serialize_pet(p) for p in result['items']]
    return jsonify(result), 200


@pets_bp.route('/<int:pet_id>', methods=['GET'])
def get_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    pet.view_count += 1
    db.session.commit()
    return jsonify(serialize_pet(pet)), 200


@pets_bp.route('/my', methods=['GET'])
@role_required('publisher')
def my_pets():
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    status = request.args.get('status', '')

    query = Pet.query.filter_by(publisher_id=user_id).filter(Pet.status != 'offline')
    if status:
        query = query.filter(Pet.status == status)

    query = query.order_by(Pet.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [serialize_pet(p) for p in result['items']]
    return jsonify(result), 200


@pets_bp.route('', methods=['POST'])
@role_required('publisher')
def create_pet():
    user_id = int(get_jwt_identity())
    data = get_request_data()

    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400

    required = ['pet_name', 'species']
    for field in required:
        if not str(data.get(field, '')).strip():
            return jsonify({'error': f'{field} 不能为空'}), 400

    image_file = request.files.get('image')
    cover_image = data.get('cover_image')

    try:
        if image_file:
            cover_image = save_uploaded_pet_image(image_file)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    pet = Pet(
        publisher_id=user_id,
        pet_name=data['pet_name'].strip(),
        species=data['species'].strip(),
        breed=data.get('breed'),
        age_desc=data.get('age_desc'),
        gender=data.get('gender', 'unknown'),
        health_status=data.get('health_status'),
        adoption_requirements=data.get('adoption_requirements'),
        location=data.get('location'),
        description=data.get('description'),
        cover_image=cover_image,
        status='online',
    )
    db.session.add(pet)
    db.session.flush()

    if cover_image:
        db.session.add(PetImage(pet_id=pet.pet_id, image_url=cover_image))

    images = request.form.getlist('images') if request.form else data.get('images', [])
    if isinstance(images, list):
        existing_urls = {cover_image} if cover_image else set()
        for img_url in images:
            if img_url and img_url not in existing_urls:
                db.session.add(PetImage(pet_id=pet.pet_id, image_url=img_url))

    db.session.commit()
    return jsonify({'message': '宠物信息发布成功', 'pet': serialize_pet(pet)}), 201


@pets_bp.route('/<int:pet_id>', methods=['PUT'])
@jwt_required()
def update_pet(pet_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    pet = Pet.query.get_or_404(pet_id)

    if pet.publisher_id != user_id and user.role_type != 'admin':
        return jsonify({'error': '无权操作'}), 403

    data = get_request_data()
    image_file = request.files.get('image')

    updatable = [
        'pet_name', 'species', 'breed', 'age_desc', 'gender',
        'health_status', 'adoption_requirements', 'location',
        'description', 'cover_image', 'status'
    ]

    for field in updatable:
        if field in data and data[field] is not None:
            setattr(pet, field, data[field])

    try:
        if image_file:
            new_cover = save_uploaded_pet_image(image_file)
            pet.cover_image = new_cover

            PetImage.query.filter_by(pet_id=pet_id).delete()
            db.session.add(PetImage(pet_id=pet_id, image_url=new_cover))
        elif request.form and 'images' in request.form:
            PetImage.query.filter_by(pet_id=pet_id).delete()
            for img_url in request.form.getlist('images'):
                if img_url:
                    db.session.add(PetImage(pet_id=pet_id, image_url=img_url))
        elif isinstance(data.get('images'), list):
            PetImage.query.filter_by(pet_id=pet_id).delete()
            for img_url in data['images']:
                if img_url:
                    db.session.add(PetImage(pet_id=pet_id, image_url=img_url))
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    db.session.commit()
    return jsonify({'message': '更新成功', 'pet': serialize_pet(pet)}), 200


@pets_bp.route('/<int:pet_id>', methods=['DELETE'])
@jwt_required()
def delete_pet(pet_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    pet = Pet.query.get_or_404(pet_id)

    if pet.publisher_id != user_id and user.role_type != 'admin':
        return jsonify({'error': '无权操作'}), 403

    pet.status = 'offline'
    db.session.commit()
    return jsonify({'message': '宠物信息已下架'}), 200
