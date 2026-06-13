"""TC-010 提交订单 / TC-011 库存不足下单失败 / TC-012 模拟支付成功"""

import pytest


class TestCreateOrder:
    """TC-010: 提交订单"""

    def test_create_order_success(self, client, normal_user_auth, test_product, test_address):
        resp = client.post('/api/orders', json={
            'items': [{'product_id': test_product.product_id, 'quantity': 2}],
            'address_id': test_address.address_id,
            'remark': '请尽快发货',
        }, headers=normal_user_auth)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['message'] == '订单创建成功'
        order = data['order']
        assert order['pay_status'] == 'pending'
        assert len(order['items']) == 1

    def test_create_order_deducts_stock(self, client, normal_user_auth, test_product, test_address, app):
        from app.extensions import db
        from app.models import Product

        before_stock = test_product.stock
        client.post('/api/orders', json={
            'items': [{'product_id': test_product.product_id, 'quantity': 3}],
            'address_id': test_address.address_id,
        }, headers=normal_user_auth)

        with app.app_context():
            product = db.session.get(Product, test_product.product_id)
            assert product.stock == before_stock - 3

    def test_create_order_missing_address(self, client, normal_user_auth, test_product):
        resp = client.post('/api/orders', json={
            'items': [{'product_id': test_product.product_id, 'quantity': 1}],
        }, headers=normal_user_auth)
        assert resp.status_code == 400

    def test_create_order_empty_items(self, client, normal_user_auth, test_address):
        resp = client.post('/api/orders', json={
            'items': [],
            'address_id': test_address.address_id,
        }, headers=normal_user_auth)
        assert resp.status_code == 400

    def test_create_order_from_cart(self, client, normal_user_auth, test_product, test_address):
        """从购物车下单"""
        add_resp = client.post('/api/cart', json={
            'product_id': test_product.product_id,
            'quantity': 2,
        }, headers=normal_user_auth)
        cart_id = add_resp.get_json()['cart_item']['cart_id']

        resp = client.post('/api/orders', json={
            'cart_ids': [cart_id],
            'address_id': test_address.address_id,
        }, headers=normal_user_auth)
        assert resp.status_code == 201
        order = resp.get_json()['order']
        assert order['pay_status'] == 'pending'


class TestOrderInsufficientStock:
    """TC-011: 库存不足下单失败"""

    def test_create_order_insufficient_stock(self, client, normal_user_auth, test_product_low_stock, test_address):
        resp = client.post('/api/orders', json={
            'items': [{'product_id': test_product_low_stock.product_id, 'quantity': 5}],
            'address_id': test_address.address_id,
        }, headers=normal_user_auth)
        assert resp.status_code == 400
        data = resp.get_json()
        assert '库存不足' in data['error']

    def test_create_order_no_overselling(self, client, normal_user_auth, test_product_low_stock, test_address, app):
        """确认不会超卖：库存为3，下单5件被拦截"""
        from app.extensions import db
        from app.models import Product

        resp = client.post('/api/orders', json={
            'items': [{'product_id': test_product_low_stock.product_id, 'quantity': 5}],
            'address_id': test_address.address_id,
        }, headers=normal_user_auth)
        assert resp.status_code == 400

        with app.app_context():
            product = db.session.get(Product, test_product_low_stock.product_id)
            assert product.stock == 3


class TestOrderPay:
    """TC-012: 模拟支付成功"""

    @pytest.fixture
    def pending_order(self, app, normal_user, test_product, test_address):
        from app.extensions import db
        from app.models import Order

        order = Order(
            order_no='PO_TEST_PAY_001',
            buyer_id=normal_user.user_id,
            total_amount=99.00,
            address_snapshot='{}',
            pay_status='pending',
        )
        db.session.add(order)
        db.session.commit()
        return order

    def test_pay_order_success(self, client, normal_user_auth, pending_order):
        resp = client.put(
            f'/api/orders/{pending_order.order_id}/pay',
            headers=normal_user_auth,
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['message'] == '支付成功'
        assert data['order']['pay_status'] == 'paid'

    def test_pay_order_sets_paid_at(self, client, normal_user_auth, pending_order, app):
        resp = client.put(
            f'/api/orders/{pending_order.order_id}/pay',
            headers=normal_user_auth,
        )
        assert resp.status_code == 200
        order_data = resp.get_json()['order']
        assert order_data['paid_at'] is not None

    def test_pay_order_already_paid(self, client, normal_user_auth, pending_order):
        client.put(
            f'/api/orders/{pending_order.order_id}/pay',
            headers=normal_user_auth,
        )
        resp = client.put(
            f'/api/orders/{pending_order.order_id}/pay',
            headers=normal_user_auth,
        )
        assert resp.status_code == 400

    def test_pay_order_not_owner(self, client, publisher_user_auth, pending_order):
        resp = client.put(
            f'/api/orders/{pending_order.order_id}/pay',
            headers=publisher_user_auth,
        )
        assert resp.status_code == 403

    def test_my_orders(self, client, normal_user_auth):
        resp = client.get('/api/orders', headers=normal_user_auth)
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'items' in data

    def test_get_order_detail(self, client, normal_user_auth, pending_order):
        resp = client.get(
            f'/api/orders/{pending_order.order_id}',
            headers=normal_user_auth,
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['order_no'] == 'PO_TEST_PAY_001'
