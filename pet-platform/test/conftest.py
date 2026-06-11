import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'
    JWT_SECRET_KEY = 'test-jwt-secret-key'
    JWT_IDENTITY_CLAIM = 'uid'
    JWT_ACCESS_TOKEN_EXPIRES = 86400
    UPLOAD_FOLDER = '/tmp/test-uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024


@pytest.fixture
def app():
    _app = create_app('default')
    _app.config.from_object(TestConfig)
    with _app.app_context():
        db.create_all()
        yield _app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# ---- Helpers ----

def auth_header(token):
    return {'Authorization': f'Bearer {token}'}


# ---- User fixtures ----

@pytest.fixture
def normal_user(app):
    from app.models import User
    user = User(
        username='normaluser',
        password_hash=generate_password_hash('123456'),
        nickname='normaluser',
        role_type='user',
        status='active',
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def normal_user_token(client, normal_user):
    resp = client.post('/api/auth/login', json={
        'username': 'normaluser',
        'password': '123456',
    })
    assert resp.status_code == 200
    return resp.get_json()['token']


@pytest.fixture
def normal_user_auth(normal_user_token):
    return auth_header(normal_user_token)


@pytest.fixture
def publisher_user(app):
    from app.models import User
    user = User(
        username='publisher1',
        password_hash=generate_password_hash('123456'),
        nickname='publisher1',
        role_type='publisher',
        status='active',
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def publisher_user_token(client, publisher_user):
    resp = client.post('/api/auth/login', json={
        'username': 'publisher1',
        'password': '123456',
    })
    assert resp.status_code == 200
    return resp.get_json()['token']


@pytest.fixture
def publisher_user_auth(publisher_user_token):
    return auth_header(publisher_user_token)


@pytest.fixture
def admin_user(app):
    from app.models import User
    user = User(
        username='admin1',
        password_hash=generate_password_hash('123456'),
        nickname='admin1',
        role_type='admin',
        status='active',
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def admin_user_token(client, admin_user):
    resp = client.post('/api/auth/login', json={
        'username': 'admin1',
        'password': '123456',
    })
    assert resp.status_code == 200
    return resp.get_json()['token']


@pytest.fixture
def admin_user_auth(admin_user_token):
    return auth_header(admin_user_token)


# ---- Test data fixtures ----

@pytest.fixture
def test_pet(app, publisher_user):
    from app.models import Pet
    pet = Pet(
        publisher_id=publisher_user.user_id,
        pet_name='旺财',
        species='犬',
        breed='中华田园犬',
        age_desc='1岁',
        gender='male',
        health_status='健康',
        adoption_requirements='需要稳定住所',
        location='天津',
        description='可爱狗狗',
        cover_image='/static/uploads/pets/test.jpg',
        status='online',
    )
    db.session.add(pet)
    db.session.commit()
    return pet


@pytest.fixture
def test_product(app, publisher_user):
    from app.models import Product
    product = Product(
        publisher_id=publisher_user.user_id,
        product_name='高级狗粮',
        category='宠物食品',
        description='优质狗粮',
        cover_image='/static/uploads/products/dog_food.jpg',
        price=99.00,
        stock=100,
        status='online',
    )
    db.session.add(product)
    db.session.commit()
    return product


@pytest.fixture
def test_product_low_stock(app, publisher_user):
    from app.models import Product
    product = Product(
        publisher_id=publisher_user.user_id,
        product_name='限量猫粮',
        category='宠物食品',
        description='限量猫粮',
        cover_image='/static/uploads/products/cat_food.jpg',
        price=50.00,
        stock=3,
        status='online',
    )
    db.session.add(product)
    db.session.commit()
    return product


@pytest.fixture
def test_service(app, publisher_user):
    from app.models import Service, ServiceSlot
    service = Service(
        publisher_id=publisher_user.user_id,
        service_name='宠物洗护',
        category='美容护理',
        description='专业洗护',
        price=80.00,
        duration='1小时',
        location='天津',
        status='online',
    )
    db.session.add(service)
    db.session.flush()

    slot = ServiceSlot(
        service_id=service.service_id,
        slot_date='2025-06-10',
        slot_time='09:00-10:00',
        capacity=5,
        booked_count=0,
    )
    db.session.add(slot)
    db.session.flush()
    service._test_slot = slot
    db.session.commit()
    return service


@pytest.fixture
def test_slot_full(app, publisher_user):
    from app.models import Service, ServiceSlot
    service = Service(
        publisher_id=publisher_user.user_id,
        service_name='宠物寄养',
        category='寄养服务',
        description='专业寄养',
        price=120.00,
        duration='全天',
        location='天津',
        status='online',
    )
    db.session.add(service)
    db.session.flush()

    slot = ServiceSlot(
        service_id=service.service_id,
        slot_date='2025-06-11',
        slot_time='10:00-11:00',
        capacity=1,
        booked_count=1,
    )
    db.session.add(slot)
    db.session.flush()
    service._test_slot = slot
    db.session.commit()
    return service


@pytest.fixture
def test_address(app, normal_user):
    from app.models import UserAddress
    addr = UserAddress(
        user_id=normal_user.user_id,
        receiver_name='张三',
        phone='13800000000',
        province='天津',
        city='天津',
        district='南开区',
        detail='卫津路94号',
        is_default=True,
    )
    db.session.add(addr)
    db.session.commit()
    return addr


@pytest.fixture
def test_order(app, normal_user, test_product, test_address):
    from app.models import Order, OrderItem
    order = Order(
        order_no='PO_TEST_001',
        buyer_id=normal_user.user_id,
        total_amount=198.00,
        address_snapshot='{}',
        pay_status='paid',
        delivery_status='delivered',
        receive_status='received',
    )
    db.session.add(order)
    db.session.flush()

    item = OrderItem(
        order_id=order.order_id,
        product_id=test_product.product_id,
        product_name=test_product.product_name,
        price=99.00,
        quantity=2,
        image_url=test_product.cover_image,
    )
    db.session.add(item)
    db.session.commit()
    return order
