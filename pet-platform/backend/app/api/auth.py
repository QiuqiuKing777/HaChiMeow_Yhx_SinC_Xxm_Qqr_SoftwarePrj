from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app.extensions import db
from app.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')
    nickname = data.get('nickname', username)
    phone    = data.get('phone', '')
    email    = data.get('email', '')
    role_type = data.get('role_type', 'user')

    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    if len(username) < 3 or len(username) > 50:
        return jsonify({'error': '用户名长度需在3-50个字符之间'}), 400
    if len(password) < 6:
        return jsonify({'error': '密码长度不能少于6位'}), 400
    if role_type not in ('user', 'publisher'):
        role_type = 'user'

    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已存在'}), 409

    user = User(
        username=username,
        password_hash=generate_password_hash(password),
        nickname=nickname,
        phone=phone,
        email=email,
        role_type=role_type,
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=user.user_id)
    return jsonify({'message': '注册成功', 'token': token, 'user': user.to_dict()}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据不能为空'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': '用户名或密码错误'}), 401
    if user.status == 'disabled':
        return jsonify({'error': '账号已被禁用，请联系管理员'}), 403

    token = create_access_token(identity=user.user_id)
    return jsonify({'message': '登录成功', 'token': token, 'user': user.to_dict()}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    return jsonify(user.to_dict()), 200
