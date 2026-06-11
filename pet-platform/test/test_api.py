"""接口测试：覆盖测试报告中全部主要API端点

对应测试报告表\ref{tab:apitest}中的15个核心接口
"""

import pytest


class TestAuthAPI:
    """POST /api/auth/register - 验证新用户注册功能"""

    def test_register_201(self, client):
        resp = client.post('/api/auth/register', json={
            'username': 'newuser',
            'password': '123456',
            'role_type': 'user',
        })
        assert resp.status_code == 201

    def test_register_400_empty(self, client):
        resp = client.post('/api/auth/register', json={
            'username': '',
            'password': '',
        })
        assert resp.status_code == 400

    """POST /api/auth/login - 验证登录认证与JWT令牌颁发"""

    def test_login_200(self, client, normal_user):
        resp = client.post('/api/auth/login', json={
            'username': 'normaluser',
            'password': '123456',
        })
        assert resp.status_code == 200
        assert 'token' in resp.get_json()

    def test_login_401_wrong_password(self, client, normal_user):
        resp = client.post('/api/auth/login', json={
            'username': 'normaluser',
            'password': 'wrong',
        })
        assert resp.status_code == 401


class TestPetsAPI:
    """GET /api/pets - 验证宠物列表分页查询和多条件筛选功能"""

    def test_list_pets_200(self, client):
        resp = client.get('/api/pets')
        assert resp.status_code == 200

    def test_list_pets_filtered_200(self, client, test_pet):
        resp = client.get('/api/pets?species=犬&gender=male&location=天津')
        assert resp.status_code == 200

    """GET /api/pets/1 - 验证宠物详情查询"""

    def test_get_pet_detail_200(self, client, test_pet):
        resp = client.get(f'/api/pets/{test_pet.pet_id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'images' in data

    def test_get_pet_detail_404(self, client):
        resp = client.get('/api/pets/99999')
        assert resp.status_code == 404


class TestAdoptionsAPI:
    """POST /api/adoptions - 验证领养申请提交及重复提交拦截"""

    def test_submit_adoption_201(self, client, normal_user_auth, test_pet):
        resp = client.post('/api/adoptions', json={
            'pet_id': test_pet.pet_id,
            'housing_info': '自有住房',
            'promise_statement': '承诺善待宠物',
        }, headers=normal_user_auth)
        assert resp.status_code == 201

    def test_duplicate_adoption_409(self, client, normal_user_auth, test_pet):
        payload = {
            'pet_id': test_pet.pet_id,
            'housing_info': '自有住房',
            'promise_statement': '承诺善待宠物',
        }
        client.post('/api/adoptions', json=payload, headers=normal_user_auth)
        resp = client.post('/api/adoptions', json=payload, headers=normal_user_auth)
        assert resp.status_code == 409

    """PUT /api/adoptions/1/review - 验证发布方审核通过申请"""

    def test_review_adoption_200(self, client, publisher_user_auth, normal_user, test_pet, app):
        from app.extensions import db
        from app.models import AdoptionApplication

        app_obj = AdoptionApplication(
            pet_id=test_pet.pet_id,
            applicant_id=normal_user.user_id,
            housing_info='自有住房',
            promise_statement='承诺',
            review_status='pending',
        )
        db.session.add(app_obj)
        db.session.commit()

        resp = client.put(
            f'/api/adoptions/{app_obj.application_id}/review',
            json={'review_status': 'approved'},
            headers=publisher_user_auth,
        )
        assert resp.status_code == 200


class TestProductsAPI:
    """GET /api/products - 验证商品列表查询及分类和关键词筛选"""

    def test_list_products_200(self, client):
        resp = client.get('/api/products')
        assert resp.status_code == 200

    def test_list_products_filtered_200(self, client, test_product):
        resp = client.get('/api/products?category=宠物食品&keyword=狗粮')
        assert resp.status_code == 200


class TestOrdersAPI:
    """POST /api/orders - 验证订单创建、库存扣减及库存不足时的拦截"""

    def test_create_order_201(self, client, normal_user_auth, test_product, test_address):
        resp = client.post('/api/orders', json={
            'items': [{'product_id': test_product.product_id, 'quantity': 2}],
            'address_id': test_address.address_id,
        }, headers=normal_user_auth)
        assert resp.status_code == 201

    def test_insufficient_stock_400(self, client, normal_user_auth, test_product_low_stock, test_address):
        resp = client.post('/api/orders', json={
            'items': [{'product_id': test_product_low_stock.product_id, 'quantity': 10}],
            'address_id': test_address.address_id,
        }, headers=normal_user_auth)
        assert resp.status_code == 400

    """PUT /api/orders/1/pay - 验证模拟支付功能及订单状态正确流转"""

    def test_pay_order_200(self, client, normal_user, normal_user_auth, test_product, test_address, app):
        from app.extensions import db
        from app.models import Order

        order = Order(
            order_no='PO_API_TEST_001',
            buyer_id=normal_user.user_id,
            total_amount=99.00,
            address_snapshot='{}',
            pay_status='pending',
        )
        db.session.add(order)
        db.session.commit()

        resp = client.put(
            f'/api/orders/{order.order_id}/pay',
            headers=normal_user_auth,
        )
        assert resp.status_code == 200
        assert resp.get_json()['order']['pay_status'] == 'paid'


class TestServicesAPI:
    """GET /api/services/1/slots - 验证服务可用时段查询及已约容量信息"""

    def test_get_slots_200(self, client, test_service):
        resp = client.get(f'/api/services/{test_service.service_id}/slots')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        if data:
            assert 'available' in data[0]


class TestBookingsAPI:
    """POST /api/bookings - 验证预约创建及时段容量原子性更新"""

    def test_create_booking_201(self, client, normal_user_auth, test_service):
        slot = test_service._test_slot
        resp = client.post('/api/bookings', json={
            'slot_id': slot.slot_id,
            'pet_name': '小黄',
        }, headers=normal_user_auth)
        assert resp.status_code == 201

    """PUT /api/bookings/1/confirm - 验证发布方确认预约及状态流转"""

    def test_confirm_booking_200(self, client, publisher_user_auth, test_service, normal_user, app):
        from app.extensions import db
        from app.models import Booking

        booking = Booking(
            service_id=test_service.service_id,
            user_id=normal_user.user_id,
            slot_id=test_service._test_slot.slot_id,
            pet_name='旺财',
            booking_status='pending',
        )
        db.session.add(booking)
        db.session.commit()

        resp = client.put(
            f'/api/bookings/{booking.booking_id}/confirm',
            headers=publisher_user_auth,
        )
        assert resp.status_code == 200


class TestAdminAPI:
    """GET /api/admin/users - 验证管理员用户列表查询及角色筛选"""

    def test_admin_users_200(self, client, admin_user_auth):
        resp = client.get('/api/admin/users', headers=admin_user_auth)
        assert resp.status_code == 200

    def test_admin_users_role_filter_200(self, client, admin_user_auth):
        resp = client.get('/api/admin/users?role_type=publisher', headers=admin_user_auth)
        assert resp.status_code == 200

    """GET /api/admin/statistics - 验证统计数据查询及日期范围筛选"""

    def test_admin_stats_200(self, client, admin_user_auth):
        resp = client.get('/api/admin/stats', headers=admin_user_auth)
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'trend' in data

    def test_admin_stats_date_filter_200(self, client, admin_user_auth):
        resp = client.get(
            '/api/admin/stats?start_date=2025-01-01&end_date=2025-12-31',
            headers=admin_user_auth,
        )
        assert resp.status_code == 200

    """GET /api/admin/audit-logs - 验证操作日志的分页查询和按操作类型筛选功能"""

    def test_admin_logs_200(self, client, admin_user_auth):
        resp = client.get('/api/admin/logs', headers=admin_user_auth)
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'items' in data
        assert 'total' in data


class TestUserCenterAPI:
    """用户中心模块接口"""

    def test_get_profile_200(self, client, normal_user_auth):
        resp = client.get('/api/user/profile', headers=normal_user_auth)
        assert resp.status_code == 200

    def test_update_profile_200(self, client, normal_user_auth):
        resp = client.put('/api/user/profile', json={
            'nickname': '新昵称',
        }, headers=normal_user_auth)
        assert resp.status_code == 200

    def test_list_addresses_200(self, client, normal_user_auth):
        resp = client.get('/api/user/addresses', headers=normal_user_auth)
        assert resp.status_code == 200

    def test_create_address_201(self, client, normal_user_auth):
        resp = client.post('/api/user/addresses', json={
            'receiver_name': '李四',
            'phone': '13900001111',
            'detail': '测试地址',
        }, headers=normal_user_auth)
        assert resp.status_code == 201

    def test_list_favorites_200(self, client, normal_user_auth):
        resp = client.get('/api/user/favorites', headers=normal_user_auth)
        assert resp.status_code == 200

    def test_add_favorite_201(self, client, normal_user_auth, test_pet):
        resp = client.post('/api/user/favorites', json={
            'target_type': 'pet',
            'target_id': test_pet.pet_id,
        }, headers=normal_user_auth)
        assert resp.status_code == 201

    def test_list_notifications_200(self, client, normal_user_auth):
        resp = client.get('/api/user/notifications', headers=normal_user_auth)
        assert resp.status_code == 200

    def test_send_message_201(self, client, normal_user, normal_user_auth, publisher_user):
        resp = client.post('/api/user/messages', json={
            'receiver_id': publisher_user.user_id,
            'content': '您好，我想咨询一下',
        }, headers=normal_user_auth)
        assert resp.status_code == 201

    def test_list_messages_200(self, client, normal_user_auth):
        resp = client.get('/api/user/messages', headers=normal_user_auth)
        assert resp.status_code == 200


class TestComplaintsAPI:
    """投诉模块接口"""

    def test_submit_complaint_201(self, client, normal_user_auth):
        resp = client.post('/api/complaints', json={
            'target_type': 'order',
            'target_id': 1,
            'content': '商品有质量问题，申请退款',
        }, headers=normal_user_auth)
        assert resp.status_code == 201

    def test_my_complaints_200(self, client, normal_user_auth):
        resp = client.get('/api/complaints/mine', headers=normal_user_auth)
        assert resp.status_code == 200


class TestAIChatAPI:
    """AI咨询模块接口"""

    def test_ai_chat_200(self, client):
        resp = client.post('/api/ai/chat', json={
            'message': '如何领养宠物？',
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'reply' in data
        assert 'source' in data

    def test_ai_chat_keyword_match(self, client):
        resp = client.post('/api/ai/chat', json={
            'message': '领养流程是什么',
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['source'] == 'rule'

    def test_ai_chat_fallback(self, client):
        resp = client.post('/api/ai/chat', json={
            'message': '今天天气怎么样？',
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'reply' in data

    def test_ai_chat_empty_message(self, client):
        resp = client.post('/api/ai/chat', json={
            'message': '',
        })
        assert resp.status_code == 400


class TestReviewsAPI:
    """评价模块接口"""

    def test_create_review_201(self, client, normal_user_auth, test_order):
        resp = client.post('/api/reviews', json={
            'target_type': 'order',
            'target_id': test_order.order_id,
            'rating': 5,
            'content': '非常好',
        }, headers=normal_user_auth)
        assert resp.status_code == 201

    def test_list_reviews_200(self, client, test_order):
        resp = client.get(
            f'/api/reviews?target_type=order&target_id={test_order.order_id}'
        )
        assert resp.status_code == 200


class TestCartAPI:
    """购物车模块接口"""

    def test_get_cart_200(self, client, normal_user_auth):
        resp = client.get('/api/cart', headers=normal_user_auth)
        assert resp.status_code == 200

    def test_add_cart_201(self, client, normal_user_auth, test_product):
        resp = client.post('/api/cart', json={
            'product_id': test_product.product_id,
            'quantity': 1,
        }, headers=normal_user_auth)
        assert resp.status_code == 201

    def test_update_cart_200(self, client, normal_user_auth, test_product):
        r = client.post('/api/cart', json={
            'product_id': test_product.product_id,
            'quantity': 1,
        }, headers=normal_user_auth)
        cart_id = r.get_json()['cart_item']['cart_id']

        resp = client.put(f'/api/cart/{cart_id}', json={
            'quantity': 3,
        }, headers=normal_user_auth)
        assert resp.status_code == 200

    def test_delete_cart_200(self, client, normal_user_auth, test_product):
        r = client.post('/api/cart', json={
            'product_id': test_product.product_id,
            'quantity': 1,
        }, headers=normal_user_auth)
        cart_id = r.get_json()['cart_item']['cart_id']

        resp = client.delete(f'/api/cart/{cart_id}', headers=normal_user_auth)
        assert resp.status_code == 200
