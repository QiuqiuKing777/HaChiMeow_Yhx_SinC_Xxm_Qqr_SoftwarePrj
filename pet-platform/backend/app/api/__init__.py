from flask import Blueprint

from .auth import auth_bp
from .pets import pets_bp
from .adoptions import adoptions_bp
from .products import products_bp
from .cart import cart_bp
from .orders import orders_bp
from .services import services_bp
from .bookings import bookings_bp
from .user import user_bp
from .admin import admin_bp
from .reviews import reviews_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(pets_bp)
    app.register_blueprint(adoptions_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(reviews_bp)
