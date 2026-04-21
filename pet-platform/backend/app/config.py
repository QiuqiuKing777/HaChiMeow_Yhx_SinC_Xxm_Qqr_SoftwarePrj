import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-secret-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:YS2005yzx@localhost/pet_platform?charset=utf8mb4'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'change-this-jwt-secret-in-production')
    JWT_IDENTITY_CLAIM = 'uid'
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24小时

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 最大上传16MB


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
