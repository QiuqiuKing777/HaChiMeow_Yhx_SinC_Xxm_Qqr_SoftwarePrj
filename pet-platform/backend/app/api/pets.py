from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request

from app.extensions import db
from app.models import Pet, PetImage, User
from app.utils import role_required, paginate_query

pets_bp = Blueprint('pets', __name__, url_prefix='/api/pets')


@pets_bp.route('', methods=['GET'])
def list_pets():
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    species  = request.args.get('species', '')
    breed    = request.args.get('breed', '')
    gender   = request.args.get('gender', '')
    location = request.args.get('location', '')
    keyword  = request.args.get('keyword', '')

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
        query = query.filter(Pet.pet_name.ilike(f'%{keyword}%') | Pet.description.ilike(f'%{keyword}%'))

    query = query.order_by(Pet.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [p.to_dict() for p in result['items']]
    return jsonify(result), 200


@pets_bp.route('/<int:pet_id>', methods=['GET'])
def get_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    # 增加浏览量
    pet.view_count += 1
    db.session.commit()
    return jsonify(pet.to_dict()), 200


@pets_bp.route('/my', methods=['GET'])
@role_required('publisher')
def my_pets():
    user_id  = get_jwt_identity()
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    status   = request.args.get('status', '')

    query = Pet.query.filter_by(publisher_id=user_id)
    if status:
        query = query.filter(Pet.status == status)
    query = query.order_by(Pet.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [p.to_dict() for p in result['items']]
    return jsonify(result), 200


@pets_bp.route('', methods=['POST'])
@role_required('publisher')
def create_pet():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400

    required = ['pet_name', 'species']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} 不能为空'}), 400

    pet = Pet(
        publisher_id=user_id,
        pet_name=data['pet_name'],
        species=data['species'],
        breed=data.get('breed'),
        age_desc=data.get('age_desc'),
        gender=data.get('gender', 'unknown'),
        health_status=data.get('health_status'),
        adoption_requirements=data.get('adoption_requirements'),
        location=data.get('location'),
        description=data.get('description'),
        cover_image=data.get('cover_image'),
        status='online',  # 发布方直接上线，管理员可后台下架
    )
    db.session.add(pet)
    db.session.flush()

    for img_url in data.get('images', []):
        db.session.add(PetImage(pet_id=pet.pet_id, image_url=img_url))

    db.session.commit()
    return jsonify({'message': '宠物信息发布成功', 'pet': pet.to_dict()}), 201


@pets_bp.route('/<int:pet_id>', methods=['PUT'])
@jwt_required()
def update_pet(pet_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    pet  = Pet.query.get_or_404(pet_id)

    if pet.publisher_id != user_id and user.role_type != 'admin':
        return jsonify({'error': '无权操作'}), 403

    data = request.get_json() or {}
    updatable = ['pet_name', 'species', 'breed', 'age_desc', 'gender',
                 'health_status', 'adoption_requirements', 'location',
                 'description', 'cover_image', 'status']
    for field in updatable:
        if field in data:
            setattr(pet, field, data[field])

    if 'images' in data:
        PetImage.query.filter_by(pet_id=pet_id).delete()
        for img_url in data['images']:
            db.session.add(PetImage(pet_id=pet_id, image_url=img_url))

    db.session.commit()
    return jsonify({'message': '更新成功', 'pet': pet.to_dict()}), 200


@pets_bp.route('/<int:pet_id>', methods=['DELETE'])
@jwt_required()
def delete_pet(pet_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    pet  = Pet.query.get_or_404(pet_id)

    if pet.publisher_id != user_id and user.role_type != 'admin':
        return jsonify({'error': '无权操作'}), 403

    pet.status = 'offline'
    db.session.commit()
    return jsonify({'message': '宠物信息已下架'}), 200
