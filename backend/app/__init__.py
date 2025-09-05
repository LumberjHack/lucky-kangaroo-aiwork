"""
Application Flask Lucky Kangaroo - Factory Pattern
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_session import Session
import redis
from celery import Celery
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

# Initialiser les extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
socketio = SocketIO()
mail = Mail()
bcrypt = Bcrypt()
cache = Cache()
session = Session()

def create_app(config_name=None):
    """Factory pour créer l'application Flask"""
    
    app = Flask(__name__)
    
    # Déterminer la configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Importer la configuration
    from config import config as app_config
    app.config.from_object(app_config[config_name])
    
    # Créer le dossier d'upload s'il n'existe pas
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialiser les extensions avec l'app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    cache.init_app(app)
    session.init_app(app)
    limiter.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Enregistrer les blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Routes de base
    @app.route('/')
    def index():
        """Route racine de l'API"""
        return {
            'message': 'Lucky Kangaroo API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'auth': '/api/v1/auth',
                'users': '/api/v1/users',
                'listings': '/api/v1/listings',
                'exchanges': '/api/v1/exchanges',
                'chat': '/api/v1/chat',
                'search': '/api/v1/search',
                'ai': '/api/v1/ai'
            }
        }
    
    @app.route('/health')
    def health_check():
        """Vérification de santé de l'API"""
        try:
            # Vérifier la base de données
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            db_status = 'healthy'
        except Exception as e:
            db_status = f'unhealthy: {str(e)}'
        
        return {
            'status': 'healthy',
            'database': db_status,
            'timestamp': '2024-01-01T00:00:00Z'
        }
    
    return app

def create_celery(app):
    """Factory pour créer l'instance Celery"""
    celery = Celery(
        app.import_name,
        backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        broker=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    )
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery