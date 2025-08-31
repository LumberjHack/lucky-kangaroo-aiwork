"""
Lucky Kangaroo - Backend Package

This package contains the backend implementation for the Lucky Kangaroo application,
including the Flask application factory, database models, API routes, and other core functionality.
"""

import os
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_restx import Api
from flask_principal import Principal
from opensearchpy import OpenSearch
from celery import Celery
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
jwt = JWTManager()
mail = Mail()
bcrypt = Bcrypt()
cors = CORS()
principal = Principal()
socketio = SocketIO()
api = Api(version='1.0', title='Lucky Kangaroo API',
          description='API for Lucky Kangaroo - The Ultimate Exchange Platform')

# Initialize Celery without config
celery = Celery()

# Initialize OpenSearch client
search = None

# Import models to ensure they are registered with SQLAlchemy
from .models.user import User
from .models.listing import Listing
from .models.exchange import Exchange
from .models.chat import Chat, Message
from .models.notification import Notification
from .models.image import Image

def create_app(config_name=None):
    """
    Application factory function to create and configure the Flask app.
    
    Args:
        config_name: Name of the configuration to use (development, testing, production)
        
    Returns:
        Flask: Configured Flask application instance
    """
    from config import config
    
    # Create and configure the app
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)
    principal.init_app(app)
    
    # Configure rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    
    # Configure Socket.IO
    socketio.init_app(
        app,
        message_queue=app.config.get('SOCKETIO_MESSAGE_QUEUE'),
        cors_allowed_origins=app.config.get('CORS_ORIGINS', '*'),
        async_mode=app.config.get('SOCKETIO_ASYNC_MODE', 'eventlet')
    )
    
    # Configure Celery
    celery.conf.update(app.config)
    
    # Configure OpenSearch
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
            ssl_show_warn=app.config.get('OPENSEARCH_SSL_SHOW_WARN', True)
        )
    
    # Register blueprints
    from .api.v1 import api_blueprint
    app.register_blueprint(api_blueprint)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Shell context
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': User,
            'Listing': Listing,
            'Exchange': Exchange,
            'Chat': Chat,
            'Message': Message,
            'Notification': Notification,
            'Image': Image
        }
    
    return app

def register_error_handlers(app):
    ""Register error handlers."""
    from werkzeug.exceptions import HTTPException
    
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

# Create the application instance
app = create_app()

# Import API routes after app creation to avoid circular imports
from .api.v1 import routes  # noqa
