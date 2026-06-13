"""TC-004 宠物列表查询 / TC-005 宠物条件筛选"""


class TestPetList:
    """TC-004: 宠物列表查询"""

    def test_list_pets_empty(self, client):
        resp = client.get('/api/pets')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'items' in data
        assert 'total' in data

    def test_list_pets_with_data(self, client, test_pet):
        resp = client.get('/api/pets')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['total'] >= 1
        items = data['items']
        assert any(p['pet_name'] == '旺财' for p in items)

    def test_list_pets_pagination(self, client, test_pet):
        resp = client.get('/api/pets?page=1&per_page=12')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'page' in data
        assert 'pages' in data

    def test_list_pets_returns_online_only(self, client, app, publisher_user_auth):
        """线下宠物不应出现在列表里"""
        client.post('/api/auth/register', json={
            'username': 'pub2',
            'password': '123456',
            'role_type': 'publisher',
        })
        # 创建 pending 状态的宠物不应返回
        resp = client.get('/api/pets')
        data = resp.get_json()
        for item in data['items']:
            assert item.get('status') != 'pending'


class TestPetFilter:
    """TC-005: 宠物条件筛选"""

    def test_filter_by_breed(self, client, test_pet):
        resp = client.get('/api/pets?breed=中华田园犬')
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['items']) >= 1
        for p in data['items']:
            assert '中华田园犬' in p['breed']

    def test_filter_by_gender(self, client, test_pet):
        resp = client.get('/api/pets?gender=male')
        assert resp.status_code == 200
        data = resp.get_json()
        for p in data['items']:
            assert p['gender'] == 'male'

    def test_filter_by_location(self, client, test_pet):
        resp = client.get('/api/pets?location=天津')
        assert resp.status_code == 200
        data = resp.get_json()
        for p in data['items']:
            assert '天津' in p['location']

    def test_filter_by_species(self, client, test_pet):
        resp = client.get('/api/pets?species=犬')
        assert resp.status_code == 200
        data = resp.get_json()
        for p in data['items']:
            assert p['species'] == '犬'

    def test_filter_by_keyword(self, client, test_pet):
        resp = client.get('/api/pets?keyword=旺财')
        assert resp.status_code == 200
        data = resp.get_json()
        assert any('旺财' in p.get('pet_name', '') for p in data['items'])

    def test_filter_no_results(self, client, test_pet):
        resp = client.get('/api/pets?breed=不存在品种')
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['items']) == 0


class TestPetDetail:
    """宠物详情查询"""

    def test_get_pet_detail(self, client, test_pet):
        resp = client.get(f'/api/pets/{test_pet.pet_id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['pet_name'] == '旺财'
        assert data['species'] == '犬'

    def test_get_pet_not_found(self, client):
        resp = client.get('/api/pets/99999')
        assert resp.status_code == 404

    def test_get_pet_increments_view_count(self, client, test_pet, app):
        from app.extensions import db
        from app.models import Pet

        before = test_pet.view_count
        client.get(f'/api/pets/{test_pet.pet_id}')

        with app.app_context():
            pet = db.session.get(Pet, test_pet.pet_id)
            assert pet.view_count == before + 1
