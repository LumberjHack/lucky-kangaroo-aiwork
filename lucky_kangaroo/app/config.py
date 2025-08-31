import os

class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-fallback-secret')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///instance/lucky_kangaroo.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-fallback-secret')
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    DEBUG = False

class DevelopmentConfig(BaseConfig):
    DEBUG = True

class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(BaseConfig):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
