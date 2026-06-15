from datetime import datetime, timedelta
import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import PetFeedback, AdoptionApplication, Pet
from app.utils import role_required, paginate_query, send_notification

feedbacks_bp = Blueprint('feedbacks', __name__, url_prefix='/api/feedbacks')


def _build_full_image_url(path):
    """Convert relative path to full URL (same pattern as pets.py)."""
    if not path:
        return None
    base = request.host_url.rstrip('/')
    if path.startswith('http://') or path.startswith('https://'):
        return path
    if path.startswith('/static/'):
        return f'{base}{path}'
    if path.startswith('uploads/'):
        return f'{base}/static/{path}'
    if path.startswith('/'):
        return f'{base}{path}'
    return f'{base}/{path}'


def _serialize_feedback(fb):
    data = fb.to_dict()
    data['photo_url'] = _build_full_image_url(data.get('photo_url'))
    return data


def _save_photo(file) -> str:
    """Save uploaded photo and return relative path."""
    ext = file.filename.rsplit('.', 1)[-1] if '.' in (file.filename or '') else 'jpg'
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'feedbacks')
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)
    return f"/static/uploads/feedbacks/{filename}"


@feedbacks_bp.route('', methods=['POST'])
@role_required('user')
def submit_feedback():
    user_id = int(get_jwt_identity())

    application_id = request.form.get('application_id', type=int)
    if not application_id:
        return jsonify({'error': 'application_id 不能为空'}), 400

    app_obj = AdoptionApplication.query.get_or_404(application_id)
    if app_obj.applicant_id != user_id:
        return jsonify({'error': '无权操作'}), 403
    if app_obj.review_status != 'approved':
        return jsonify({'error': '只有已通过的领养申请才能提交反馈'}), 400

    photo_url = None
    if 'photo' in request.files:
        photo_url = _save_photo(request.files['photo'])

    weight = request.form.get('weight', type=float)
    notes = request.form.get('notes', '')

    feedback = PetFeedback(
        pet_id=app_obj.pet_id,
        application_id=application_id,
        user_id=user_id,
        photo_url=photo_url,
        weight=weight,
        notes=notes,
    )
    db.session.add(feedback)
    db.session.commit()

    send_notification(
        app_obj.pet.publisher_id, 'feedback',
        f'宠物「{app_obj.pet.pet_name}」收到新的状态反馈',
        f'领养者已提交了宠物的最新状态反馈，请及时查看。'
    )

    return jsonify({'message': '反馈提交成功', 'feedback': _serialize_feedback(feedback)}), 201


@feedbacks_bp.route('/my', methods=['GET'])
@jwt_required()
def my_feedbacks():
    user_id = int(get_jwt_identity())
    application_id = request.args.get('application_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = PetFeedback.query.filter_by(user_id=user_id)
    if application_id:
        query = query.filter_by(application_id=application_id)
    query = query.order_by(PetFeedback.created_at.desc())

    result = paginate_query(query, page, per_page)
    result['items'] = [_serialize_feedback(f) for f in result['items']]
    return jsonify(result), 200


@feedbacks_bp.route('/pet/<int:pet_id>', methods=['GET'])
@role_required('publisher')
def pet_feedbacks(pet_id):
    user_id = int(get_jwt_identity())

    pet = Pet.query.get_or_404(pet_id)
    if pet.publisher_id != user_id:
        return jsonify({'error': '无权查看'}), 403

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = PetFeedback.query.filter_by(pet_id=pet_id).order_by(PetFeedback.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [_serialize_feedback(f) for f in result['items']]

    # 附上宠物基本信息
    result['pet'] = {
        'pet_id': pet.pet_id,
        'pet_name': pet.pet_name,
        'species': pet.species,
        'breed': pet.breed,
        'cover_image': pet.cover_image,
        'status': pet.status,
    }

    return jsonify(result), 200


@feedbacks_bp.route('/status/<int:application_id>', methods=['GET'])
@jwt_required()
def feedback_status(application_id):
    """获取某领养申请的反馈状态（是否逾期、下次反馈时间等）"""
    user_id = int(get_jwt_identity())

    app_obj = AdoptionApplication.query.get_or_404(application_id)
    if app_obj.applicant_id != user_id and app_obj.pet.publisher_id != user_id:
        return jsonify({'error': '无权查看'}), 403

    if app_obj.review_status != 'approved':
        return jsonify({'error': '该申请尚未通过'}), 400

    latest = PetFeedback.query.filter_by(application_id=application_id)\
        .order_by(PetFeedback.created_at.desc()).first()

    interval_days = 3

    if latest:
        last_date = latest.created_at
        next_due = last_date + timedelta(days=interval_days)
        overdue = datetime.utcnow() > next_due
        days_since = (datetime.utcnow() - last_date).days
    else:
        last_date = app_obj.reviewed_at or app_obj.submitted_at
        next_due = last_date + timedelta(days=interval_days)
        overdue = datetime.utcnow() > next_due
        days_since = (datetime.utcnow() - last_date).days

    days_remaining = max(0, (next_due - datetime.utcnow()).days)

    return jsonify({
        'application_id': application_id,
        'last_feedback_date': latest.created_at.isoformat() if latest else None,
        'next_due_date': next_due.isoformat(),
        'overdue': overdue,
        'days_since_last': days_since,
        'days_remaining': days_remaining,
        'total_count': PetFeedback.query.filter_by(application_id=application_id).count(),
        'status': 'overdue' if overdue else 'ok',
    }), 200
