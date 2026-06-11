"""TC-001 用户注册成功 / TC-002 用户登录成功 / TC-003 登录密码错误"""

import pytest
from app.models import User


class TestUserRegister:
    """TC-001: 用户注册成功"""

    def test_register_success(self, client, app):
        resp = client.post('/api/auth/register', json={
            'username': 'testuser',
            'password': '123456',
            'nickname': '测试用户',
            'phone': '13800000000',
            'email': 'test@example.com',
            'role_type': 'user',
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['message'] == '注册成功'
        assert 'token' in data
        assert data['user']['username'] == 'testuser'

        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            assert user is not None
            assert user.password_hash != '123456'

    def test_register_missing_password(self, client):
        resp = client.post('/api/auth/register', json={
            'username': 'testuser',
            'password': '',
        })
        assert resp.status_code == 400

    def test_register_existing_username(self, client, normal_user):
        resp = client.post('/api/auth/register', json={
            'username': 'normaluser',
            'password': '123456',
        })
        assert resp.status_code == 409
        data = resp.get_json()
        assert '用户名已存在' in data['error']


class TestUserLogin:
    """TC-002: 用户登录成功 / TC-003: 登录密码错误"""

    def test_login_success(self, client, normal_user):
        resp = client.post('/api/auth/login', json={
            'username': 'normaluser',
            'password': '123456',
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['message'] == '登录成功'
        assert 'token' in data
        assert data['user']['username'] == 'normaluser'

    def test_login_wrong_password(self, client, normal_user):
        """TC-003: 密码错误"""
        resp = client.post('/api/auth/login', json={
            'username': 'normaluser',
            'password': 'wrongpwd',
        })
        assert resp.status_code == 401
        data = resp.get_json()
        assert '用户名或密码错误' in data['error']

    def test_login_nonexistent_user(self, client):
        resp = client.post('/api/auth/login', json={
            'username': 'nobody',
            'password': '123456',
        })
        assert resp.status_code == 401

    def test_login_disabled_user(self, client, app):
        from werkzeug.security import generate_password_hash
        from app.extensions import db
        from app.models import User

        user = User(
            username='disableduser',
            password_hash=generate_password_hash('123456'),
            role_type='user',
            status='disabled',
        )
        db.session.add(user)
        db.session.commit()

        resp = client.post('/api/auth/login', json={
            'username': 'disableduser',
            'password': '123456',
        })
        assert resp.status_code == 403

    def test_get_me(self, client, normal_user_token, normal_user_auth):
        resp = client.get('/api/auth/me', headers=normal_user_auth)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['username'] == 'normaluser'
