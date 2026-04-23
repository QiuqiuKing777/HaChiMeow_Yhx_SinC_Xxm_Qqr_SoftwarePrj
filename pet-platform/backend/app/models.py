from datetime import datetime
from .extensions import db


# ----------------------------------------------------------------
# 用户表
# ----------------------------------------------------------------
class User(db.Model):
    __tablename__ = 'users'

    user_id       = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username      = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nickname      = db.Column(db.String(50))
    phone         = db.Column(db.String(20))
    email         = db.Column(db.String(100))
    avatar        = db.Column(db.String(255))
    role_type     = db.Column(db.Enum('user', 'publisher', 'admin'), nullable=False, default='user')
    status        = db.Column(db.Enum('active', 'disabled'), nullable=False, default='active')
    created_at    = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'user_id':    self.user_id,
            'username':   self.username,
            'nickname':   self.nickname,
            'phone':      self.phone,
            'email':      self.email,
            'avatar':     self.avatar,
            'role_type':  self.role_type,
            'status':     self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def to_public_dict(self):
        return {
            'user_id':  self.user_id,
            'username': self.username,
            'nickname': self.nickname,
            'avatar':   self.avatar,
            'role_type': self.role_type,
        }


# ----------------------------------------------------------------
# 宠物表
# ----------------------------------------------------------------
class Pet(db.Model):
    __tablename__ = 'pets'

    pet_id               = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    publisher_id         = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    pet_name             = db.Column(db.String(50), nullable=False)
    species              = db.Column(db.String(30), nullable=False)
    breed                = db.Column(db.String(50))
    age_desc             = db.Column(db.String(50))
    gender               = db.Column(db.Enum('male', 'female', 'unknown'), default='unknown')
    health_status        = db.Column(db.String(200))
    adoption_requirements = db.Column(db.Text)
    location             = db.Column(db.String(100))
    description          = db.Column(db.Text)
    cover_image          = db.Column(db.String(255))
    view_count           = db.Column(db.Integer, default=0)
    status               = db.Column(db.Enum('pending', 'online', 'adopted', 'offline'), default='pending')
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at           = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    publisher = db.relationship('User', backref='pets', foreign_keys=[publisher_id])
    images    = db.relationship('PetImage', backref='pet', cascade='all, delete-orphan')

    def to_dict(self, include_publisher=True):
        d = {
            'pet_id':                self.pet_id,
            'publisher_id':          self.publisher_id,
            'pet_name':              self.pet_name,
            'species':               self.species,
            'breed':                 self.breed,
            'age_desc':              self.age_desc,
            'gender':                self.gender,
            'health_status':         self.health_status,
            'adoption_requirements': self.adoption_requirements,
            'location':              self.location,
            'description':           self.description,
            'cover_image':           self.cover_image,
            'view_count':            self.view_count,
            'status':                self.status,
            'images':                [img.to_dict() for img in self.images],
            'created_at':            self.created_at.isoformat() if self.created_at else None,
        }
        if include_publisher and self.publisher:
            d['publisher'] = self.publisher.to_public_dict()
        return d


class PetImage(db.Model):
    __tablename__ = 'pet_images'

    image_id   = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    pet_id     = db.Column(db.BigInteger, db.ForeignKey('pets.pet_id'), nullable=False)
    image_url  = db.Column(db.String(255), nullable=False)
    sort_order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {'image_id': self.image_id, 'image_url': self.image_url, 'sort_order': self.sort_order}


# ----------------------------------------------------------------
# 领养申请表
# ----------------------------------------------------------------
class AdoptionApplication(db.Model):
    __tablename__ = 'adoption_applications'

    application_id    = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    pet_id            = db.Column(db.BigInteger, db.ForeignKey('pets.pet_id'), nullable=False)
    applicant_id      = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    housing_info      = db.Column(db.Text, nullable=False)
    pet_experience    = db.Column(db.Text)
    family_attitude   = db.Column(db.Text)
    promise_statement = db.Column(db.Text, nullable=False)
    contact_info      = db.Column(db.String(100))
    review_status     = db.Column(db.Enum('pending', 'approved', 'rejected', 'supplement', 'cancelled'), default='pending')
    review_remark     = db.Column(db.Text)
    reviewed_by       = db.Column(db.BigInteger, db.ForeignKey('users.user_id'))
    reviewed_at       = db.Column(db.DateTime)
    submitted_at      = db.Column(db.DateTime, default=datetime.utcnow)

    pet      = db.relationship('Pet', backref='applications')
    applicant = db.relationship('User', foreign_keys=[applicant_id])
    reviewer  = db.relationship('User', foreign_keys=[reviewed_by])

    def to_dict(self):
        return {
            'application_id':    self.application_id,
            'pet_id':            self.pet_id,
            'pet':               {'pet_name': self.pet.pet_name, 'cover_image': self.pet.cover_image,
                                  'species': self.pet.species} if self.pet else None,
            'applicant_id':      self.applicant_id,
            'applicant':         self.applicant.to_public_dict() if self.applicant else None,
            'housing_info':      self.housing_info,
            'pet_experience':    self.pet_experience,
            'family_attitude':   self.family_attitude,
            'promise_statement': self.promise_statement,
            'contact_info':      self.contact_info,
            'review_status':     self.review_status,
            'review_remark':     self.review_remark,
            'reviewed_by':       self.reviewed_by,
            'reviewed_at':       self.reviewed_at.isoformat() if self.reviewed_at else None,
            'submitted_at':      self.submitted_at.isoformat() if self.submitted_at else None,
        }


# ----------------------------------------------------------------
# 商品表
# ----------------------------------------------------------------
class Product(db.Model):
    __tablename__ = 'products'

    product_id   = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    publisher_id = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    category     = db.Column(db.String(50))
    description  = db.Column(db.Text)
    cover_image  = db.Column(db.String(255))
    price        = db.Column(db.Numeric(10, 2), nullable=False)
    stock        = db.Column(db.Integer, default=0)
    sales_count  = db.Column(db.Integer, default=0)
    status       = db.Column(db.Enum('pending', 'online', 'offline'), default='pending')
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    publisher = db.relationship('User', backref='products')
    images    = db.relationship('ProductImage', backref='product', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'product_id':   self.product_id,
            'publisher_id': self.publisher_id,
            'product_name': self.product_name,
            'category':     self.category,
            'description':  self.description,
            'cover_image':  self.cover_image,
            'price':        float(self.price),
            'stock':        self.stock,
            'sales_count':  self.sales_count,
            'status':       self.status,
            'images':       [img.to_dict() for img in self.images],
            'created_at':   self.created_at.isoformat() if self.created_at else None,
        }


class ProductImage(db.Model):
    __tablename__ = 'product_images'

    image_id   = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    product_id = db.Column(db.BigInteger, db.ForeignKey('products.product_id'), nullable=False)
    image_url  = db.Column(db.String(255), nullable=False)
    sort_order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {'image_id': self.image_id, 'image_url': self.image_url, 'sort_order': self.sort_order}


# ----------------------------------------------------------------
# 购物车表
# ----------------------------------------------------------------
class CartItem(db.Model):
    __tablename__ = 'cart_items'

    cart_id    = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id    = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    product_id = db.Column(db.BigInteger, db.ForeignKey('products.product_id'), nullable=False)
    quantity   = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product')

    def to_dict(self):
        return {
            'cart_id':    self.cart_id,
            'product_id': self.product_id,
            'product':    self.product.to_dict() if self.product else None,
            'quantity':   self.quantity,
        }


# ----------------------------------------------------------------
# 收货地址表
# ----------------------------------------------------------------
class UserAddress(db.Model):
    __tablename__ = 'user_addresses'

    address_id    = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id       = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    receiver_name = db.Column(db.String(50), nullable=False)
    phone         = db.Column(db.String(20), nullable=False)
    province      = db.Column(db.String(50))
    city          = db.Column(db.String(50))
    district      = db.Column(db.String(50))
    detail        = db.Column(db.String(200), nullable=False)
    is_default    = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'address_id':    self.address_id,
            'receiver_name': self.receiver_name,
            'phone':         self.phone,
            'province':      self.province,
            'city':          self.city,
            'district':      self.district,
            'detail':        self.detail,
            'is_default':    self.is_default,
            'full_address':  f"{self.province or ''}{self.city or ''}{self.district or ''}{self.detail}",
        }


# ----------------------------------------------------------------
# 订单表
# ----------------------------------------------------------------
class Order(db.Model):
    __tablename__ = 'orders'

    order_id         = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    order_no         = db.Column(db.String(30), unique=True, nullable=False)
    buyer_id         = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    total_amount     = db.Column(db.Numeric(10, 2), nullable=False)
    pay_status       = db.Column(db.Enum('pending', 'paid', 'refunded', 'cancelled'), default='pending')
    delivery_status  = db.Column(db.Enum('pending', 'shipped', 'delivered'), default='pending')
    receive_status   = db.Column(db.Enum('pending', 'received'), default='pending')
    address_snapshot = db.Column(db.Text, nullable=False)
    remark           = db.Column(db.Text)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at          = db.Column(db.DateTime)

    buyer = db.relationship('User')
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'order_id':        self.order_id,
            'order_no':        self.order_no,
            'buyer_id':        self.buyer_id,
            'total_amount':    float(self.total_amount),
            'pay_status':      self.pay_status,
            'delivery_status': self.delivery_status,
            'receive_status':  self.receive_status,
            'address_snapshot': self.address_snapshot,
            'remark':          self.remark,
            'items':           [item.to_dict() for item in self.items],
            'created_at':      self.created_at.isoformat() if self.created_at else None,
            'paid_at':         self.paid_at.isoformat() if self.paid_at else None,
        }


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    item_id      = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    order_id     = db.Column(db.BigInteger, db.ForeignKey('orders.order_id'), nullable=False)
    product_id   = db.Column(db.BigInteger, db.ForeignKey('products.product_id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    price        = db.Column(db.Numeric(10, 2), nullable=False)
    quantity     = db.Column(db.Integer, nullable=False)
    image_url    = db.Column(db.String(255))

    def to_dict(self):
        return {
            'item_id':      self.item_id,
            'product_id':   self.product_id,
            'product_name': self.product_name,
            'price':        float(self.price),
            'quantity':     self.quantity,
            'image_url':    self.image_url,
        }


# ----------------------------------------------------------------
# 服务项目表
# ----------------------------------------------------------------
class Service(db.Model):
    __tablename__ = 'services'

    service_id   = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    publisher_id = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    service_name = db.Column(db.String(100), nullable=False)
    category     = db.Column(db.String(50))
    description  = db.Column(db.Text)
    price        = db.Column(db.Numeric(10, 2), nullable=False)
    cover_image  = db.Column(db.String(255))
    duration     = db.Column(db.String(50))
    location     = db.Column(db.String(100))
    status       = db.Column(db.Enum('pending', 'online', 'offline'), default='pending')
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    publisher = db.relationship('User', backref='services')
    slots     = db.relationship('ServiceSlot', backref='service', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'service_id':   self.service_id,
            'publisher_id': self.publisher_id,
            'publisher':    self.publisher.to_public_dict() if self.publisher else None,
            'service_name': self.service_name,
            'category':     self.category,
            'description':  self.description,
            'price':        float(self.price),
            'cover_image':  self.cover_image,
            'duration':     self.duration,
            'location':     self.location,
            'status':       self.status,
            'created_at':   self.created_at.isoformat() if self.created_at else None,
        }


class ServiceSlot(db.Model):
    __tablename__ = 'service_slots'

    slot_id      = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    service_id   = db.Column(db.BigInteger, db.ForeignKey('services.service_id'), nullable=False)
    slot_date    = db.Column(db.Date, nullable=False)
    slot_time    = db.Column(db.String(30), nullable=False)
    capacity     = db.Column(db.Integer, default=5)
    booked_count = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'slot_id':      self.slot_id,
            'service_id':   self.service_id,
            'slot_date':    self.slot_date.isoformat() if self.slot_date else None,
            'slot_time':    self.slot_time,
            'capacity':     self.capacity,
            'booked_count': self.booked_count,
            'available':    self.capacity - self.booked_count,
        }


# ----------------------------------------------------------------
# 服务预约表
# ----------------------------------------------------------------
class Booking(db.Model):
    __tablename__ = 'bookings'

    booking_id     = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    service_id     = db.Column(db.BigInteger, db.ForeignKey('services.service_id'), nullable=False)
    user_id        = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    slot_id        = db.Column(db.BigInteger, db.ForeignKey('service_slots.slot_id'), nullable=False)
    pet_name       = db.Column(db.String(50))
    pet_breed      = db.Column(db.String(50))
    booking_status = db.Column(db.Enum('pending', 'confirmed', 'cancelled', 'finished'), default='pending')
    remark         = db.Column(db.Text)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    service = db.relationship('Service')
    user    = db.relationship('User')
    slot    = db.relationship('ServiceSlot')

    def to_dict(self):
        return {
            'booking_id':     self.booking_id,
            'service_id':     self.service_id,
            'service':        self.service.to_dict() if self.service else None,
            'user_id':        self.user_id,
            'slot_id':        self.slot_id,
            'slot':           self.slot.to_dict() if self.slot else None,
            'pet_name':       self.pet_name,
            'pet_breed':      self.pet_breed,
            'booking_status': self.booking_status,
            'remark':         self.remark,
            'created_at':     self.created_at.isoformat() if self.created_at else None,
        }


# ----------------------------------------------------------------
# 评价表
# ----------------------------------------------------------------
class Review(db.Model):
    __tablename__ = 'reviews'

    review_id   = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    reviewer_id = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    target_type = db.Column(db.Enum('order', 'booking', 'pet'), nullable=False)
    target_id   = db.Column(db.BigInteger, nullable=False)
    rating      = db.Column(db.Integer, nullable=False)
    content     = db.Column(db.Text)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    reviewer = db.relationship('User')

    def to_dict(self):
        return {
            'review_id':   self.review_id,
            'reviewer_id': self.reviewer_id,
            'reviewer':    self.reviewer.to_public_dict() if self.reviewer else None,
            'target_type': self.target_type,
            'target_id':   self.target_id,
            'rating':      self.rating,
            'content':     self.content,
            'created_at':  self.created_at.isoformat() if self.created_at else None,
        }


# ----------------------------------------------------------------
# 消息通知表
# ----------------------------------------------------------------
class Notification(db.Model):
    __tablename__ = 'notifications'

    notification_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id         = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    type            = db.Column(db.String(50), nullable=False)
    title           = db.Column(db.String(100), nullable=False)
    content         = db.Column(db.Text)
    is_read         = db.Column(db.Boolean, default=False)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'notification_id': self.notification_id,
            'type':      self.type,
            'title':     self.title,
            'content':   self.content,
            'is_read':   self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ----------------------------------------------------------------
# 收藏表
# ----------------------------------------------------------------
class Favorite(db.Model):
    __tablename__ = 'favorites'

    favorite_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id     = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    target_type = db.Column(db.Enum('pet', 'product', 'service'), nullable=False)
    target_id   = db.Column(db.BigInteger, nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        target = None
        model_map = {
            'pet': Pet,
            'product': Product,
            'service': Service,
        }
        model = model_map.get(self.target_type)
        if model:
            target = db.session.get(model, self.target_id)

        target_name = None
        image_url = None
        if target:
            if self.target_type == 'pet':
                target_name = target.pet_name
            elif self.target_type == 'product':
                target_name = target.product_name
            elif self.target_type == 'service':
                target_name = target.service_name
            image_url = getattr(target, 'cover_image', None)

        return {
            'favorite_id': self.favorite_id,
            'target_type': self.target_type,
            'target_id':   self.target_id,
            'target_name': target_name,
            'image_url':   image_url,
            'created_at':  self.created_at.isoformat() if self.created_at else None,
        }


# ----------------------------------------------------------------
# 站内消息表
# ----------------------------------------------------------------
class Message(db.Model):
    __tablename__ = 'messages'

    message_id  = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    sender_id   = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    receiver_id = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    pet_id      = db.Column(db.BigInteger, db.ForeignKey('pets.pet_id'))
    content     = db.Column(db.Text, nullable=False)
    is_read     = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    sender   = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])

    def to_dict(self):
        return {
            'message_id':  self.message_id,
            'sender_id':   self.sender_id,
            'sender':      self.sender.to_public_dict() if self.sender else None,
            'receiver_id': self.receiver_id,
            'pet_id':      self.pet_id,
            'content':     self.content,
            'is_read':     self.is_read,
            'created_at':  self.created_at.isoformat() if self.created_at else None,
        }


# ----------------------------------------------------------------
# 操作日志表
# ----------------------------------------------------------------
class OperationLog(db.Model):
    __tablename__ = 'operation_logs'

    log_id      = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    operator_id = db.Column(db.BigInteger, db.ForeignKey('users.user_id'), nullable=False)
    action      = db.Column(db.String(100), nullable=False)
    target_type = db.Column(db.String(50))
    target_id   = db.Column(db.BigInteger)
    detail      = db.Column(db.Text)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    operator = db.relationship('User')
