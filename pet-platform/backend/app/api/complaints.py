from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import Complaint

complaints_bp = Blueprint('complaints', __name__, url_prefix='/api/complaints')


@complaints_bp.route('', methods=['GET'])
def list_complaints():
    target_type = request.args.get('target_type')
    target_id = request.args.get('target_id', type=int)

    type_map = {
        'pet': 'pets',
        'pets': 'pets',
        'product': 'products',
        'products': 'products',
        'service': 'services',
        'services': 'services',
    }

    if target_type:
        target_type = type_map.get(str(target_type).strip(), target_type)

    query = Complaint.query

    if target_type:
        query = query.filter(Complaint.target_type == target_type)

    if target_id:
        query = query.filter(Complaint.target_id == target_id)

    complaints = query.order_by(Complaint.created_at.desc()).all()

    # 这里故意返回成“评价组件能直接用”的格式
    return jsonify([
        {
            'review_id': c.complaint_id,
            'complaint_id': c.complaint_id,

            'reviewer_id': c.user_id,
            'reviewer': c.user.to_public_dict() if c.user else None,
            'user': c.user.to_public_dict() if c.user else None,

            'target_type': c.target_type,
            'target_id': c.target_id,

            'rating': c.score,
            'score': c.score,

            'content': c.content,
            'status': c.status,

            'created_at': c.created_at.isoformat() if c.created_at else None,
        }
        for c in complaints
    ]), 200


@complaints_bp.route('', methods=['POST'])
@jwt_required()
def create_complaint():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    target_type = data.get('target_type')
    target_id = data.get('target_id')
    score = data.get('score', 5)
    content = (data.get('content') or '').strip()

    if not target_type:
        return jsonify({'error': 'target_type 不能为空'}), 400

    if not target_id:
        return jsonify({'error': 'target_id 不能为空'}), 400

    if not content:
        return jsonify({'error': 'content 不能为空'}), 400

    try:
        complaint = Complaint(
            user_id=user_id,
            target_type=target_type,
            target_id=target_id,
            score=score,
            content=content,
            status='pending'
        )

        db.session.add(complaint)
        db.session.commit()

        return jsonify({
            'message': '评价提交成功',
            'complaint': complaint.to_dict()
        }), 201

    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

    except Exception:
        db.session.rollback()
        return jsonify({'error': '评价提交失败'}), 500
