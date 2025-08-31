import os
from datetime import timedelta
from pathlib import Path

class BaseConfig:
    # Application
    APP_NAME = 'Lucky Kangaroo'
    APP_VERSION = '1.0.0'
    DEBUG = False
    TESTING = False
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'lucky-kangaroo-secret-key-2024')
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT', 'lucky-kangaroo-salt-2024')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql+psycopg://lk:lkpass@localhost:5432/lucky_kangaroo')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 20,
        'max_overflow': 20
    }
    
    # Uploads
    BASE_DIR = Path(os.path.dirname(os.path.dirname(__file__)))
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', str(BASE_DIR / 'uploads'))
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_IMAGE_DIMENSION = 4096  # pixels
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    REDIS_CACHE_DB = int(os.getenv('REDIS_CACHE_DB', '1'))
    REDIS_QUEUE_DB = int(os.getenv('REDIS_QUEUE_DB', '2'))
    REDIS_SOCKETIO_DB = int(os.getenv('REDIS_SOCKETIO_DB', '3'))
    
    # Cache
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'RedisCache')
    CACHE_REDIS_URL = os.getenv('CACHE_REDIS_URL', f"{REDIS_URL}/{REDIS_CACHE_DB}")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', '300'))  # 5 minutes
    
    # Rate Limiting
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '200 per hour')
    RATELIMIT_STORAGE_URI = REDIS_URL
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'lucky-kangaroo-jwt-secret-2024')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600'))  # 1h par défaut
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', '30'))
    )
    JWT_BLACKLIST_ENABLED = os.getenv('JWT_BLACKLIST_ENABLED', 'true').lower() == 'true'
    JWT_BLACKLIST_TOKEN_CHECKS = os.getenv(
        'JWT_BLACKLIST_TOKEN_CHECKS', 'access,refresh'
    ).split(',')
    
    # Email
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@luckykangaroo.com')
    MAIL_DEBUG = os.getenv('MAIL_DEBUG', 'false').lower() == 'true'
    
    # Search
    SEARCH_URL = os.getenv('SEARCH_URL', 'http://localhost:9200')
    SEARCH_INDEX_PREFIX = os.getenv('SEARCH_INDEX_PREFIX', 'luckykangaroo')
    SEARCH_TIMEOUT = int(os.getenv('SEARCH_TIMEOUT', '10'))  # seconds
    
    # OpenAI (AI Features)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_ORGANIZATION = os.getenv('OPENAI_ORGANIZATION', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '1000'))
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
    
    # Stripe (Payments)
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')
    STRIPE_API_VERSION = os.getenv('STRIPE_API_VERSION', '2023-10-16')
    DEFAULT_CURRENCY = os.getenv('DEFAULT_CURRENCY', 'CHF')
    
    # Feature Flags
    FEATURE_AI_ENABLED = os.getenv('FEATURE_AI_ENABLED', 'true').lower() == 'true'
    FEATURE_PAYMENTS_ENABLED = os.getenv('FEATURE_PAYMENTS_ENABLED', 'true').lower() == 'true'
    FEATURE_GAMIFICATION_ENABLED = os.getenv('FEATURE_GAMIFICATION_ENABLED', 'true').lower() == 'true'
    SEARCH_RESULTS_PER_PAGE = 20
    
    # Celery
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', f"{REDIS_URL}/{REDIS_QUEUE_DB}")
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', f"{REDIS_URL}/{REDIS_QUEUE_DB}")
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TASK_TRACK_STARTED = True
    CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
    CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes
    
    # WebSockets
    SOCKETIO_MESSAGE_QUEUE = os.getenv('SOCKETIO_MESSAGE_QUEUE', f"{REDIS_URL}/{REDIS_SOCKETIO_DB}")
    SOCKETIO_ASYNC_MODE = os.getenv('SOCKETIO_ASYNC_MODE', 'eventlet')
    SOCKETIO_CORS_ALLOWED_ORIGINS = os.getenv('SOCKETIO_CORS_ALLOWED_ORIGINS', '*')
    
    # External Services
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')
    RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY', '')
    RECAPTCHA_SITE_KEY = os.getenv('RECAPTCHA_SITE_KEY', '')
    GOOGLE_OAUTH_CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID', '')
    GOOGLE_OAUTH_CLIENT_SECRET = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET', '')
    FACEBOOK_OAUTH_CLIENT_ID = os.getenv('FACEBOOK_OAUTH_CLIENT_ID', '')
    FACEBOOK_OAUTH_CLIENT_SECRET = os.getenv('FACEBOOK_OAUTH_CLIENT_SECRET', '')
    APPLE_OAUTH_CLIENT_ID = os.getenv('APPLE_OAUTH_CLIENT_ID', '')
    APPLE_OAUTH_TEAM_ID = os.getenv('APPLE_OAUTH_TEAM_ID', '')
    APPLE_OAUTH_KEY_ID = os.getenv('APPLE_OAUTH_KEY_ID', '')
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    
    # API
    API_VERSION = 'v1'
    API_TITLE = 'Lucky Kangaroo API'
    API_DESCRIPTION = 'API for Lucky Kangaroo - The Ultimate Exchange Platform'
    OPENAPI_VERSION = '3.0.3'
    OPENAPI_URL_PREFIX = '/api'
    OPENAPI_SWAGGER_UI_PATH = '/swagger-ui'
    OPENAPI_SWAGGER_UI_URL = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    
    # Trust & Safety
    MIN_TRUST_SCORE = 0
    MAX_TRUST_SCORE = 100
    TRUST_SCORE_THRESHOLD = 70
    
    # Exchange
    MAX_EXCHANGE_PARTICIPANTS = 8
    
    # File Storage
    USE_S3 = os.getenv('USE_S3', 'false').lower() == 'true'
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'lucky-kangaroo-uploads')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))
    LOG_DIR = os.path.dirname(LOG_FILE) if os.path.dirname(LOG_FILE) else 'logs'
    
    # Ensure log directory exists
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)
    
    # Monitoring
    SENTRY_DSN = os.getenv('SENTRY_DSN', '')
    DATADOG_TRACE_ENABLED = os.getenv('DATADOG_TRACE_ENABLED', 'false').lower() == 'true'
    
    # Feature Flags
    ENABLE_AI_FEATURES = os.getenv('ENABLE_AI_FEATURES', 'true').lower() == 'true'
    ENABLE_EMAIL_VERIFICATION = os.getenv('ENABLE_EMAIL_VERIFICATION', 'true').lower() == 'true'
    ENABLE_TWO_FACTOR_AUTH = os.getenv('ENABLE_TWO_FACTOR_AUTH', 'false').lower() == 'true'
    
    # External Services
    GOOGLE_OAUTH_CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID', '')
    GOOGLE_OAUTH_CLIENT_SECRET = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET', '')
    FACEBOOK_OAUTH_CLIENT_ID = os.getenv('FACEBOOK_OAUTH_CLIENT_ID', '')
    FACEBOOK_OAUTH_CLIENT_SECRET = os.getenv('FACEBOOK_OAUTH_CLIENT_SECRET', '')
    APPLE_OAUTH_CLIENT_ID = os.getenv('APPLE_OAUTH_CLIENT_ID', '')
    APPLE_OAUTH_TEAM_ID = os.getenv('APPLE_OAUTH_TEAM_ID', '')
    APPLE_OAUTH_KEY_ID = os.getenv('APPLE_OAUTH_KEY_ID', '')
    
    # CDN
    CDN_URL = os.getenv('CDN_URL', '')


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
    PROPAGATE_EXCEPTIONS = True
    WTF_CSRF_ENABLED = False
    
    # Development-specific settings
    TEMPLATES_AUTO_RELOAD = True
    EXPLAIN_TEMPLATE_LOADING = False
    
    # Enable CORS for development
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
    
    # Disable caching in development
    SEND_FILE_MAX_AGE_DEFAULT = 0
    
    # Enable profiling
    PROFILE = os.getenv('PROFILE', 'false').lower() == 'true'


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    
    # Disable background tasks during tests
    CELERY_ALWAYS_EAGER = True
    CELERY_EAGER_PROPAGATES = True


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING')
    
    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PREFERRED_URL_SCHEME = 'https'
    
    # Rate limiting
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '1000 per hour')
    
    # Server
    SERVER_NAME = os.getenv('SERVER_NAME')
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')
    
    # Cache
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', '300'))
    
    # File uploads
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '33554432'))  # 32MB
    
    # Performance
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False


# External services configuration
class ServicesConfig:
    # Email settings
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@luckykangaroo.com')
    
    # Stripe (Payments)
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')
    STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', '')
    
    # OpenAI (for AI features)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Google Maps (for geolocation)
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')
    
    # Sentry (error tracking)
    SENTRY_DSN = os.getenv('SENTRY_DSN', '')
    SENTRY_ENVIRONMENT = os.getenv('SENTRY_ENVIRONMENT', 'development')
    
    # Redis (for caching and background tasks)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Search (OpenSearch/Elasticsearch)
    SEARCH_URL = os.getenv('SEARCH_URL', 'http://localhost:9200')
    SEARCH_INDEX_PREFIX = os.getenv('SEARCH_INDEX_PREFIX', 'luckykangaroo')
    
    # File storage (S3 or local)
    STORAGE_PROVIDER = os.getenv('STORAGE_PROVIDER', 'local')  # 'local' or 's3'
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'lucky-kangaroo-uploads')

# Configuration dictionary
CONFIG_BY_NAME = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config(env: str = None):
    """Get configuration class based on environment."""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    return CONFIG_BY_NAME.get(env.lower(), CONFIG_BY_NAME['default'])

# Get configuration from environment
ENV = os.getenv('FLASK_ENV', 'development')
config = CONFIG_BY_NAME.get(ENV, DevelopmentConfig)
