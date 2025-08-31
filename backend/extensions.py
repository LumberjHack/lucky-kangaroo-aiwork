import os
from datetime import timedelta
import json
from functools import wraps
from typing import Optional

from flask import request, jsonify, current_app, Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_restx import Api
from flask_principal import Principal, Permission, RoleNeed, Identity, identity_loaded, UserNeed
from opensearchpy import OpenSearch
from celery import Celery
from redis import Redis, ConnectionPool
from sqlalchemy import event
from sqlalchemy.engine import Engine
import stripe

# Initialize extensions with no arguments
db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
jwt = JWTManager()
mail = Mail()
bcrypt = Bcrypt()
cors = CORS()
cache = Cache()
principal = Principal(use_sessions=False)

# Rate limiting
def get_remote_identifier():
    """Get remote identifier for rate limiting, prefers X-Forwarded-For if behind proxy."""
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0].split(',')[0]
    return get_remote_address()

limiter = Limiter(
    key_func=get_remote_identifier,
    default_limits=["200 per hour", "50 per minute"],
    storage_uri="memory://"  # Will be overridden by app config
)

# Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
stripe.api_version = '2023-10-16'  # Use a fixed API version

# Socket.IO
socketio = SocketIO(
    async_mode='eventlet',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True,
    json=json  # Use the standard json module for better performance
)

# REST API
api = Api(
    version='1.0',
    title='Lucky Kangaroo API',
    description='API for Lucky Kangaroo - The Ultimate Exchange Platform',
    doc='/api/docs',
    default='Lucky Kangaroo',
    default_label='Core API endpoints',
    security='Bearer Auth',
    authorizations={
        'Bearer Auth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Type in the *Value* input box: Bearer {your JWT token}.'
        }
    }
)

# Permissions
admin_permission = Permission(RoleNeed('admin'))
moderator_permission = Permission(RoleNeed('moderator'))
user_permission = Permission(RoleNeed('user'))

# Initialize Celery without config
celery = Celery()

# Initialize OpenSearch client
search = None


def init_extensions(app: Flask) -> None:
    """Initialize all extensions with the Flask app.
    
    Args:
        app: The Flask application instance
    """
    # SQLAlchemy
    db.init_app(app)
    
    # Migrations
    migrate.init_app(app, db)
    
    # Marshmallow
    ma.init_app(app)
    
    # JWT
    jwt.init_app(app)
    
    # Configure JWT
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
    
    # Initialize Stripe with app config
    stripe.api_key = app.config.get('STRIPE_SECRET_KEY')
    stripe.max_network_retries = 2
    
    # Mail
    mail.init_app(app)
    
    # Bcrypt
    bcrypt.init_app(app)
    
    # CORS
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', '*'),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            "expose_headers": ["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
            "supports_credentials": True,
            "max_age": 600
        },
        r"/socket.io/*": {
            "origins": app.config.get('CORS_ORIGINS', '*'),
            "methods": ["GET", "POST"],
            "allow_headers": ["Authorization"],
            "supports_credentials": True
        },
        r"/webhooks/*": {
            "origins": app.config.get('CORS_ORIGINS', '*'),
            "methods": ["POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Stripe-Signature"],
            "supports_credentials": True
        }
    })

    # Caching
    cache.init_app(app, config={
        'CACHE_TYPE': app.config.get('CACHE_TYPE', 'SimpleCache'),
        'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
    })
    
    # Principal
    principal.init_app(app)
    
    # Rate limiting
    limiter.storage_uri = app.config.get('RATELIMIT_STORAGE_URI')
    limiter.init_app(app)
    
    # Socket.IO
    socketio.init_app(
        app,
        message_queue=app.config.get('SOCKETIO_MESSAGE_QUEUE'),
        cors_allowed_origins=app.config.get('CORS_ORIGINS', '*'),
        async_mode=app.config.get('SOCKETIO_ASYNC_MODE', 'eventlet')
    )
    
    # Celery
    init_celery(app)
    
    # OpenSearch
    global search
    search = init_opensearch(app)
    
    # Add request context processors and other app-wide configurations
    with app.app_context():
        # Import models to ensure they are registered with SQLAlchemy
        
        # Create database tables if they don't exist
        if app.config.get('SQLALCHEMY_DATABASE_URI', '').startswith('sqlite'):
            # Enable foreign key constraints for SQLite
            @event.listens_for(Engine, 'connect')
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute('PRAGMA foreign_keys=ON')
                cursor.close()
        
        # Initialize database
        db.create_all()
        
        # Configure Flask-Principal
        @identity_loaded.connect_via(app)
        def on_identity_loaded(sender: Flask, identity: Identity) -> None:
            """Add user roles to identity."""
            from models.user import User  # Avoid circular imports
            
            # Set the identity user object
            identity.user = User.query.get(identity.id)
            
            if identity.user:
                # Add the UserNeed to the identity
                identity.provides.add(UserNeed(identity.user.id))
                
                # Add roles to the identity
                if identity.user.roles:
                    for role in identity.user.roles:
                        identity.provides.add(RoleNeed(role.name))
        
        # Error handlers
        @jwt.unauthorized_loader
        def unauthorized_callback(callback):
            return jsonify({
                'error': 'authorization_required',
                'message': 'Missing or invalid token'
            }), 401
        
        @jwt.invalid_token_loader
        def invalid_token_callback(callback):
            return jsonify({
                'error': 'invalid_token',
                'message': 'Signature verification failed'
            }), 422
        
        @jwt.expired_token_loader
        def expired_token_callback(jwt_header, jwt_payload):
            return jsonify({
                'error': 'token_expired',
                'message': 'The token has expired'
            }), 401
        
        @jwt.revoked_token_loader
        def revoked_token_callback(jwt_header, jwt_payload):
            return jsonify({
                'error': 'token_revoked',
                'message': 'The token has been revoked'
            }), 401


def init_celery(app=None):
    """Initialize Celery with Flask app context."""
    app = app or current_app
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.conf.update(app.config)
    celery.Task = ContextTask
    
    # Configure Celery
    celery.conf.update(
        broker_url=app.config.get('CELERY_BROKER_URL'),
        result_backend=app.config.get('CELERY_RESULT_BACKEND'),
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=30 * 60,  # 30 minutes
        task_soft_time_limit=25 * 60,  # 25 minutes
        worker_max_tasks_per_child=100,  # Prevent memory leaks
        worker_prefetch_multiplier=1,  # Fair task distribution
        broker_connection_retry_on_startup=True,
        broker_connection_retry=True,
        broker_connection_max_retries=10,
        broker_transport_options={
            'max_retries': 3,
            'interval_start': 0,
            'interval_step': 0.2,
            'interval_max': 0.5,
        }
    )
    
    return celery


def init_opensearch(app):
    """Initialize OpenSearch client."""
    global search
    
    if app.config.get('OPENSEARCH_URL'):
        search = OpenSearch(
            [app.config['OPENSEARCH_URL']],
            http_auth=(
                app.config.get('OPENSEARCH_USER', ''),
                app.config.get('OPENSEARCH_PASSWORD', '')
            ) if app.config.get('OPENSEARCH_USER') else None,
            use_ssl=app.config.get('OPENSEARCH_USE_SSL', True),
            verify_certs=app.config.get('OPENSEARCH_VERIFY_CERTS', True),
            ssl_show_warn=app.config.get('OPENSEARCH_SSL_SHOW_WARN', True),
            timeout=30,
            max_retries=10,
            retry_on_timeout=True
        )
        
        # Create default index if it doesn't exist
        if not search.indices.exists(index='listings'):
            search.indices.create(
                index='listings',
                body={
                    'settings': {
                        'number_of_shards': 1,
                        'number_of_replicas': 0
                    },
                    'mappings': {
                        'properties': {
                            'title': {'type': 'text', 'analyzer': 'standard'},
                            'description': {'type': 'text', 'analyzer': 'standard'},
                            'category': {'type': 'keyword'},
                            'condition': {'type': 'keyword'},
                            'price': {'type': 'float'},
                            'location': {'type': 'geo_point'},
                            'created_at': {'type': 'date'},
                            'user_id': {'type': 'keyword'},
                            'tags': {'type': 'keyword'}
                        }
                    }
                }
            )


def redis_connection() -> Optional[Redis]:
    """Get a Redis connection from the pool."""
    if not hasattr(redis_connection, 'pool'):
        try:
            redis_url = current_app.config.get('REDIS_URL')
            if not redis_url:
                return None
                
            redis_connection.pool = ConnectionPool.from_url(
                redis_url,
                max_connections=20,
                decode_responses=True
            )
        except Exception as e:
            current_app.logger.error(f'Failed to create Redis connection pool: {e}')
            return None
    
    try:
        return Redis(connection_pool=redis_connection.pool)
    except Exception as e:
        current_app.logger.error(f'Failed to get Redis connection: {e}')
        return None


def rate_limited(max_per_minute=60):
    """Decorator for rate limiting API endpoints."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_app.testing:  # Skip rate limiting in tests
                key = f'rate_limit:{request.endpoint}:{get_remote_identifier()}'
                redis = redis_connection()
                
                if redis:
                    current = redis.incr(key)
                    if current == 1:
                        redis.expire(key, 60)  # Set expiry to 1 minute
                    
                    if current > max_per_minute:
                        return jsonify({
                            'error': 'Too many requests',
                            'message': f'Rate limit exceeded: {max_per_minute} requests per minute',
                            'status_code': 429
                        }), 429
            
            return f(*args, **kwargs)
        return wrapped
    return decorator
