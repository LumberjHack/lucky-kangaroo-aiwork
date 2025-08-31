#!/usr/bin/env python3
"""
Lucky Kangaroo - Backend API
Application principale Flask avec configuration modulaire
"""
import logging
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os
import sys
from typing import Optional, Dict, Any

# Ajout du rpertoire parent au PYTHONPATH pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import des modules de configuration et de gestion des erreurs
from config import config
from errors import register_error_handlers, APIError, ValidationError, AuthenticationError, ForbiddenError, NotFoundError, ConflictError, RateLimitError

import os
import sys
import logging
import datetime
import uuid
import json
import stripe
import openai
from functools import wraps
from typing import Dict, Any, Optional, List, Union, Tuple, Callable

from flask import Flask, request, jsonify, send_from_directory, redirect, url_for, current_app, g
from flask.json.provider import DefaultJSONProvider
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException, BadRequest, Unauthorized, Forbidden, NotFound, InternalServerError
from dotenv import load_dotenv
from marshmallow import Schema, fields, validates, ValidationError, validate, EXCLUDE, post_load
import jwt
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, create_refresh_token,
    get_jwt_identity, get_jwt, verify_jwt_in_request, get_jwt_claims
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_principal import Principal, Permission, RoleNeed, UserNeed, identity_loaded, Identity
from flask_mail import Mail, Message
from flask_socketio import SocketIO, emit, join_room, leave_room, ConnectionRefusedError
from flask_restx import Api, Resource, fields, Namespace, reqparse, abort
from opensearchpy import OpenSearch, NotFoundError, helpers
from celery import Celery, Task
import redis
from redis.exceptions import RedisError
from sqlalchemy import event, func, or_, and_, text, exc as sa_exc
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from geoalchemy2 import Geometry, functions as geo_func
from geoalchemy2.shape import to_shape
from shapely.geometry import Point, shape, mapping
import geojson
import boto3
from botocore.exceptions import ClientError
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from prometheus_flask_exporter import PrometheusMetrics
from flask_caching import Cache
from flask_cors import CORS
from flask_limiter import RateLimitExceeded
from flask_limiter.util import get_remote_address as get_limiter_remote_address
from flask_limiter.extension import C
from flask_limiter.wrappers import Limit, LimitGroup

# Configuration de Stripe
stripe.api_version = '2023-10-16'

# Configuration d'OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.organization = os.getenv('OPENAI_ORGANIZATION', '')

# Configuration du cache
cache = Cache()

# Configuration du rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    storage_options={"socket_connect_timeout": 30},
    strategy="fixed-window",
    headers_enabled=True
)

# Configuration de Sentry
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[
        FlaskIntegration(),
        SqlalchemyIntegration(),
        RedisIntegration()
    ],
    traces_sample_rate=1.0 if os.getenv('FLASK_ENV') == 'development' else 0.1,
    environment=os.getenv('FLASK_ENV', 'production')
)

# Local imports
from config import config
from extensions import (
    db, migrate, ma, jwt, mail, bcrypt, cors, principal, limiter, 
    socketio, celery, search, init_extensions, redis_connection, rate_limited,
    admin_permission, moderator_permission, user_permission
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Sentry if DSN is provided
if os.getenv('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
        environment=os.getenv('FLASK_ENV', 'development')
    )

# Custom JSON encoder to handle datetime and other non-serializable types
class CustomJSONProvider(DefaultJSONProvider):
    """Custom JSON provider to handle additional types."""
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat() + 'Z'
        elif isinstance(o, (datetime.date, datetime.time)):
            return o.isoformat()
        elif isinstance(o, datetime.timedelta):
            return str(o)
        elif isinstance(o, uuid.UUID):
            return str(o)
        elif hasattr(o, 'to_dict'):
            return o.to_dict()
        elif hasattr(o, 'to_json'):
            return o.to_json()
        elif isinstance(o, bytes):
            return o.decode('utf-8', errors='replace')
        elif hasattr(o, '__dict__'):
            return vars(o)
        elif hasattr(o, '__table__'):  # SQLAlchemy model
            return {c.name: getattr(o, c.name) for c in o.__table__.columns}
        return super().default(o)


def create_app(config_name: Optional[str] = None):
    """
    Application factory function to create and configure the Flask app.
    
    Args:
        config_name: Configuration to use (development, testing, production)
        
    Returns:
        Flask: Configured Flask application instance
    """
    # Create and configure the app
    app = Flask(__name__)
    
    # Initialize OpenSearch client
    search = None
    if app.config.get('OPENSEARCH_URL'):
        try:
            search = OpenSearch([app.config['OPENSEARCH_URL']], use_ssl=True, verify_certs=True)
        except Exception as e:
            app.logger.error(f'Failed to initialize OpenSearch client: {str(e)}')
    
    # Configuration de l'application
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Chargement de la configuration approprie
    app.config.from_object(config[config_name])
    
    # Initialisation des extensions
    from .extensions import db, migrate, jwt, cors, cache, limiter, mail, sentry_sdk
    
    # Configuration de la base de donnes
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configuration JWT
    jwt.init_app(app)
    
    # Configuration CORS
    cors.init_app(app, resources={"*": {"origins": app.config.get('CORS_ORIGINS', '*')}})
    
    # Configuration du cache
    cache.init_app(app, config=app.config.get('CACHE_CONFIG', {}))
    
    # Configuration du rate limiting
    limiter.init_app(app)
    
    # Configuration de l'envoi d'emails
    mail.init_app(app)
    
    # Configuration de Sentry pour la surveillance des erreurs
    if app.config.get('SENTRY_DSN'):
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            environment=app.config.get('ENV', 'development'),
            traces_sample_rate=app.config.get('SENTRY_TRACES_SAMPLE_RATE', 0.5),
            profiles_sample_rate=app.config.get('SENTRY_PROFILES_SAMPLE_RATE', 0.5),
        )
    
    # Configuration de la journalisation
    configure_logging(app)
    
    # Enregistrement des blueprints
    register_blueprints(app)
    
    # Enregistrement des gestionnaires d'erreurs
    register_error_handlers(app)
    
    # Commandes CLI personnalises
    register_commands(app)
    
    # Contexte shell personnalis
    @app.shell_context_processor
    def make_shell_context():
        from .models import User, Listing, Exchange, Chat, Notification, Image
        return {
            'db': db,
            'User': User,
            'Listing': Listing,
            'Exchange': Exchange,
            'Chat': Chat,
            'Notification': Notification,
            'Image': Image
        }
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Apply configuration based on environment
    if config_name == 'testing':
        app.config.from_object('config.TestingConfig')
    elif config_name == 'production':
        app.config.from_object('config.ProductionConfig')
    else:  # development by default
        app.config.from_object('config.DevelopmentConfig')
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Override with environment variables
    for key in [
        'SECRET_KEY', 'SQLALCHEMY_DATABASE_URI', 'JWT_SECRET_KEY',
        'MAIL_SERVER', 'MAIL_PORT', 'MAIL_USE_TLS', 'MAIL_USE_SSL',
        'MAIL_USERNAME', 'MAIL_PASSWORD', 'MAIL_DEFAULT_SENDER',
        'REDIS_URL', 'OPENSEARCH_URL', 'SENTRY_DSN', 'STRIPE_SECRET_KEY',
        'STRIPE_PUBLISHABLE_KEY', 'STRIPE_WEBHOOK_SECRET', 'OPENAI_API_KEY',
        'GOOGLE_MAPS_API_KEY', 'RECAPTCHA_SECRET_KEY', 'RECAPTCHA_SITE_KEY'
    ]:
        if key in os.environ:
            app.config[key] = os.environ[key]
    
    # Configure JSON provider
    app.json = CustomJSONProvider(app)
    
    # Initialize extensions
    from extensions import (
        db, migrate, ma, jwt, mail, bcrypt, cors, principal, limiter,
        socketio, celery, search, cache, init_extensions, redis_connection
    )
    
    # Initialize all extensions
    init_extensions(app)
    
    # Configure Stripe
    stripe.api_key = app.config.get('STRIPE_SECRET_KEY')
    
    # Configure OpenAI
    openai.api_key = app.config.get('OPENAI_API_KEY')
    
    # Configure Sentry in production
    if app.config.get('SENTRY_DSN') and app.config['ENV'] == 'production':
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            integrations=[
                FlaskIntegration(),
                SqlalchemyIntegration(),
                RedisIntegration()
            ],
            traces_sample_rate=1.0,
            environment=app.config['ENV']
        )
    
    # Configure CORS
    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins": app.config.get('CORS_ORIGINS', '*').split(',')
            },
            r"/socket.io/*": {
                "origins": app.config.get('CORS_ORIGINS', '*').split(',')
            },
            r"/webhook/*": {
                "origins": app.config.get('CORS_ORIGINS', '*').split(',')
            }
        },
        supports_credentials=True,
        expose_headers=['Content-Type', 'X-Requested-With', 'Authorization'],
        allow_headers=['Content-Type', 'Authorization', 'X-Forwarded-For', 'X-Real-IP'],
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        max_age=600
    )
    
    # Configure rate limiting
    limiter.init_app(app)
    
    # Configure cache
    cache.init_app(app, config={
        'CACHE_TYPE': 'RedisCache',
        'CACHE_REDIS_URL': app.config.get('REDIS_URL'),
        'CACHE_DEFAULT_TIMEOUT': 300  # 5 minutes
    })
    
    # Configure JWT
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token_in_redis = redis_connection.get(jti)
        return token_in_redis is not None
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'error': 'Token has been revoked',
            'message': 'The token has been revoked. Please log in again.'
        }), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'error': 'Token has expired',
            'message': 'The access token has expired. Please refresh the token or log in again.'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'success': False,
            'error': 'Invalid token',
            'message': 'The provided token is invalid. Please log in again.'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'success': False,
            'error': 'Authorization required',
            'message': 'Request does not contain an access token. Please log in.'
        }), 401
    
    # Register blueprints
    from api.v1 import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')
    
    # Register error handlers
    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': str(error)
        }), 400
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        return jsonify({
            'success': False,
            'error': 'Unauthorized',
            'message': 'Authentication is required to access this resource.'
        }), 401
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource.'
        }), 403
    
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': 'The requested resource was not found.'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed_error(error):
        return jsonify({
            'success': False,
            'error': 'Method Not Allowed',
            'message': 'The method is not allowed for the requested URL.'
        }), 405
    
    @app.errorhandler(409)
    def conflict_error(error):
        return jsonify({
            'success': False,
            'error': 'Conflict',
            'message': str(error)
        }), 409
    
    @app.errorhandler(422)
    def validation_error(error):
        return jsonify({
            'success': False,
            'error': 'Validation Error',
            'message': 'Input validation failed',
            'errors': error.messages if hasattr(error, 'messages') else str(error)
        }), 422
    
    @app.errorhandler(RateLimitExceeded)
    def ratelimit_handler(error):
        return jsonify({
            'success': False,
            'error': 'Too Many Requests',
            'message': f'Rate limit exceeded: {error.description}'
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error('Internal Server Error: %s', str(error), exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred. Please try again later.'
        }), 500
    
    # Handle database errors
    @app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(error):
        db.session.rollback()
        app.logger.error(f'Database error: {str(error)}', exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Database Error',
            'message': 'A database error occurred. Please try again.'
        }), 500
    
    # Handle Redis errors
    @app.errorhandler(RedisError)
    def handle_redis_error(error):
        app.logger.error('Redis error: %s', str(error), exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Cache Error',
            'message': 'A cache error occurred. Please try again.'
        }), 500
    
    # Handle AWS errors
    @app.errorhandler(ClientError)
    def handle_aws_error(error):
        app.logger.error('AWS error: %s', str(error), exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Storage Error',
            'message': 'A storage error occurred. Please try again.'
        }), 500
    
    # Shell context
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': User,
            'Listing': Listing,
            'Image': Image,
            'Exchange': Exchange,
            'Message': Message,
            'Review': Review,
            'Notification': Notification
        }
    
    # CLI commands
    @app.cli.command('init-db')
    def init_db_command():
        """Initialize the database."""
        db.create_all()
        print('Database initialized.')
    
    @app.cli.command('create-admin')
    @click.argument('email')
    @click.argument('password')
    def create_admin_command(email, password):
        """Create an admin user."""
        from werkzeug.security import generate_password_hash
        
        if not email or not password:
            print('Error: Email and password are required')
            return
        
        if User.query.filter_by(email=email).first():
            print('Error: User already exists')
            return
        
        admin = User(
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            is_admin=True,
            is_active=True,
            email_verified=True
        )
        
        db.session.add(admin)
        db.session.commit()
        print(f'Admin user {email} created successfully')
    
    @app.cli.command('reindex')
    def reindex_command():
        """Reindex all listings in the search engine."""
        from opensearchpy.helpers import bulk
        from tqdm import tqdm
        from models.listing import Listing  # Import the Listing model
        
        index_name = f"{app.config['SEARCH_INDEX_PREFIX']}_listings"
        
        # Delete existing index
        try:
            search.indices.delete(index=index_name)
            print(f'Deleted existing index: {index_name}')
        except NotFoundError:
            print(f'Index {index_name} does not exist, creating new index...')
        
        # Create index with mapping
        mapping = {
            'mappings': {
                'properties': {
                    'title': {'type': 'text', 'analyzer': 'french'},
                    'description': {'type': 'text', 'analyzer': 'french'},
                    'price': {'type': 'float'},
                    'location': {'type': 'geo_point'},
                    'created_at': {'type': 'date'},
                    'updated_at': {'type': 'date'},
                    'status': {'type': 'keyword'},
                    'category': {'type': 'keyword'},
                    'tags': {'type': 'keyword'}
                }
            },
            'settings': {
                'number_of_shards': 1,
                'number_of_replicas': 0
            }
        }
        
        search.indices.create(index=index_name, body=mapping)
        print(f'Created index: {index_name}')
        
        # Index all active listings with progress bar
        listings = Listing.query.filter_by(status='active').all()
        total = len(listings)
        print(f'Indexing {total} listings...')
        
        def generate_actions():
            for listing in tqdm(listings, desc='Indexing', unit='listing'):
                doc = listing.to_dict()
                doc['_index'] = index_name
                doc['_id'] = listing.id
                if hasattr(listing, 'location') and listing.location:
                    point = to_shape(listing.location)
                    doc['location'] = {'lat': point.y, 'lon': point.x}
                yield doc
        
        success, errors = bulk(
            search,
            generate_actions(),
            index=index_name,
            raise_on_error=False,
            stats_only=False
        )
        
        if errors:
            print(f'\nEncountered {len(errors)} errors during indexing:')
            for i, error in enumerate(errors[:5], 1):
                print(f'Error {i}: {error}')
            if len(errors) > 5:
                print(f'... and {len(errors) - 5} more errors')
        
        print(f'\nSuccessfully indexed {success} out of {total} listings')
        
        # Refresh the index to make the changes searchable
        search.indices.refresh(index=index_name)
        print('Index refresh complete')
    
    @app.cli.command('clear-cache')
    def clear_cache_command():
        """Clear the application cache."""
        try:
            cache.clear()
            print('Cache cleared successfully')
        except Exception as e:
            print(f'Error clearing cache: {str(e)}')
    
    @app.cli.command('send-test-email')
    @click.argument('recipient')
    def send_test_email_command(recipient):
        """Send a test email to the specified recipient."""
        try:
            msg = Message(
                'Test Email from Lucky Kangaroo',
                sender=app.config['MAIL_DEFAULT_SENDER'],
                recipients=[recipient]
            )
            msg.body = 'This is a test email from the Lucky Kangaroo application.'
            mail.send(msg)
            print(f'Test email sent to {recipient}')
        except Exception as e:
            print(f'Error sending test email: {str(e)}')
    
    @app.cli.command('create-indexes')
    def create_indexes_command():
        """Create database indexes for better query performance."""
        from sqlalchemy import Index, text
        
        # Example indexes - adjust based on your query patterns
        indexes = [
            ('user', 'email', True),  # Unique index on email
            ('listing', 'user_id', False),
            ('listing', 'status', False),
            ('exchange', 'status', False),
            ('exchange', 'initiator_id', False),
            ('exchange', 'receiver_id', False),
            ('message', 'exchange_id', False),
            ('message', 'sender_id', False),
            ('notification', 'user_id', False),
            ('notification', 'read', False),
            ('review', 'author_id', False),
            ('review', 'target_id', False),
        ]
        
        with db.engine.connect() as connection:
            for table, column, is_unique in indexes:
                idx_name = f'idx_{table}_{column}'
                unique = 'UNIQUE' if is_unique else ''
                try:
                    connection.execute(text(
                        f'CREATE {unique} INDEX IF NOT EXISTS {idx_name} ON {table} ({column})'
                    ))
                    print(f'Created index: {idx_name}')
                except Exception as e:
                    print(f'Error creating index {idx_name}: {str(e)}')
        
        print('Index creation complete')
    
    @app.cli.command('check-services')
    def check_services_command():
        """Check the status of external services."""
        import requests
        from urllib.parse import urlparse
        
        services = {
            'Database': app.config.get('SQLALCHEMY_DATABASE_URI'),
            'Redis': app.config.get('REDIS_URL'),
            'OpenSearch': app.config.get('OPENSEARCH_URL'),
            'Mail Server': f"{app.config.get('MAIL_SERVER')}:{app.config.get('MAIL_PORT')}" if app.config.get('MAIL_SERVER') else None,
            'Stripe': 'Configured' if app.config.get('STRIPE_SECRET_KEY') else None,
            'OpenAI': 'Configured' if app.config.get('OPENAI_API_KEY') else None
        }
        
        print('\n=== Service Status ===')
        for name, url in services.items():
            status = 'OK' if url else 'Not Configured'
            status_icon = '' if url else ''
            print(f'{status_icon} {name}: {status}')
            if url and name in ['Database', 'Redis', 'OpenSearch']:
                parsed = urlparse(url)
                
                # Check PostgreSQL connection
                if parsed.scheme in ['postgresql', 'postgres']:
                    try:
                        db.session.execute('SELECT 1')
                        print(f'   Connected to {parsed.hostname}:{parsed.port or 5432}')
                    except Exception as e:
                        print(f'   Error connecting to PostgreSQL: {str(e)}')
                
                # Check Redis connection
                elif parsed.scheme == 'redis':
                    redis_conn = redis_connection()
                    if redis_conn is None:
                        print('   Redis client not initialized')
                        continue
                    
                    try:
                        redis_conn.ping()
                        print(f'   Connected to Redis at {parsed.hostname}:{parsed.port or 6379}')
                    except Exception as e:
                        print(f'   Error connecting to Redis: {str(e)}')
                    finally:
                        if redis_conn:
                            redis_conn.connection_pool.disconnect()
                
                # Check OpenSearch/Elasticsearch connection
                elif 'opensearch' in url or 'elasticsearch' in url:
                    if search is None:
                        print('   OpenSearch client not initialized')
                    else:
                        try:
                            if search.ping():
                                info = search.info()
                                version = info.get('version', {}).get('number', 'unknown')
                                print(f'   Connected to OpenSearch {version}')
                            else:
                                print('   OpenSearch ping failed')
                        except Exception as e:
                            print('   Error connecting to OpenSearch: ' + str(e))
        
        # Check email configuration
        mail_server = app.config.get('MAIL_SERVER')
        if mail_server:
            mail_port = app.config.get('MAIL_PORT')
            print(f'   Mail server: {mail_server}:{mail_port}')
            if app.config.get('MAIL_USERNAME'):
                print('   Mail authentication: Enabled')
            else:
                print('   Mail authentication: Disabled')
            
            # Only attempt to connect if credentials are provided
            if app.config.get('MAIL_USERNAME') and app.config.get('MAIL_PASSWORD'):
                try:
                    with mail.connect() as conn:
                        print('   Mail server connection: Successful')
                except Exception as e:
                    print(f'   Mail server connection failed: {str(e)}')
        else:
            print('   Mail server: Not configured')
            
        # Check Stripe configuration
        stripe_key = app.config.get('STRIPE_SECRET_KEY')
        if stripe_key:
            print('   Stripe: Configured')
            try:
                # Test Stripe connection by making a simple API call
                import stripe
                stripe.api_key = stripe_key
                account = stripe.Account.retrieve()
                business_name = account.get('business_profile', {}).get('name', 'Connected')
                print(f'   Stripe account: {business_name}')
            except Exception as e:
                print(f'   Stripe connection error: {str(e)}')
        else:
            print('   Stripe: Not configured')
            
        # Check OpenAI configuration
        openai_key = app.config.get('OPENAI_API_KEY')
        if openai_key:
            print('   OpenAI: Configured')
            try:
                import openai
                openai.api_key = openai_key
                # Test OpenAI connection by listing models (no cost)
                models = openai.Model.list()
                model_count = len(models.get('data', []))
                print(f'   OpenAI models available: {model_count}')
            except Exception as e:
                print(f'   OpenAI connection error: {str(e)}')
        else:
            print('   OpenAI: Not configured')
        
        print('\n=== Application Configuration ===')
        print(f'Environment: {app.config.get("ENV", "not set")}')
        print(f'Debug Mode: {app.config.get("DEBUG", False)}')
        print(f'Testing Mode: {app.config.get("TESTING", False)}')
        print(f'Instance Path: {app.instance_path}')
        
        # Database configuration
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if db_uri:
            parsed = urlparse(db_uri)
            print(f'\nDatabase: {parsed.scheme}://{parsed.hostname}:{parsed.port or 5432}{parsed.path}')
        
        # Cache configuration
        cache_config = app.config.get('CACHE_TYPE', 'SimpleCache')
        print(f'Cache: {cache_config}')
        if cache_config == 'RedisCache':
            redis_url = app.config.get('CACHE_REDIS_URL', app.config.get('REDIS_URL', ''))
            if redis_url:
                parsed = urlparse(redis_url)
                print(f'   Redis: {parsed.hostname}:{parsed.port or 6379}')
        
        # Feature flags
        print('\n=== Feature Flags ===')
        print(f'Maintenance Mode: {app.config.get("MAINTENANCE_MODE", False)}')
        print(f'Registration Enabled: {app.config.get("REGISTRATION_ENABLED", True)}')
        print(f'Email Verification Required: {app.config.get("EMAIL_VERIFICATION_REQUIRED", False)}')
        print(f'API Rate Limiting: {not app.config.get("RATELIMIT_DISABLED", False)}')
        
        print('\n=== System Information ===')
        import platform
        import sys
        print(f'Python: {sys.version.split()[0]}')
        print(f'OS: {platform.system()} {platform.release()}')
        print(f'Processor: {platform.processor()}')
        
        print('\nStatus check complete ')
    
    return app

def configure_logging(app) -> None:
    """Configure la journalisation pour l'application.
    
    Args:
        app: L'instance de l'application Flask
    """
    # Cration du rpertoire de logs s'il n'existe pas
    log_dir = Path(app.config.get('LOG_DIR', 'logs'))
    log_dir.mkdir(exist_ok=True, parents=True)
    
    # Configuration du format des logs
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    
    # Configuration du dictionnaire de logging
    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': log_format,
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'json': {
                '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'stream': 'ext://sys.stdout',
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'filename': str(log_dir / 'app.log'),
                'maxBytes': 10 * 1024 * 1024,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8',
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'json',
                'filename': str(log_dir / 'error.log'),
                'maxBytes': 10 * 1024 * 1024,  # 10MB
                'backupCount': 5,
                'level': 'ERROR',
                'encoding': 'utf8',
            }
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console', 'file', 'error_file'],
                'level': log_level,
                'propagate': True,
            },
            'werkzeug': {
                'handlers': ['console', 'file'],
                'level': 'INFO',  # vite les logs trop verbeux de Werkzeug
                'propagate': False,
            },
            'sqlalchemy.engine': {
                'handlers': ['console', 'file'],
                'level': 'WARNING',  # Rduit la verbosit de SQLAlchemy
                'propagate': False,
            },
        }
    }
    
    # Appliquer la configuration
    dictConfig(log_config)
    
    # Configurer le logger de l'application
    app.logger = logging.getLogger(__name__)
    app.logger.setLevel(log_level)
    
    # Dsactiver le logger de requtes HTTP de Werkzeug en production
    if not app.debug:
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    app.logger.info('Configuration de la journalisation termine')


def register_blueprints(app):
    """Register Flask blueprints."""
    # Import blueprints here to avoid circular imports
    from .api.v1.auth import auth_bp
    from .api.v1.users import users_bp
    from .api.v1.listings import listings_bp
    from .api.v1.chat import chat_bp
    from .api.v1.search import search_bp
    from .api.v1.notifications import notifications_bp
    from .api.v1.admin import admin_bp
    from .api.v1.gamification import gamification_bp
    from .api.v1.ai import ai_bp
    from .api.v1.payments import payments_bp
    from .api.v1.reports import reports_bp
    
    # Enable CORS for all routes
    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins": app.config.get("ALLOWED_ORIGINS", ["*"]),
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True
            }
        }
    )
    
    # Register blueprints with versioning
    api_v1_prefix = "/api/v1"
    
    # Core features
    app.register_blueprint(auth_bp, url_prefix=f"{api_v1_prefix}/auth")
    app.register_blueprint(users_bp, url_prefix=f"{api_v1_prefix}/users")
    app.register_blueprint(listings_bp, url_prefix=f"{api_v1_prefix}/listings")
    app.register_blueprint(chat_bp, url_prefix=f"{api_v1_prefix}/chat")
    app.register_blueprint(search_bp, url_prefix=f"{api_v1_prefix}/search")
    app.register_blueprint(notifications_bp, url_prefix=f"{api_v1_prefix}/notifications")
    
    # Business features
    app.register_blueprint(admin_bp, url_prefix=f"{api_v1_prefix}/admin")
    app.register_blueprint(gamification_bp, url_prefix=f"{api_v1_prefix}/gamification")
    app.register_blueprint(ai_bp, url_prefix=f"{api_v1_prefix}/ai")
    app.register_blueprint(payments_bp, url_prefix=f"{api_v1_prefix}/payments")
    app.register_blueprint(reports_bp, url_prefix=f"{api_v1_prefix}/reports")
    
    # Health check endpoint
    @app.route("/health")
    def health_check():
        return (
            jsonify(
                {
                    "status": "healthy",
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                    "version": "1.0.0"
                }
            ),
            200
        )
    
    # Register API documentation
    # Initialize API documentation
    try:
        from api.v1 import api as api_blueprint
        api_blueprint.init_app(app)
    except ImportError as e:
        app.logger.warning(f'Failed to initialize API documentation: {str(e)}')


def register_error_handlers(app):
    """Register error handlers."""
    
    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            'error': 'bad_request',
            'message': str(error)
        }), 400
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        return jsonify({
            'error': 'unauthorized',
            'message': 'Authentication required'
        }), 401
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return jsonify({
            'error': 'forbidden',
            'message': 'You do not have permission to access this resource'
        }), 403
    
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'error': 'not_found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed_error(error):
        return jsonify({
            'error': 'method_not_allowed',
            'message': 'The method is not allowed for the requested URL'
        }), 405
    
    @app.errorhandler(409)
    def conflict_error(error):
        return jsonify({
            'error': 'conflict',
            'message': str(error)
        }), 409
    
    @app.errorhandler(422)
    def validation_error(error):
        return jsonify({
            'error': 'validation_error',
            'message': 'Validation failed',
            'errors': error.description
        }), 422
    
    @app.errorhandler(429)
    def ratelimit_handler(error):
        return jsonify({
            'error': 'rate_limit_exceeded',
            'message': f'Rate limit exceeded: {error.description}'
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal Error: {error}')
        return jsonify({
            'error': 'internal_server_error',
            'message': 'An internal server error occurred'
        }), 500
    
    # Handle SQLAlchemy errors
    @app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(error):
        db.session.rollback()
        app.logger.error(f'Database Error: {error}')
        return jsonify({
            'error': 'database_error',
            'message': 'A database error occurred'
        }), 500
    
    # Handle Redis errors
    @app.errorhandler(RedisError)
    def handle_redis_error(error):
        app.logger.error(f'Redis Error: {error}')
        return jsonify({
            'error': 'cache_error',
            'message': 'A cache service error occurred'
        }), 500
    
    # Handle AWS errors
    @app.errorhandler(ClientError)
    def handle_aws_error(error):
        app.logger.error(f'AWS Error: {error}')
        return jsonify({
            'error': 'storage_error',
            'message': 'A storage service error occurred'
        }), 500


def register_shell_context(app):
    ""Register shell context objects."""
    @app.shell_context_processor
    def make_shell_context():
        from .models import User, Listing, Exchange, Chat, Notification, Image
        
        return {
            'db': db,
            'User': User,
            'Listing': Listing,
            'Exchange': Exchange,
            'Chat': Chat,
            'Notification': Notification,
            'Image': Image
        }


def register_commands(app):
    ""Register Click commands."""
    import click
    from flask.cli import with_appcontext
    
    @app.cli.command('init-db')
    @with_appcontext
    def init_db_command():
        """Initialize the database."""
        db.create_all()
        click.echo('Initialized the database.')
    
    @app.cli.command('create-admin')
    @click.argument('email')
    @click.argument('password')
    @with_appcontext
    def create_admin_command(email, password):
        """Create an admin user."""
        from .models import User
        
        if User.query.filter_by(email=email).first():
            click.echo(f'User {email} already exists.')
            return
        
        admin = User(
            email=email,
            password=bcrypt.generate_password_hash(password).decode('utf-8'),
            is_admin=True,
            email_verified=True
        )
        
        db.session.add(admin)
        db.session.commit()
        click.echo(f'Admin user {email} created.')
    
    @app.cli.command('reindex')
    @with_appcontext
    def reindex_command():
        """Reindex all listings in the search engine."""
        from .models import Listing
        from .search import index_listing
        
        count = 0
        for listing in Listing.query.filter_by(is_active=True):
            index_listing(listing)
            count += 1
        
        click.echo(f'Indexed {count} listings.')


# Create the application
app = create_app()


if __name__ == '__main__':
    # Run the application
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])

# Small helpers
def bool_flag(val):
    return str(val).strip().lower() in ('1', 'true', 'yes', 'on') if val is not None else False

def build_upload_url(filename: str) -> str:
    """Build absolute public URL for a file in UPLOAD_FOLDER."""
    scheme = request.scheme
    host = request.host
    return f"{scheme}://{host}/uploads/{filename}"

def file_path_to_url(path: str) -> str:
    return build_upload_url(os.path.basename(path)) if path else None

# ------------ Matching helpers (heuristic) ------------
def _normalize_text(s: str) -> str:
    if not s:
        return ''
    return ''.join(ch.lower() if ch.isalnum() or ch.isspace() else ' ' for ch in s)

def _tokens(s: str) -> set:
    return {t for t in _normalize_text(s).split() if len(t) > 1}

def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b) or 1
    return inter / union

def _value_similarity(v1, v2) -> float:
    try:
        f1 = float(v1)
        f2 = float(v2)
    except Exception:
        return 0.5
    if f1 <= 0 or f2 <= 0:
        return 0.5
    ratio = min(f1, f2) / max(f1, f2)
    return max(0.0, min(1.0, ratio))

def _condition_similarity(c1: str, c2: str) -> float:
    order = ['neuf', 'excellent', 'trs bon', 'bon', 'correct', 'us']
    m = {name: idx for idx, name in enumerate(order)}
    c1 = (c1 or '').lower(); c2 = (c2 or '').lower()
    if c1 == c2 and c1:
        return 1.0
    if c1 in m and c2 in m:
        diff = abs(m[c1] - m[c2])
        return max(0.0, 1.0 - diff / (len(order)-1))
    return 0.5

def _geo_distance_km(lat1, lon1, lat2, lon2) -> float:
    try:
        from math import radians, cos, sin, asin, sqrt
        lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371
        return float(c * r)
    except Exception:
        return 9999.0

def _geo_score_km(distance_km: float) -> float:
    # 0km => 1.0, 50km => ~0.5, 200km => ~0.0 (cap)
    if distance_km <= 0:
        return 1.0
    if distance_km >= 200:
        return 0.0
    return max(0.0, 1.0 - (distance_km / 200.0))

def _pref_score(tags: set, user_prefs: set) -> float:
    if not user_prefs:
        return 0.5
    return 0.3 + 0.7 * _jaccard(tags, user_prefs)

def _success_prediction(trust_a: float, trust_b: float, completeness: float, confidence: float) -> float:
    # simple weighted mean in 0..1
    trust_a = (trust_a or 50) / 100.0
    trust_b = (trust_b or 50) / 100.0
    completeness = max(0.0, min(1.0, completeness))
    confidence = max(0.0, min(1.0, confidence))
    return max(0.0, min(1.0, 0.35*trust_a + 0.35*trust_b + 0.15*completeness + 0.15*confidence))

def _listing_completeness(l) -> float:
    filled = 0; total = 6
    for k in ['title','description','category','brand','estimated_value','main_photo']:
        if getattr(l, k, None):
            filled += 1
    return filled/total

def _extract_tags_from_listing(l) -> set:
    tags = set()
    if getattr(l, 'ai_tags', None):
        try:
            data = json.loads(l.ai_tags) if isinstance(l.ai_tags, str) else l.ai_tags
            for t in data or []:
                if isinstance(t, str):
                    tags.add(t.lower())
        except Exception:
            pass
    # also from title/description
    tags |= _tokens(getattr(l, 'title', ''))
    tags |= _tokens(getattr(l, 'description', ''))
    return tags

# Configuration
load_dotenv()  # charge les variables depuis .env si prsent
app = Flask(__name__)
app.config['SECRET_KEY'] = 'lucky-kangaroo-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///lucky_kangaroo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['JSON_AS_ASCII'] = False  # legacy flag (kept), provider below enforces UTF-8
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'

class UTF8JSONProvider(DefaultJSONProvider):
    ensure_ascii = False

# enforce UTF-8 JSON encoding globally
app.json = UTF8JSONProvider(app)
app.config['REDIS_URL'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
app.config['OPENSEARCH_URL'] = os.getenv('OPENSEARCH_URL', 'http://localhost:9200')
app.config['RATELIMIT_STORAGE_URI'] = app.config['REDIS_URL']

# Extensions
db = SQLAlchemy(app)
Migrate(app, db)
CORS(app, origins="*")

# Rate Limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "60 per hour"],
)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Serve uploaded files (development only)
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    bio = db.Column(db.Text)
    phone = db.Column(db.String(20))
    birth_date = db.Column(db.Date)
    
    # Golocalisation
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100), default='France')
    
    # Trust system
    trust_score = db.Column(db.Float, default=50.0)
    reputation_score = db.Column(db.Float, default=0.0)
    successful_exchanges = db.Column(db.Integer, default=0)
    total_exchanges = db.Column(db.Integer, default=0)
    
    # Prfrences
    preferred_language = db.Column(db.String(5), default='fr')
    preferred_currency = db.Column(db.String(3), default='EUR')
    max_distance = db.Column(db.Integer, default=50)
    email_notifications = db.Column(db.Boolean, default=True)
    push_notifications = db.Column(db.Boolean, default=True)
    
    # Scurit
    login_attempts = db.Column(db.Integer, default=0)
    account_locked = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    
    # Premium
    is_premium = db.Column(db.Boolean, default=False)
    premium_expires = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relations
    listings = db.relationship('Listing', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'bio': self.bio,
            'phone': self.phone,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'address': self.address,
            'city': self.city,
            'country': self.country,
            'trust_score': self.trust_score,
            'reputation_score': self.reputation_score,
            'successful_exchanges': self.successful_exchanges,
            'total_exchanges': self.total_exchanges,
            'preferred_language': self.preferred_language,
            'preferred_currency': self.preferred_currency,
            'max_distance': self.max_distance,
            'is_premium': self.is_premium,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ================================
# Validation Schemas (Marshmallow)
# ================================

class RegisterSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6, max=128))
    first_name = fields.Str(load_default="")
    last_name = fields.Str(load_default="")
    phone = fields.Str(load_default="")
    city = fields.Str(load_default="")
    latitude = fields.Float(load_default=None, allow_none=True)
    longitude = fields.Float(load_default=None, allow_none=True)
    address = fields.Str(load_default="")

class LoginSchema(Schema):
    username = fields.Str(load_default=None, allow_none=True)
    email = fields.Email(load_default=None, allow_none=True)
    password = fields.Str(required=True, validate=validate.Length(min=6, max=128))

class UpdateProfileSchema(Schema):
    first_name = fields.Str()
    last_name = fields.Str()
    bio = fields.Str()
    phone = fields.Str()
    city = fields.Str()
    address = fields.Str()
    latitude = fields.Float(allow_none=True)
    longitude = fields.Float(allow_none=True)
    preferred_language = fields.Str(validate=validate.Length(max=5))
    max_distance = fields.Int(validate=validate.Range(min=1, max=1000))

class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Infos de base
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    subcategory = db.Column(db.String(100))
    
    # Dtails objet
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    color = db.Column(db.String(50))
    size = db.Column(db.String(50))
    condition = db.Column(db.String(50))
    
    # Valeur
    estimated_value = db.Column(db.Float)
    min_exchange_value = db.Column(db.Float)
    max_exchange_value = db.Column(db.Float)
    currency = db.Column(db.String(3), default='EUR')
    
    # Golocalisation
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.String(255))
    max_distance = db.Column(db.Integer, default=50)
    
    # Photos
    main_photo = db.Column(db.String(255))
    photo_count = db.Column(db.Integer, default=0)
    
    # IA
    ai_tags = db.Column(db.Text)  # JSON string
    ai_confidence = db.Column(db.Float)
    ai_estimated_value = db.Column(db.Float)
    ai_keywords = db.Column(db.Text)  # JSON string
    
    # Statistiques
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    contacts = db.Column(db.Integer, default=0)
    exchange_requests = db.Column(db.Integer, default=0)
    
    # Statut
    status = db.Column(db.String(20), default='draft')  # draft, active, exchanged, expired
    is_featured = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relations
    images = db.relationship('Image', backref='listing', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'subcategory': self.subcategory,
            'brand': self.brand,
            'model': self.model,
            'color': self.color,
            'condition': self.condition,
            'estimated_value': self.estimated_value,
            'currency': self.currency,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'address': self.address,
            'max_distance': self.max_distance,
            'main_photo': self.main_photo,
            'photo_count': self.photo_count,
            'ai_tags': json.loads(self.ai_tags) if self.ai_tags else [],
            'ai_confidence': self.ai_confidence,
            'ai_estimated_value': self.ai_estimated_value,
            'views': self.views,
            'likes': self.likes,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'owner': self.owner.to_dict() if self.owner else None
        }

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    
    # Fichier
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255))
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    
    # Mtadonnes
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    format = db.Column(db.String(10))
    
    # IA
    ai_analysis = db.Column(db.Text)  # JSON string
    ai_tags = db.Column(db.Text)  # JSON string
    detected_objects = db.Column(db.Text)  # JSON string
    suggested_category = db.Column(db.String(100))
    
    # Statut
    is_main = db.Column(db.Boolean, default=False)
    is_processed = db.Column(db.Boolean, default=False)
    moderation_status = db.Column(db.String(20), default='pending')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'width': self.width,
            'height': self.height,
            'ai_analysis': json.loads(self.ai_analysis) if self.ai_analysis else None,
            'ai_tags': json.loads(self.ai_tags) if self.ai_tags else [],
            'is_main': self.is_main,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# JWT Token decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token manquant'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(uuid=data['uuid']).first()
            if not current_user:
                return jsonify({'message': 'Token invalide'}), 401
        except:
            return jsonify({'message': 'Token invalide'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# Utility functions
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    if not all([lat1, lon1, lat2, lon2]):
        return None
    
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def simulate_ai_analysis(filename):
    """Simulate AI analysis of uploaded image"""
    objects = ['iPhone 14', 'MacBook Pro', 'Vlo lectrique', 'Appareil photo Canon', 
               'Montre Apple', 'Casque Bose', 'Tablette iPad', 'Console PlayStation',
               'Guitare lectrique', 'Livre de cuisine', 'Sac  main Louis Vuitton']
    
    categories = ['lectronique', 'Informatique', 'Sport', 'Photo', 'Audio', 'Gaming', 
                  'Musique', 'Livres', 'Mode']
    
    tags = ['excellent tat', 'comme neuf', 'peu utilis', 'garantie', 'accessoires inclus', 
            'bote d\'origine', 'facture disponible', 'sans rayures']
    
    random_object = random.choice(objects)
    random_category = random.choice(categories)
    random_tags = random.sample(tags, 3)
    confidence = random.randint(85, 98)
    estimated_value = random.randint(50, 1200)
    
    return {
        'object': random_object,
        'category': random_category,
        'confidence': confidence,
        'estimated_value': estimated_value,
        'tags': random_tags,
        'condition': 'Trs bon tat',
        'brand': random_object.split(' ')[0] if ' ' in random_object else 'Gnrique'
    }

# Image processing helper
def generate_image_variants(src_path, remove_bg=False):
    """Generate large and thumbnail variants; optionally remove background.
    Returns dict with file paths keyed by variant name.
    """
    variants = {}
    try:
        if not HAS_PIL:
            return variants

        base_dir = os.path.dirname(src_path)
        base_name = os.path.splitext(os.path.basename(src_path))[0]

        # Open source image
        with PILImage.open(src_path) as im:
            # Ensure RGB for JPEG
            if im.mode not in ("RGB", "RGBA"):
                im = im.convert("RGB")

            # Large variant (max 1280)
            lg = im.copy()
            lg.thumbnail((1280, 1280), PILImage.LANCZOS)
            lg_path = os.path.join(base_dir, f"{base_name}_lg.jpg")
            lg.save(lg_path, format="JPEG", quality=85, optimize=True)
            variants['large'] = lg_path

            # Thumbnail (max 320)
            sm = im.copy()
            sm.thumbnail((320, 320), PILImage.LANCZOS)
            sm_path = os.path.join(base_dir, f"{base_name}_sm.jpg")
            sm.save(sm_path, format="JPEG", quality=80, optimize=True)
            variants['thumb'] = sm_path

            # Optional background removal (PNG)
            if remove_bg and HAS_REMBG:
                buf = BytesIO()
                # Work from RGBA for better cutout
                cut_src = im.convert("RGBA") if im.mode != "RGBA" else im
                cut_src.save(buf, format="PNG")
                cut_bytes = buf.getvalue()
                cutout = rembg_remove(cut_bytes)
                cut_path = os.path.join(base_dir, f"{base_name}_cut.png")
                with open(cut_path, 'wb') as f:
                    f.write(cutout)
                variants['cutout'] = cut_path
    except Exception:
        # Fail-safe: return whatever we managed to produce
        pass

    return variants

# Routes - Authentication
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json() or {}
        try:
            data = RegisterSchema().load(data)
        except ValidationError as ve:
            return jsonify({'error': 'Validation', 'details': ve.messages}), 400
        
        # Check if user exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Nom d\'utilisateur dj pris'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email dj utilis'}), 400
        
        # Create user
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            phone=data.get('phone', ''),
            city=data.get('city', ''),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            address=data.get('address', '')
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = jwt.encode({
            'uuid': user.uuid,
            'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=30)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'Utilisateur cr avec succs',
            'token': token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==========================================
# MATCHING IA (heuristique)
# ==========================================

@app.route('/api/matching/score', methods=['POST'])
def matching_score():
    """Calcule un score de compatibilit (0-100) entre deux annonces.
    Body JSON peut contenir listing_a_uuid, listing_b_uuid, ou des objets inline.
    """
    try:
        data = request.get_json(force=True) or {}
        la_uuid = data.get('listing_a_uuid')
        lb_uuid = data.get('listing_b_uuid')
        la_obj = data.get('listing_a')
        lb_obj = data.get('listing_b')

        def load_listing(obj, uuid_key):
            if obj:
                # minimal object-like to compute
                class X: pass
                x = X();
                for k,v in (obj or {}).items():
                    setattr(x, k, v)
                return x
            if uuid_key:
                return Listing.query.filter_by(uuid=uuid_key).first()
            return None

        la = load_listing(la_obj, la_uuid)
        lb = load_listing(lb_obj, lb_uuid)
        if not la or not lb:
            return jsonify({'error': 'Annonces introuvables ou non fournies'}), 400

        # Semantic analysis
        def safe_tokens(text):
            return _tokens(str(text or ''))
            
        def safe_extract_tags(listing):
            try:
                return _extract_tags_from_listing(listing)
            except Exception:
                return set()
                
        ta = safe_tokens(getattr(la, 'title', '')) | safe_tokens(getattr(la, 'description', ''))
        tb = safe_tokens(getattr(lb, 'title', '')) | safe_tokens(getattr(lb, 'description', ''))
        sa = safe_extract_tags(la)
        sb = safe_extract_tags(lb)
        semantic = 0.6 * _jaccard(ta, tb) + 0.4 * _jaccard(sa, sb)

        # Compatibility
        cat_score = 1.0 if getattr(la, 'category', '').lower() == getattr(lb, 'category', '').lower() and getattr(la,'category',None) else 0.4
        subcat_score = 1.0 if getattr(la, 'subcategory', '').lower() == getattr(lb, 'subcategory', '').lower() and getattr(la,'subcategory',None) else 0.5
        brand_score = 1.0 if getattr(la, 'brand', '').lower() == getattr(lb, 'brand', '').lower() and getattr(la,'brand',None) else 0.6
        cond_score = _condition_similarity(getattr(la,'condition', ''), getattr(lb,'condition',''))
        value_score = _value_similarity(getattr(la,'estimated_value', getattr(la,'ai_estimated_value',0)), getattr(lb,'estimated_value', getattr(lb,'ai_estimated_value',0)))
        compatibility = 0.25*cat_score + 0.15*subcat_score + 0.2*brand_score + 0.2*cond_score + 0.2*value_score

        # Geo
        dkm = _geo_distance_km(getattr(la,'latitude',None), getattr(la,'longitude',None), getattr(lb,'latitude',None), getattr(lb,'longitude',None))
        geo = _geo_score_km(dkm)

        # Preferences (if provided)
        user_prefs = set([t.lower() for t in (data.get('user_prefs') or []) if isinstance(t, str)])
        prefs_score = _pref_score(sa | ta, user_prefs)

        # Success prediction
        trust_a = getattr(User.query.get(getattr(la,'user_id',None)) or User(), 'trust_score', 50)
        trust_b = getattr(User.query.get(getattr(lb,'user_id',None)) or User(), 'trust_score', 50)
        completeness = 0.5*(_listing_completeness(la) + _listing_completeness(lb))
        confidence = ((getattr(la,'ai_confidence',70) or 70) + (getattr(lb,'ai_confidence',70) or 70)) / 200.0
        success = _success_prediction(trust_a, trust_b, completeness, confidence)

        # Calculate final score with weights
        weights = {
            'semantic': 0.32,
            'compatibility': 0.25,
            'geo': 0.18,
            'prefs': 0.12,
            'success': 0.13
        }
        
        # Calculate weighted sum
        score = sum([
            weights['semantic'] * semantic,
            weights['compatibility'] * compatibility,
            weights['geo'] * geo,
            weights['prefs'] * prefs_score,
            weights['success'] * success
        ]) * 100.0

        return jsonify({
            'success': True,
            'score_compatibilite': round(score, 1),
            'details': {
                'semantic': round(semantic*100,1),
                'compatibility': round(compatibility*100,1),
                'geo': {'distance_km': None if dkm==9999.0 else round(dkm,1), 'score': round(geo*100,1)},
                'preferences': round(prefs_score*100,1),
                'success_prediction': round(success*100,1)
            },
            'suggestions_amelioration': _build_suggestions(la, lb)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _build_suggestions(la, lb):
    sugs = []
    for l in [la, lb]:
        if not getattr(l,'main_photo',None): sugs.append("Ajouter une photo principale de qualit")
        if not getattr(l,'description',None) or len(getattr(l,'description','')) < 80: sugs.append("Allonger la description ( 80 caractres)")
        if not getattr(l,'brand',None): sugs.append("Renseigner la marque si connue")
        if not getattr(l,'estimated_value',None) and not getattr(l,'ai_estimated_value',None): sugs.append("Indiquer une valeur estime")
        if not getattr(l,'category',None): sugs.append("Choisir une catgorie prcise")
    # deduplicate
    seen = set(); out=[]
    for s in sugs:
        if s not in seen:
            seen.add(s); out.append(s)
    return out

@app.route('/api/matching/recommendations', methods=['GET'])
@token_required
def matching_recommendations(current_user):
    """Retourne des recommandations d'annonces pour l'utilisateur courant."""
    try:
        listings = Listing.query.filter(Listing.status=='active').order_by(Listing.created_at.desc()).limit(200).all()
        # derive user pref tags from last interactions or profile fields
        user_tags = set(_tokens(getattr(current_user,'city','')))  # placeholder
        scored = []
        for l in listings:
            # Reference as if user searched items similar to their preferences
            ta = _tokens(getattr(l,'title','')) | _tokens(getattr(l,'description',''))
            sa = _extract_tags_from_listing(l)
            semantic = 0.6*_jaccard(ta, user_tags) + 0.4*_jaccard(sa, user_tags)
            # geo
            dkm = _geo_distance_km(current_user.latitude, current_user.longitude, getattr(l,'latitude',None), getattr(l,'longitude',None))
            geo = _geo_score_km(dkm)
            # trust and completeness
            trust = getattr(User.query.get(getattr(l,'user_id',None)) or User(), 'trust_score', 50)
            success = _success_prediction(trust, current_user.trust_score or 50, _listing_completeness(l), (getattr(l,'ai_confidence',70) or 70)/100.0)
            score = (0.45*semantic + 0.3*geo + 0.25*success) * 100.0
            scored.append({
                'listing_uuid': getattr(l,'uuid',None),
                'title': getattr(l,'title',None),
                'category': getattr(l,'category',None),
                'brand': getattr(l,'brand',None),
                'distance_km': None if dkm==9999.0 else round(dkm,1),
                'score': round(score,1),
                'main_photo': getattr(l,'main_photo',None)
            })
        scored.sort(key=lambda x: x['score'], reverse=True)
        return jsonify({'success': True, 'recommendations': scored[:20]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/matching/diagnostic', methods=['POST'])
def matching_diagnostic():
    """Analyse une annonce et propose des amliorations."""
    try:
        data = request.get_json(force=True) or {}
        class X: pass
        l = X();
        for k,v in (data.get('listing') or {}).items(): setattr(l,k,v)
        sugs = _build_suggestions(l, l)
        issues = []
        if getattr(l,'estimated_value',None) and isinstance(l.estimated_value,(int,float)) and l.estimated_value < 10:
            issues.append('Valeur trs faible, vrifier le march')
        return jsonify({'success': True, 'suggestions': sugs, 'issues': issues})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==========================================
# IA simple: Lookup via Google Images/Lens
# ==========================================
@app.route('/api/ai/lookup', methods=['POST'])
def ai_lookup():
    """
    Accept a single image (multipart key 'file' or 'image' or 'files').
    Save it, build a public URL to it, and return a Google Images search URL.
    Also return naive 'similar' local listings filtered by category/brand/city if available.
    """
    try:
        # Get file from multiple possible keys for convenience
        file = request.files.get('file') or request.files.get('image')
        if not file:
            # fallback to first from 'files'
            files = request.files.getlist('files')
            file = files[0] if files else None
        if not file:
            return jsonify({'error': 'Aucun fichier reu'}), 400

        filename = secure_filename(file.filename)
        if not filename:
            filename = f"upload_{uuid.uuid4().hex}.jpg"
        save_name = f"{uuid.uuid4()}_{filename}"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], save_name)
        file.save(save_path)

        # Process variants (optional bg removal via form flag)
        remove_bg_flag = bool_flag(request.form.get('remove_bg'))
        vfiles = generate_image_variants(save_path, remove_bg=remove_bg_flag)

        # Public URL of uploaded file (dev): http://<host>/uploads/<filename>
        image_url = build_upload_url(save_name)
        variant_urls = {k: file_path_to_url(p) for k, p in vfiles.items()}

        # Build Google Images search-by-image URL (legacy endpoint)
        # Works in many regions; alternative is lens upload in browser.
        from urllib.parse import quote_plus
        google_img_url = f"https://www.google.com/searchbyimage?image_url={quote_plus(image_url)}&encoded_image=&image_content=&filename=&hl=fr"
        lens_url = "https://lens.google.com/upload?ep=ccm"  # requires browser interaction

        # Try to infer category/brand from last created listing for demo (very naive)
        # Or simply return top N recent listings as 'similar'
        listings = Listing.query.order_by(Listing.created_at.desc()).limit(50).all()
        similar = []
        for l in listings:
            similar.append({
                'uuid': getattr(l, 'uuid', None),
                'title': getattr(l, 'title', None),
                'brand': getattr(l, 'brand', None),
                'category': getattr(l, 'category', None),
                # Use address if present; some schemas may not have 'city'
                'address': getattr(l, 'address', None),
                'main_photo': getattr(l, 'main_photo', None),
                'ai_estimated_value': getattr(l, 'ai_estimated_value', None),
            })
        # Keep top 10 for response brevity
        similar = similar[:10]

        return jsonify({
            'message': 'Analyse image simple effectue',
            'uploaded_image_url': image_url,
            'google_images_search_url': google_img_url,
            'google_lens_url': lens_url,
            'variants': variant_urls,
            'similar_listings_local': similar
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/analyze', methods=['POST'])
def ai_analyze():
    """
    Accept a single image (multipart key 'file' or 'image' or first of 'files').
    Save it, generate resized variants and optional background removal, and
    return heuristic AI analysis (simulated) with structured metadata.
    Optional form field: remove_bg = 1/true/yes
    """
    try:
        file = request.files.get('file') or request.files.get('image')
        if not file:
            files = request.files.getlist('files')
            file = files[0] if files else None
        if not file:
            return jsonify({'error': 'Aucun fichier reu'}), 400

        filename = secure_filename(file.filename) or f"upload_{uuid.uuid4().hex}.jpg"
        save_name = f"{uuid.uuid4()}_{filename}"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], save_name)
        file.save(save_path)

        # Flags and processing
        remove_bg_flag = bool_flag(request.form.get('remove_bg'))
        vfiles = generate_image_variants(save_path, remove_bg=remove_bg_flag)

        # Heuristic AI
        ai = simulate_ai_analysis(filename)

        # URLs
        uploaded_url = build_upload_url(save_name)
        variant_urls = {k: file_path_to_url(p) for k, p in vfiles.items()}

        return jsonify({
            'message': 'Analyse IA effectue',
            'uploaded_image_url': uploaded_url,
            'variants': variant_urls,
            'analysis': ai,
            'options': {
                'background_removed': bool('cutout' in vfiles),
                'pil_available': HAS_PIL,
                'rembg_available': HAS_REMBG
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    try:
        data = request.get_json() or {}
        try:
            data = LoginSchema().load(data)
        except ValidationError as ve:
            return jsonify({'error': 'Validation', 'details': ve.messages}), 400
        
        # Support login with either username OR email
        identifier_username = data.get('username')
        identifier_email = data.get('email')
        password = data.get('password')

        if not password or not (identifier_username or identifier_email):
            return jsonify({'error': 'Donnes manquantes'}), 400

        user = None
        if identifier_username:
            user = User.query.filter_by(username=identifier_username).first()
        elif identifier_email:
            user = User.query.filter_by(email=identifier_email).first()
        
        if not user or not check_password_hash(user.password_hash, data['password']):
            return jsonify({'error': 'Identifiants invalides'}), 401
        
        # Update last login
        user.last_login = datetime.datetime.now(datetime.UTC)
        user.login_attempts = 0
        db.session.commit()
        
        # Generate token
        token = jwt.encode({
            'uuid': user.uuid,
            'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=30)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'Connexion russie',
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/refresh', methods=['POST'])
@token_required
def refresh_token(current_user):
    """Issue a new JWT using a valid token (simple refresh)."""
    try:
        new_token = jwt.encode({
            'uuid': current_user.uuid,
            'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=30)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': new_token}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Routes - User Profile
@app.route('/api/user/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({'user': current_user.to_dict()}), 200

@app.route('/api/user/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    try:
        data = request.get_json() or {}
        try:
            data = UpdateProfileSchema().load(data, partial=True)
        except ValidationError as ve:
            return jsonify({'error': 'Validation', 'details': ve.messages}), 400
        
        # Update fields
        for field in ['first_name', 'last_name', 'bio', 'phone', 'city', 'address', 
                     'latitude', 'longitude', 'preferred_language', 'max_distance']:
            if field in data:
                setattr(current_user, field, data[field])
        
        current_user.updated_at = datetime.datetime.now(datetime.UTC)
        db.session.commit()
        
        return jsonify({
            'message': 'Profil mis  jour',
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Routes - Listings
@app.route('/api/listings', methods=['GET'])
def get_listings():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category')
        search = request.args.get('search')
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        max_distance = request.args.get('max_distance', 50, type=int)
        
        query = Listing.query.filter_by(status='active')
        
        if category:
            query = query.filter_by(category=category)
        
        if search:
            query = query.filter(Listing.title.contains(search))
        
        listings = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Calculate distances if location provided
        results = []
        for listing in listings.items:
            listing_dict = listing.to_dict()
            if lat and lon and listing.latitude and listing.longitude:
                distance = calculate_distance(lat, lon, listing.latitude, listing.longitude)
                if distance and distance <= max_distance:
                    listing_dict['distance'] = round(distance, 1)
                    results.append(listing_dict)
            else:
                results.append(listing_dict)
        
        return jsonify({
            'listings': results,
            'total': listings.total,
            'pages': listings.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/listings', methods=['POST'])
@token_required
def create_listing(current_user):
    try:
        data = request.get_json()
        
        if not data.get('title'):
            return jsonify({'error': 'Titre requis'}), 400
        
        listing = Listing(
            user_id=current_user.id,
            title=data['title'],
            description=data.get('description', ''),
            category=data.get('category'),
            subcategory=data.get('subcategory'),
            brand=data.get('brand'),
            model=data.get('model'),
            color=data.get('color'),
            condition=data.get('condition'),
            estimated_value=data.get('estimated_value'),
            latitude=data.get('latitude') or current_user.latitude,
            longitude=data.get('longitude') or current_user.longitude,
            address=data.get('address') or current_user.address,
            max_distance=data.get('max_distance', 50),
            status='draft'
        )
        
        db.session.add(listing)
        db.session.commit()
        
        return jsonify({
            'message': 'Annonce cre',
            'listing': listing.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/listings/<listing_uuid>', methods=['GET'])
def get_listing(listing_uuid):
    try:
        listing = Listing.query.filter_by(uuid=listing_uuid).first()
        if not listing:
            return jsonify({'error': 'Annonce non trouve'}), 404
        
        # Increment views
        listing.views += 1
        db.session.commit()
        
        return jsonify({'listing': listing.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Routes - Images
@app.route('/api/listings/<listing_uuid>/images', methods=['POST'])
@token_required
def upload_images(current_user, listing_uuid):
    try:
        listing = Listing.query.filter_by(uuid=listing_uuid, user_id=current_user.id).first()
        if not listing:
            return jsonify({'error': 'Annonce non trouve'}), 404
        
        if 'files' not in request.files:
            return jsonify({'error': 'Aucun fichier'}), 400
        
        files = request.files.getlist('files')
        uploaded_images = []
        
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                
                file.save(file_path)

                # Generate variants and optional background removal if requested
                remove_bg_flag = bool_flag(request.form.get('remove_bg'))
                vfiles = generate_image_variants(file_path, remove_bg=remove_bg_flag)
                
                # Simulate AI analysis
                ai_analysis = simulate_ai_analysis(filename)
                
                # Create image record
                image = Image(
                    listing_id=listing.id,
                    filename=unique_filename,
                    original_filename=filename,
                    file_path=file_path,
                    file_size=os.path.getsize(file_path),
                    mime_type=file.content_type,
                    ai_analysis=json.dumps(ai_analysis),
                    ai_tags=json.dumps(ai_analysis['tags']),
                    suggested_category=ai_analysis['category'],
                    is_main=(listing.photo_count == 0),  # First image is main
                    is_processed=True
                )
                
                db.session.add(image)
                listing.photo_count += 1
                
                if image.is_main:
                    listing.main_photo = unique_filename
                    listing.ai_estimated_value = ai_analysis['estimated_value']
                    listing.ai_tags = json.dumps(ai_analysis['tags'])
                    listing.ai_confidence = ai_analysis['confidence']
                
                # Build public URLs
                image_dict = image.to_dict()
                image_dict['url'] = build_upload_url(unique_filename)
                image_dict['variants'] = {k: file_path_to_url(p) for k, p in vfiles.items()}
                uploaded_images.append(image_dict)
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(uploaded_images)} image(s) uploade(s)',
            'images': uploaded_images
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/listings/<listing_uuid>/images', methods=['GET'])
def get_listing_images(listing_uuid):
    try:
        listing = Listing.query.filter_by(uuid=listing_uuid).first()
        if not listing:
            return jsonify({'error': 'Annonce non trouve'}), 404
        
        images = [img.to_dict() for img in listing.images]
        
        return jsonify({'images': images}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Routes - Geolocation
@app.route('/api/geo/nearby', methods=['GET'])
def get_nearby_listings():
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        radius = request.args.get('radius', 50, type=int)
        
        if not lat or not lon:
            return jsonify({'error': 'Coordonnes requises'}), 400
        
        listings = Listing.query.filter_by(status='active').all()
        nearby_listings = []
        
        for listing in listings:
            if listing.latitude and listing.longitude:
                distance = calculate_distance(lat, lon, listing.latitude, listing.longitude)
                if distance and distance <= radius:
                    listing_dict = listing.to_dict()
                    listing_dict['distance'] = round(distance, 1)
                    nearby_listings.append(listing_dict)
        
        # Sort by distance
        nearby_listings.sort(key=lambda x: x['distance'])
        
        return jsonify({
            'listings': nearby_listings,
            'count': len(nearby_listings)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/geo/cities', methods=['GET'])
def get_cities():
    cities = [
        {'name': 'Paris', 'lat': 48.8566, 'lon': 2.3522},
        {'name': 'Lyon', 'lat': 45.7640, 'lon': 4.8357},
        {'name': 'Marseille', 'lat': 43.2965, 'lon': 5.3698},
        {'name': 'Toulouse', 'lat': 43.6047, 'lon': 1.4442},
        {'name': 'Nice', 'lat': 43.7102, 'lon': 7.2620},
        {'name': 'Nantes', 'lat': 47.2184, 'lon': -1.5536},
        {'name': 'Strasbourg', 'lat': 48.5734, 'lon': 7.7521},
        {'name': 'Montpellier', 'lat': 43.6110, 'lon': 3.8767},
        {'name': 'Bordeaux', 'lat': 44.8378, 'lon': -0.5792},
        {'name': 'Lille', 'lat': 50.6292, 'lon': 3.0573}
    ]
    
    return jsonify({'cities': cities}), 200

# Routes - Statistics
@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        total_users = User.query.count()
        total_listings = Listing.query.count()
        active_listings = Listing.query.filter_by(status='active').count()
        total_images = Image.query.count()
        
        return jsonify({
            'total_users': total_users,
            'total_listings': total_listings,
            'active_listings': active_listings,
            'total_images': total_images,
            'success_rate': 98.5,
            'avg_response_time': '2.3 heures'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Routes - Health Check
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Lucky Kangaroo Backend Intgr',
        'version': '2.0.0',
        'timestamp': datetime.datetime.now(datetime.UTC).isoformat(),
        'features': [
            'Authentification JWT',
            'Gestion utilisateurs',
            'Annonces avec photos',
            'Golocalisation',
            'Analyse IA des images',
            'Recherche proximit',
            'Statistiques temps rel'
        ]
    }), 200

# (Duplicate upload route removed; primary is defined earlier as '/uploads/<path:filename>')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint non trouv'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erreur serveur interne'}), 500

# Root route quality-of-life
@app.route('/')
def root_redirect():
    return redirect('/api/health', code=302)

# Initialize database
def create_tables():
    db.create_all()
    
    # Create demo data if no users exist
    if User.query.count() == 0:
        create_demo_data()

def create_demo_data():
    """Create demo users and listings"""
    try:
        # Demo users
        users_data = [
            {
                'username': 'alice_paris',
                'email': 'alice@example.com',
                'password': 'password123',
                'first_name': 'Alice',
                'last_name': 'Martin',
                'city': 'Paris',
                'latitude': 48.8566,
                'longitude': 2.3522,
                'trust_score': 95.0,
                'successful_exchanges': 12
            },
            {
                'username': 'bob_lyon',
                'email': 'bob@example.com',
                'password': 'password123',
                'first_name': 'Bob',
                'last_name': 'Dubois',
                'city': 'Lyon',
                'latitude': 45.7640,
                'longitude': 4.8357,
                'trust_score': 88.0,
                'successful_exchanges': 8
            },
            {
                'username': 'claire_marseille',
                'email': 'claire@example.com',
                'password': 'password123',
                'first_name': 'Claire',
                'last_name': 'Moreau',
                'city': 'Marseille',
                'latitude': 43.2965,
                'longitude': 5.3698,
                'trust_score': 92.0,
                'successful_exchanges': 15
            }
        ]
        
        demo_users = []
        for user_data in users_data:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password']),
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                city=user_data['city'],
                latitude=user_data['latitude'],
                longitude=user_data['longitude'],
                trust_score=user_data['trust_score'],
                successful_exchanges=user_data['successful_exchanges']
            )
            db.session.add(user)
            demo_users.append(user)
        
        db.session.commit()
        
        # Demo listings
        listings_data = [
            {
                'title': 'iPhone 14 Pro Max 256GB',
                'description': 'iPhone en excellent tat, trs peu utilis. Bote et accessoires inclus.',
                'category': 'lectronique',
                'subcategory': 'Smartphones',
                'brand': 'Apple',
                'condition': 'Excellent',
                'estimated_value': 900,
                'user_index': 0
            },
            {
                'title': 'MacBook Pro M2 13 pouces',
                'description': 'MacBook Pro parfait pour le travail et les tudes. Garantie Apple Care.',
                'category': 'Informatique',
                'subcategory': 'Ordinateurs portables',
                'brand': 'Apple',
                'condition': 'Trs bon',
                'estimated_value': 1200,
                'user_index': 1
            },
            {
                'title': 'Vlo lectrique Decathlon',
                'description': 'Vlo lectrique peu utilis, parfait pour les trajets urbains.',
                'category': 'Sport',
                'subcategory': 'Vlos',
                'brand': 'Decathlon',
                'condition': 'Bon',
                'estimated_value': 800,
                'user_index': 2
            }
        ]
        
        for listing_data in listings_data:
            user = demo_users[listing_data['user_index']]
            listing = Listing(
                user_id=user.id,
                title=listing_data['title'],
                description=listing_data['description'],
                category=listing_data['category'],
                subcategory=listing_data['subcategory'],
                brand=listing_data['brand'],
                condition=listing_data['condition'],
                estimated_value=listing_data['estimated_value'],
                latitude=user.latitude,
                longitude=user.longitude,
                address=user.city,
                status='active',
                ai_confidence=random.randint(85, 98),
                ai_estimated_value=listing_data['estimated_value'] + random.randint(-100, 100)
            )
            db.session.add(listing)
        
        db.session.commit()
        print("Donnes de dmonstration cres avec succs!")
        
    except Exception as e:
        print(f"Erreur lors de la cration des donnes de dmo: {e}")

if __name__ == '__main__':
    with app.app_context():
        create_tables()
    
    print(" Lucky Kangaroo Backend Intgr dmarr!")
    print(" Endpoints disponibles:")
    print("   - POST /api/auth/register")
    print("   - POST /api/auth/login")
    print("   - POST /api/auth/refresh")
    print("   - GET  /api/user/profile")
    print("   - GET  /api/listings")
    print("   - POST /api/listings")
    print("   - POST /api/listings/<uuid>/images")
    print("   - GET  /api/geo/nearby")
    print("   - GET  /api/stats")
    print("   - GET  /api/health")
    print("   - GET  /")
    print("   - POST /api/ai/lookup")
    print("   - POST /api/ai/analyze")
    print("   - POST /api/matching/score")
    print("   - GET  /api/matching/recommendations")
    print("   - POST /api/matching/diagnostic")
    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5006)), debug=True)



# ==========================================
# ENDPOINTS GOLOCALISATION
# ==========================================

@app.route('/api/geo/distance', methods=['GET'])
def geo_distance_endpoint():
    """Calcul de distance entre deux points"""
    try:
        lat1 = float(request.args.get('lat1'))
        lon1 = float(request.args.get('lon1'))
        lat2 = float(request.args.get('lat2'))
        lon2 = float(request.args.get('lon2'))
        
        # Calcul de distance avec formule Haversine
        from math import radians, cos, sin, asin, sqrt
        
        # Conversion en radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Formule Haversine
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Rayon de la Terre en km
        distance = c * r
        
        return jsonify({
            'success': True,
            'distance_km': round(distance, 2),
            'distance_miles': round(distance * 0.621371, 2),
            'coordinates': {
                'point1': {'lat': lat1, 'lon': lon1},
                'point2': {'lat': lat2, 'lon': lon2}
            },
            'calculation_method': 'Haversine formula'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors du calcul de distance'
        }), 400

# ==========================================
# CATEGORIES (inspires d'Anibis & Craigslist)
# ==========================================

CATEGORIES = [
    {
        'name': 'lectronique',
        'slug': 'electronics',
        'subcategories': [
            'Smartphones', 'Tablettes', 'Ordinateurs portables', 'PC de bureau',
            'Accessoires informatiques', 'Consoles & Jeux vido', 'TV & Home Cinema',
            'Audio & Hi-Fi', 'Drones', 'Wearables', 'Appareils photo', 'Objets connects'
        ]
    },
    {
        'name': 'Informatique',
        'slug': 'computers',
        'subcategories': [
            'Laptops', 'Desktops', 'Moniteurs', 'Composants PC', 'Imprimantes & Scanners',
            'Stockage & Rseaux', 'Logiciels', 'Serveurs'
        ]
    },
    {
        'name': 'Maison & Jardin',
        'slug': 'home-garden',
        'subcategories': [
            'Meubles', 'Dcoration', 'Electromnager', 'Bricolage', 'Jardinage',
            'clairage', 'Rangement'
        ]
    },
    {
        'name': 'Vhicules',
        'slug': 'vehicles',
        'subcategories': [
            'Voitures', 'Motos', 'Vlos', 'Trottinettes', 'Utilitaires', 'quipement & pices'
        ]
    },
    {
        'name': 'Mode & Accessoires',
        'slug': 'fashion',
        'subcategories': [
            'Vtements', 'Chaussures', 'Sacs', 'Bijoux & Montres', 'Luxe', 'Accessoires'
        ]
    },
    {
        'name': 'Sport & Loisirs',
        'slug': 'sports',
        'subcategories': [
            'Vlos', 'Fitness & Musculation', 'Sports de plein air', 'Sports dhiver',
            'Camping & Randonne', 'Sports dquipe', 'Instruments de musique'
        ]
    },
    {
        'name': 'Livres & Mdias',
        'slug': 'books-media',
        'subcategories': [
            'Livres', 'BD & Mangas', 'Films & Sries', 'Musique', 'Jeux vido & rtro'
        ]
    },
    {
        'name': 'Art & Collection',
        'slug': 'art-collectibles',
        'subcategories': [
            'Art', 'Objets de collection', 'Antiquits', 'Design & Vintage'
        ]
    },
    {
        'name': 'Enfants & Bbs',
        'slug': 'kids-baby',
        'subcategories': [
            'Vtements', 'Jouets', 'Puriculture', 'Chambres & Mobilier'
        ]
    },
    {
        'name': 'Services',
        'slug': 'services',
        'subcategories': [
            'Cours & Formations', 'Rparations', 'Dmnagement', 'Jardinage', 'IT & Web', 'Autres services'
        ]
    },
    {
        'name': 'Animaux',
        'slug': 'pets',
        'subcategories': [
            'Chiens', 'Chats', 'Poissons', 'Oiseaux', 'Rongeurs', 'Accessoires & nourriture'
        ]
    },
    {
        'name': 'Emploi',
        'slug': 'jobs',
        'subcategories': [
            'Temps plein', 'Temps partiel', 'Freelance', 'Stages', 'IT', 'Commerce', 'Sant', 'Autres'
        ]
    },
    {
        'name': 'Immobilier',
        'slug': 'real-estate',
        'subcategories': [
            'Appartements', 'Maisons', 'Colocations', 'Locations vacances', 'Parkings & Garages'
        ]
    },
    {
        'name': 'Autres',
        'slug': 'others',
        'subcategories': [
            'Divers', ' donner', 'vnements', 'Matriel professionnel'
        ]
    }
]

@app.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify({'categories': CATEGORIES}), 200

# ==========================================
# ENDPOINTS ANALYSE IA
# ==========================================

@app.route('/api/ai/analyze-image', methods=['POST'])
def analyze_image():
    """Analyse d'image par IA (simulation raliste)"""
    try:
        data = request.get_json()
        image_url = data.get('image_url', '')
        filename = data.get('filename', '')
        
        # Simulation d'analyse IA base sur le nom du fichier
        detected_objects = {
            'iphone': {
                'object': 'iPhone 14 Pro',
                'category': 'lectronique',
                'subcategory': 'Smartphones',
                'brand': 'Apple',
                'condition': 'Excellent',
                'estimated_value': random.randint(800, 1200),
                'confidence': random.randint(92, 98),
                'tags': ['smartphone', 'apple', 'premium', 'excellent tat']
            },
            'macbook': {
                'object': 'MacBook Pro M2',
                'category': 'Informatique',
                'subcategory': 'Ordinateurs portables',
                'brand': 'Apple',
                'condition': 'Trs bon',
                'estimated_value': random.randint(1500, 2500),
                'confidence': random.randint(88, 96),
                'tags': ['ordinateur', 'apple', 'professionnel', 'performant']
            },
            'velo': {
                'object': 'Vlo lectrique',
                'category': 'Sport',
                'subcategory': 'Vlos',
                'brand': 'Decathlon',
                'condition': 'Bon',
                'estimated_value': random.randint(600, 1000),
                'confidence': random.randint(85, 93),
                'tags': ['vlo', 'lectrique', 'transport', 'cologique']
            },
            'camera': {
                'object': 'Canon EOS R5',
                'category': 'Photo',
                'subcategory': 'Appareils photo',
                'brand': 'Canon',
                'condition': 'Excellent',
                'estimated_value': random.randint(2000, 3000),
                'confidence': random.randint(90, 97),
                'tags': ['appareil photo', 'professionnel', 'canon', 'haute qualit']
            }
        }
        
        # Dtection base sur le nom du fichier
        detected_object = None
        for key, obj_data in detected_objects.items():
            if key.lower() in filename.lower() or key.lower() in image_url.lower():
                detected_object = obj_data
                break
        
        # Objet par dfaut si rien n'est dtect
        if not detected_object:
            detected_object = {
                'object': 'Objet non identifi',
                'category': 'Divers',
                'subcategory': 'Autres',
                'brand': 'Inconnue',
                'condition': ' valuer',
                'estimated_value': random.randint(50, 200),
                'confidence': random.randint(60, 80),
                'tags': ['objet', 'divers', ' identifier']
            }
        
        return jsonify({
            'success': True,
            'analysis': {
                'detected_object': detected_object['object'],
                'category': detected_object['category'],
                'subcategory': detected_object['subcategory'],
                'brand': detected_object['brand'],
                'condition': detected_object['condition'],
                'estimated_value': detected_object['estimated_value'],
                'confidence': detected_object['confidence'],
                'tags': detected_object['tags'],
                'processing_time': f"{random.randint(200, 800)}ms",
                'ai_model': 'Lucky Kangaroo Vision v2.0',
                'analysis_timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
            },
            'metadata': {
                'image_url': image_url,
                'filename': filename,
                'analysis_id': str(uuid.uuid4())
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de l\'analyse IA'
        }), 400

