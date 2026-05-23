from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import Complaint
from app.utils import role_required, paginate_query

complaints_bp = Blueprint('complaints', __name__, url_prefix='/api/complaints')

VALID_TARGET_TYPES = ('order', 'booking', 'pet', 'product', 'service', 'user')


@complaints_bp.route('', methods=['POST'])
@jwt_required()
def submit_complaint():
    """用户提交投诉"""
    user_id = get_jwt_identity()
    data    = request.get_json() or {}

    target_type = data.get('target_type', '').strip()
    target_id   = data.get('target_id')
    content     = data.get('content', '').strip()

    if target_type not in VALID_TARGET_TYPES:
        return jsonify({'error': f'target_type 无效，可选值: {", ".join(VALID_TARGET_TYPES)}'}), 400
    if not target_id:
        return jsonify({'error': 'target_id 不能为空'}), 400
    if not content:
        return jsonify({'error': '投诉内容不能为空'}), 400
    if len(content) > 1000:
        return jsonify({'error': '投诉内容不能超过1000字'}), 400

    complaint = Complaint(
        user_id=user_id,
        target_type=target_type,
        target_id=int(target_id),
        content=content,
    )
    db.session.add(complaint)
    db.session.commit()
    return jsonify({'message': '投诉已提交，等待管理员处理', 'complaint': complaint.to_dict()}), 201


@complaints_bp.route('/mine', methods=['GET'])
@jwt_required()
def my_complaints():
    """查看我的投诉记录"""
    user_id  = get_jwt_identity()
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status   = request.args.get('status', '')

    query = Complaint.query.filter_by(user_id=user_id)
    if status:
        query = query.filter(Complaint.status == status)
    query = query.order_by(Complaint.created_at.desc())
    result = paginate_query(query, page, per_page)
    result['items'] = [c.to_dict() for c in result['items']]
    return jsonify(result), 200
