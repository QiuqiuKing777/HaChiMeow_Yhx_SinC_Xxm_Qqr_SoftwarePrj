from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify
from app.models import User


def role_required(*roles):
    """角色权限装饰器，支持多角色"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': '用户不存在'}), 401
            if user.status == 'disabled':
                return jsonify({'error': '账号已被禁用'}), 403
            if user.role_type not in roles:
                return jsonify({'error': '权限不足'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


def log_action(action, target_type=None, target_id=None, detail=None):
    """记录操作日志"""
    from app.models import OperationLog
    from app.extensions import db
    try:
        user_id = get_jwt_identity()
        log = OperationLog(
            operator_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            detail=detail,
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        pass


def send_notification(user_id, type_, title, content=''):
    """发送系统通知"""
    from app.models import Notification
    from app.extensions import db
    try:
        note = Notification(user_id=user_id, type=type_, title=title, content=content)
        db.session.add(note)
        db.session.commit()
    except Exception:
        pass


def paginate_query(query, page, per_page):
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'items': pagination.items,
        'total': pagination.total,
        'page':  pagination.page,
        'pages': pagination.pages,
        'per_page': pagination.per_page,
    }
