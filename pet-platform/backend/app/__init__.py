from flask import Flask
from .config import config
from .extensions import db, jwt, cors


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # 注册蓝图
    from .api import register_blueprints
    register_blueprints(app)

    return app
