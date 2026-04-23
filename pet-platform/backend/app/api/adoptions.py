from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import AdoptionApplication, Pet, User
from app.utils import role_required, paginate_query, send_notification

adoptions_bp = Blueprint('adoptions', __name__, url_prefix='/api/adoptions')


@adoptions_bp.route('', methods=['POST'])
@role_required('user')
def submit_application():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400

    pet_id = data.get('pet_id')
    if not pet_id:
        return jsonify({'error': '请选择要申请的宠物'}), 400

    pet = Pet.query.get_or_404(pet_id)
    if pet.status != 'online':
        return jsonify({'error': '该宠物当前不可申请领养'}), 400

    # 检查是否已有未完结申请
    existing = AdoptionApplication.query.filter_by(
        pet_id=pet_id,
        applicant_id=user_id,
    ).filter(AdoptionApplication.review_status.in_(['pending', 'supplement'])).first()
    if existing:
        return jsonify({'error': '您已提交过该宠物的领养申请，请等待审核'}), 409

    required_fields = ['housing_info', 'promise_statement']
    for f in required_fields:
        if not data.get(f):
            return jsonify({'error': f'{f} 不能为空'}), 400

    # 检查是否曾有已通过后被本人取消的申请（满足则自动审批，无需发布方再次审核）
    prev_cancelled_approved = AdoptionApplication.query.filter_by(
        pet_id=pet_id,
        applicant_id=user_id,
        review_status='cancelled',
        review_remark='cancelled_from_approved',
    ).first()

    app_obj = AdoptionApplication(
        pet_id=pet_id,
        applicant_id=user_id,
        housing_info=data['housing_info'],
        pet_experience=data.get('pet_experience'),
        family_attitude=data.get('family_attitude'),
        promise_statement=data['promise_statement'],
        contact_info=data.get('contact_info'),
    )

    if prev_cancelled_approved:
        # 曾被审批通过后主动取消，直接自动审批通过，无需发布方再次审核
        app_obj.review_status = 'approved'
        app_obj.review_remark = '曾领养后自行取消，自动重新通过'
        app_obj.reviewed_at = datetime.utcnow()
        pet.status = 'adopted'
        # 将同一宠物其他待审核申请设为已拒绝
        AdoptionApplication.query.filter(
            AdoptionApplication.pet_id == pet.pet_id,
            AdoptionApplication.review_status == 'pending',
        ).update({'review_status': 'rejected', 'review_remark': '该宠物已被他人领养'})
        db.session.add(app_obj)
        db.session.commit()
        send_notification(
            app_obj.applicant_id, 'adoption',
            f'您关于「{pet.pet_name}」的领养申请已自动通过',
            '由于您曾领养该宠物后主动取消，此次申请已自动审批通过，无需等待审核。'
        )
        return jsonify({'message': '申请已自动通过，恭喜您重新领养成功！', 'application': app_obj.to_dict()}), 201

    db.session.add(app_obj)
    db.session.commit()

    # 通知发布方
    send_notification(
        pet.publisher_id, 'adoption',
        f'您的宠物「{pet.pet_name}」收到新的领养申请',
        f'申请人已提交申请，请及时查看并审核。'
    )
    return jsonify({'message': '申请提交成功，等待发布方审核', 'application': app_obj.to_dict()}), 201


@adoptions_bp.route('/my', methods=['GET'])
@jwt_required()
def my_applications():
    user_id  = get_jwt_identity()
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status   = request.args.get('status', '')

    query = AdoptionApplication.query.filter_by(applicant_id=user_id)
    if status:
        query = query.filter(AdoptionApplication.review_status == status)
    query = query.order_by(AdoptionApplication.submitted_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [a.to_dict() for a in result['items']]
    return jsonify(result), 200


@adoptions_bp.route('/publisher', methods=['GET'])
@role_required('publisher')
def publisher_applications():
    user_id  = get_jwt_identity()
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status   = request.args.get('status', '')

    # 查询发布方名下所有宠物的申请
    pet_ids = [p.pet_id for p in Pet.query.filter_by(publisher_id=user_id).all()]
    if not pet_ids:
        return jsonify({'items': [], 'total': 0, 'page': 1, 'pages': 0, 'per_page': per_page}), 200

    query = AdoptionApplication.query.filter(AdoptionApplication.pet_id.in_(pet_ids))
    if status:
        query = query.filter(AdoptionApplication.review_status == status)
    query = query.order_by(AdoptionApplication.submitted_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [a.to_dict() for a in result['items']]
    return jsonify(result), 200


@adoptions_bp.route('/<int:application_id>', methods=['GET'])
@jwt_required()
def get_application(application_id):
    user_id = get_jwt_identity()
    user    = User.query.get(user_id)
    app_obj = AdoptionApplication.query.get_or_404(application_id)

    # 权限：申请人本人 / 宠物发布方 / 管理员
    is_applicant  = (app_obj.applicant_id == user_id)
    is_publisher  = (app_obj.pet.publisher_id == user_id)
    is_admin      = (user.role_type == 'admin')
    if not (is_applicant or is_publisher or is_admin):
        return jsonify({'error': '无权查看'}), 403

    return jsonify(app_obj.to_dict()), 200


@adoptions_bp.route('/<int:application_id>/review', methods=['PUT'])
@role_required('publisher')
def review_application(application_id):
    user_id = get_jwt_identity()
    app_obj = AdoptionApplication.query.get_or_404(application_id)
    pet     = pet = app_obj.pet

    if pet.publisher_id != user_id:
        return jsonify({'error': '无权操作此申请'}), 403
    if app_obj.review_status not in ('pending', 'supplement'):
        return jsonify({'error': '该申请已完成审核，不可重复操作'}), 400

    data   = request.get_json() or {}
    status = data.get('review_status')
    if status not in ('approved', 'rejected', 'supplement'):
        return jsonify({'error': 'review_status 无效，可选值: approved/rejected/supplement'}), 400

    app_obj.review_status = status
    app_obj.review_remark = data.get('review_remark', '')
    app_obj.reviewed_by   = user_id
    app_obj.reviewed_at   = datetime.utcnow()

    if status == 'approved':
        # 宠物标记为已领养，并拒绝其他待审核申请
        pet.status = 'adopted'
        AdoptionApplication.query.filter(
            AdoptionApplication.pet_id == pet.pet_id,
            AdoptionApplication.application_id != application_id,
            AdoptionApplication.review_status == 'pending',
        ).update({'review_status': 'rejected', 'review_remark': '该宠物已被他人领养'})

    db.session.commit()

    # 通知申请人
    status_map = {'approved': '已通过', 'rejected': '已拒绝', 'supplement': '需补充材料'}
    send_notification(
        app_obj.applicant_id, 'adoption',
        f'您关于「{pet.pet_name}」的领养申请{status_map[status]}',
        app_obj.review_remark or ''
    )
    return jsonify({'message': '审核完成', 'application': app_obj.to_dict()}), 200


@adoptions_bp.route('/<int:application_id>', methods=['DELETE'])
@role_required('user')
def cancel_application(application_id):
    user_id = get_jwt_identity()
    app_obj = AdoptionApplication.query.get_or_404(application_id)

    if app_obj.applicant_id != user_id:
        return jsonify({'error': '无权操作'}), 403
    if app_obj.review_status not in ('pending', 'supplement', 'approved'):
        return jsonify({'error': '只能取消待审核、需补材料或已通过的申请'}), 400

    was_approved = (app_obj.review_status == 'approved')

    # 将申请标记为已取消（保留记录以供后续自动审批逻辑判断）
    app_obj.review_status = 'cancelled'
    if was_approved:
        # 标记为「已通过后取消」，再次申请时可自动审批
        app_obj.review_remark = 'cancelled_from_approved'
        # 恢复宠物状态为可领养
        pet = app_obj.pet
        pet.status = 'online'
        send_notification(
            pet.publisher_id, 'adoption',
            f'用户已取消对「{pet.pet_name}」的领养',
            '该宠物已自动重新上架，可接受新的领养申请。'
        )

    db.session.commit()
    return jsonify({'message': '申请已取消', 'pet_restored': was_approved}), 200
