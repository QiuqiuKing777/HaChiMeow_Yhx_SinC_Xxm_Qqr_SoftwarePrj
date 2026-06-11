"""TC-017 管理员查看用户列表 / TC-018 管理员审核内容 / TC-019 查看统计数据 / TC-020 操作日志记录"""

import pytest


class TestAdminUserList:
    """TC-017: 管理员查看用户列表"""

    def test_admin_list_users(self, client, admin_user_auth, normal_user, publisher_user):
        resp = client.get('/api/admin/users', headers=admin_user_auth)
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'items' in data
        assert data['total'] >= 2

    def test_admin_list_users_filter_role(self, client, admin_user_auth, normal_user, publisher_user):
        resp = client.get('/api/admin/users?role_type=user', headers=admin_user_auth)
        assert resp.status_code == 200
        data = resp.get_json()
        for u in data['items']:
            assert u['role_type'] == 'user'

    def test_admin_list_users_unauthorized(self, client, normal_user_auth):
        resp = client.get('/api/admin/users', headers=normal_user_auth)
        assert resp.status_code == 403

    def test_admin_set_user_status(self, client, admin_user_auth, normal_user):
        resp = client.put(
            f'/api/admin/users/{normal_user.user_id}/status',
            json={'status': 'disabled'},
            headers=admin_user_auth,
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['user']['status'] == 'disabled'

    def test_admin_cannot_disable_self(self, client, admin_user_auth, admin_user):
        resp = client.put(
            f'/api/admin/users/{admin_user.user_id}/status',
            json={'status': 'disabled'},
            headers=admin_user_auth,
        )
        assert resp.status_code == 403


class TestAdminContentAudit:
    """TC-018: 管理员审核内容"""

    def test_admin_audit_pet_approve(self, client, admin_user_auth, app, publisher_user):
        from app.extensions import db
        from app.models import Pet

        pet = Pet(
            publisher_id=publisher_user.user_id,
            pet_name='待审宠物',
            species='猫',
            breed='英短',
            status='pending',
        )
        db.session.add(pet)
        db.session.commit()

        resp = client.put(
            f'/api/admin/pets/{pet.pet_id}/status',
            json={'status': 'online'},
            headers=admin_user_auth,
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert '已更新' in data['message']

        with app.app_context():
            updated_pet = db.session.get(Pet, pet.pet_id)
            assert updated_pet.status == 'online'

    def test_admin_audit_product_approve(self, client, admin_user_auth, app, publisher_user):
        from app.extensions import db
        from app.models import Product

        product = Product(
            publisher_id=publisher_user.user_id,
            product_name='待审商品',
            price=50.00,
            stock=20,
            status='pending',
        )
        db.session.add(product)
        db.session.commit()

        resp = client.put(
            f'/api/admin/products/{product.product_id}/status',
            json={'status': 'online'},
            headers=admin_user_auth,
        )
        assert resp.status_code == 200

    def test_admin_audit_service_approve(self, client, admin_user_auth, app, publisher_user):
        from app.extensions import db
        from app.models import Service

        service = Service(
            publisher_id=publisher_user.user_id,
            service_name='待审服务',
            price=100.00,
            status='pending',
        )
        db.session.add(service)
        db.session.commit()

        resp = client.put(
            f'/api/admin/services/{service.service_id}/status',
            json={'status': 'online'},
            headers=admin_user_auth,
        )
        assert resp.status_code == 200

    def test_admin_audit_invalid_status(self, client, admin_user_auth, test_pet):
        resp = client.put(
            f'/api/admin/pets/{test_pet.pet_id}/status',
            json={'status': 'invalid_status'},
            headers=admin_user_auth,
        )
        assert resp.status_code == 400


class TestAdminStatistics:
    """TC-019: 查看统计数据"""

    def test_get_statistics(self, client, admin_user_auth):
        resp = client.get('/api/admin/stats', headers=admin_user_auth)
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'users' in data
        assert 'pets' in data
        assert 'products' in data
        assert 'services' in data
        assert 'orders' in data
        assert 'adoptions' in data
        assert 'bookings' in data

    def test_get_statistics_with_date_range(self, client, admin_user_auth):
        resp = client.get(
            '/api/admin/stats?start_date=2025-01-01&end_date=2025-12-31',
            headers=admin_user_auth,
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['date_range']['start_date'] == '2025-01-01'

    def test_get_statistics_invalid_date(self, client, admin_user_auth):
        resp = client.get(
            '/api/admin/stats?start_date=invalid',
            headers=admin_user_auth,
        )
        assert resp.status_code == 400

    def test_get_statistics_unauthorized(self, client, normal_user_auth):
        resp = client.get('/api/admin/stats', headers=normal_user_auth)
        assert resp.status_code == 403


class TestAdminOperationLogs:
    """TC-020: 操作日志记录"""

    def test_operation_log_created_on_audit(self, client, admin_user_auth, test_pet):
        resp = client.put(
            f'/api/admin/pets/{test_pet.pet_id}/status',
            json={'status': 'online'},
            headers=admin_user_auth,
        )
        assert resp.status_code == 200

        resp2 = client.get('/api/admin/logs', headers=admin_user_auth)
        assert resp2.status_code == 200
        data = resp2.get_json()
        assert data['total'] >= 1
        logs = data['items']
        recent_log = logs[0]
        assert 'action' in recent_log
        assert 'created_at' in recent_log

    def test_list_logs_pagination(self, client, admin_user_auth):
        resp = client.get(
            '/api/admin/logs?page=1&per_page=10',
            headers=admin_user_auth,
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'items' in data
        assert 'total' in data

    def test_list_logs_unauthorized(self, client, normal_user_auth):
        resp = client.get('/api/admin/logs', headers=normal_user_auth)
        assert resp.status_code == 403


class TestAdminAPIs:
    """管理员其他监管接口"""

    def test_admin_list_orders(self, client, admin_user_auth):
        resp = client.get('/api/admin/orders', headers=admin_user_auth)
        assert resp.status_code == 200

    def test_admin_list_bookings(self, client, admin_user_auth):
        resp = client.get('/api/admin/bookings', headers=admin_user_auth)
        assert resp.status_code == 200

    def test_admin_list_adoptions(self, client, admin_user_auth):
        resp = client.get('/api/admin/adoptions', headers=admin_user_auth)
        assert resp.status_code == 200

    def test_admin_list_products(self, client, admin_user_auth):
        resp = client.get('/api/admin/products', headers=admin_user_auth)
        assert resp.status_code == 200

    def test_admin_list_services(self, client, admin_user_auth):
        resp = client.get('/api/admin/services', headers=admin_user_auth)
        assert resp.status_code == 200

    def test_admin_list_complaints(self, client, admin_user_auth):
        resp = client.get('/api/admin/complaints', headers=admin_user_auth)
        assert resp.status_code == 200

    def test_admin_handle_complaint(self, client, admin_user_auth, app, normal_user):
        from app.extensions import db
        from app.models import Complaint

        complaint = Complaint(
            user_id=normal_user.user_id,
            target_type='order',
            target_id=1,
            content='商品有质量问题',
            status='pending',
        )
        db.session.add(complaint)
        db.session.commit()

        resp = client.put(
            f'/api/admin/complaints/{complaint.complaint_id}/handle',
            json={'status': 'resolved', 'admin_reply': '已为您处理'},
            headers=admin_user_auth,
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['complaint']['status'] == 'resolved'
        assert data['complaint']['admin_reply'] == '已为您处理'
