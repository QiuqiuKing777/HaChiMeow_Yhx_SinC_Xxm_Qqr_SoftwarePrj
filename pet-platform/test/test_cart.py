"""TC-009 商品加入购物车"""


class TestCartAdd:
    """TC-009: 商品加入购物车"""

    def test_add_to_cart_success(self, client, normal_user_auth, test_product):
        resp = client.post('/api/cart', json={
            'product_id': test_product.product_id,
            'quantity': 2,
        }, headers=normal_user_auth)
        assert resp.status_code == 201
        data = resp.get_json()
        assert '加入购物车' in data['message']
        item = data['cart_item']
        assert item['quantity'] == 2
        assert item['product_id'] == test_product.product_id

    def test_add_to_cart_multiple_times(self, client, normal_user_auth, test_product):
        """多次加入同一商品，数量累加"""
        client.post('/api/cart', json={
            'product_id': test_product.product_id,
            'quantity': 1,
        }, headers=normal_user_auth)
        resp = client.post('/api/cart', json={
            'product_id': test_product.product_id,
            'quantity': 2,
        }, headers=normal_user_auth)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['message'] == '数量已更新'
        assert data['cart_item']['quantity'] == 3

    def test_add_to_cart_exceeds_stock(self, client, normal_user_auth, test_product_low_stock):
        resp = client.post('/api/cart', json={
            'product_id': test_product_low_stock.product_id,
            'quantity': 10,
        }, headers=normal_user_auth)
        assert resp.status_code == 400
        data = resp.get_json()
        assert '库存' in data['error']

    def test_add_to_cart_offline_product(self, client, normal_user_auth, app, publisher_user):
        from app.extensions import db
        from app.models import Product

        product = Product(
            publisher_id=publisher_user.user_id,
            product_name='下架商品',
            price=10.00,
            stock=10,
            status='offline',
        )
        db.session.add(product)
        db.session.commit()

        resp = client.post('/api/cart', json={
            'product_id': product.product_id,
            'quantity': 1,
        }, headers=normal_user_auth)
        assert resp.status_code == 400

    def test_view_cart(self, client, normal_user_auth):
        resp = client.get('/api/cart', headers=normal_user_auth)
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_update_cart_quantity(self, client, normal_user_auth, test_product):
        """修改购物车商品数量"""
        r = client.post('/api/cart', json={
            'product_id': test_product.product_id,
            'quantity': 1,
        }, headers=normal_user_auth)
        cart_id = r.get_json()['cart_item']['cart_id']

        resp = client.put(f'/api/cart/{cart_id}', json={
            'quantity': 5,
        }, headers=normal_user_auth)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['cart_item']['quantity'] == 5

    def test_remove_cart_item(self, client, normal_user_auth, test_product):
        """删除购物车项"""
        r = client.post('/api/cart', json={
            'product_id': test_product.product_id,
            'quantity': 1,
        }, headers=normal_user_auth)
        cart_id = r.get_json()['cart_item']['cart_id']

        resp = client.delete(f'/api/cart/{cart_id}', headers=normal_user_auth)
        assert resp.status_code == 200

    def test_clear_cart(self, client, normal_user_auth, test_product):
        """清空购物车"""
        client.post('/api/cart', json={
            'product_id': test_product.product_id,
            'quantity': 1,
        }, headers=normal_user_auth)

        resp = client.delete('/api/cart/clear', headers=normal_user_auth)
        assert resp.status_code == 200

        cart = client.get('/api/cart', headers=normal_user_auth)
        assert len(cart.get_json()) == 0
