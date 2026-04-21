from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import Review
from app.utils import role_required

reviews_bp = Blueprint('reviews', __name__, url_prefix='/api/reviews')


@reviews_bp.route('', methods=['POST'])
@jwt_required()
def create_review():
    user_id = get_jwt_identity()
    data    = request.get_json() or {}

    target_type = data.get('target_type')
    target_id   = data.get('target_id')
    rating      = data.get('rating')
    content     = data.get('content', '')

    if target_type not in ('order', 'booking', 'pet'):
        return jsonify({'error': 'target_type 无效'}), 400
    if not target_id:
        return jsonify({'error': 'target_id 不能为空'}), 400
    if not rating or int(rating) not in range(1, 6):
        return jsonify({'error': '评分必须在1-5之间'}), 400

    # 防止重复评价
    existing = Review.query.filter_by(
        reviewer_id=user_id, target_type=target_type, target_id=target_id
    ).first()
    if existing:
        return jsonify({'error': '您已评价过'}), 409

    review = Review(
        reviewer_id=user_id,
        target_type=target_type,
        target_id=target_id,
        rating=rating,
        content=content,
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({'message': '评价成功', 'review': review.to_dict()}), 201


@reviews_bp.route('', methods=['GET'])
def list_reviews():
    target_type = request.args.get('target_type', '')
    target_id   = request.args.get('target_id', type=int)

    if not target_type or not target_id:
        return jsonify({'error': 'target_type 和 target_id 必须提供'}), 400

    reviews = Review.query.filter_by(
        target_type=target_type, target_id=target_id
    ).order_by(Review.created_at.desc()).all()
    return jsonify([r.to_dict() for r in reviews]), 200
