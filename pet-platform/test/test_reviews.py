"""TC-016 用户提交评价"""

import pytest


class TestSubmitReview:
    """TC-016: 用户提交评价"""

    def test_submit_review_success(self, client, normal_user_auth, test_order):
        resp = client.post('/api/reviews', json={
            'target_type': 'order',
            'target_id': test_order.order_id,
            'rating': 4,
            'content': '商品质量很好',
        }, headers=normal_user_auth)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['message'] == '评价成功'
        review = data['review']
        assert review['rating'] == 4
        assert review['content'] == '商品质量很好'
        assert review['target_type'] == 'order'

    def test_submit_duplicate_review(self, client, normal_user_auth, test_order):
        """防止重复评价"""
        payload = {
            'target_type': 'order',
            'target_id': test_order.order_id,
            'rating': 4,
            'content': '第一次评价',
        }
        r1 = client.post('/api/reviews', json=payload, headers=normal_user_auth)
        assert r1.status_code == 201

        r2 = client.post('/api/reviews', json={
            'target_type': 'order',
            'target_id': test_order.order_id,
            'rating': 3,
            'content': '重复评价',
        }, headers=normal_user_auth)
        assert r2.status_code == 409
        assert '已评价' in r2.get_json()['error']

    def test_submit_review_invalid_rating(self, client, normal_user_auth, test_order):
        resp = client.post('/api/reviews', json={
            'target_type': 'order',
            'target_id': test_order.order_id,
            'rating': 6,
            'content': '评分超范围',
        }, headers=normal_user_auth)
        assert resp.status_code == 400

    def test_submit_review_invalid_target_type(self, client, normal_user_auth):
        resp = client.post('/api/reviews', json={
            'target_type': 'invalid_type',
            'target_id': 1,
            'rating': 4,
            'content': '无效目标类型',
        }, headers=normal_user_auth)
        assert resp.status_code == 400

    def test_list_reviews(self, client, test_order):
        resp = client.get(
            f'/api/reviews?target_type=order&target_id={test_order.order_id}'
        )
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)
