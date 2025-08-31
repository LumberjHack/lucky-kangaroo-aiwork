#!/usr/bin/env python3
"""
Lucky Kangaroo - Backend API
Application principale Flask avec configuration modulaire
"""
import logging
from logging.config import dictConfig
from pathlib import Path
import os
import sys
from typing import Optional

# Ajouter le répertoire courant au path pour permettre des imports absolus du package backend
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Charger les variables d'environnement au démarrage (une seule fois)
from dotenv import load_dotenv
load_dotenv()

# Logging de démarrage minimal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import datetime
import uuid
from flask import Flask
from flask.json.provider import DefaultJSONProvider
from werkzeug.security import generate_password_hash

# Note: Duplicate Sentry initialization removed to avoid double init.

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


def configure_logging(app) -> None:
    """Configure la journalisation pour l'application.
    
    Args:
        app: L'instance de l'application Flask
    """
    # Création du répertoire de logs s'il n'existe pas
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
                'level': 'INFO',
                'propagate': False,
            },
            'sqlalchemy.engine': {
                'handlers': ['console', 'file'],
                'level': 'WARNING',
                'propagate': False,
            },
        }
    }
    
    try:
        dictConfig(log_config)
        app.logger = logging.getLogger(__name__)
        app.logger.setLevel(log_level)
        if not app.debug:
            logging.getLogger('werkzeug').setLevel(logging.WARNING)
        app.logger.info('Configuration de la journalisation terminée')
    except Exception as e:
        # Fallback vers un logging basique pour ne pas bloquer le démarrage
        logging.basicConfig(level=logging.INFO)
        app.logger = logging.getLogger(__name__)
        app.logger.error(f"Erreur configuration logging: {e}")
        app.logger.warning("Fallback vers logging.basicConfig(level=INFO)")


def register_blueprints(app):
    """Register API blueprint (Flask-RESTX)."""
    # Utilise le blueprint RESTX global défini dans api/__init__.py
    from api import api_blueprint
    app.register_blueprint(api_blueprint, url_prefix="/api")


def register_commands(app):
    """Register Click commands."""
    import click
    from flask.cli import with_appcontext
    from extensions import db  # import absolu

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
        from models import User  # import absolu

        if User.query.filter_by(email=email).first():
            click.echo(f'User {email} already exists.')
            return

        admin = User(
            email=email,
            password=generate_password_hash(password),
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
        from models import Listing
        from search import index_listing

        count = 0
        for listing in Listing.query.filter_by(is_active=True):
            index_listing(listing)
            count += 1

        click.echo(f'Indexed {count} listings.')


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

    # Déterminer l'environnement
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    # Charger la configuration depuis le module config via get_config()
    from config import get_config
    try:
        app.config.from_object(get_config(config_name))
    except Exception:
        # Fallback vers development si l'alias de config est inconnu
        # configure_logging n'est pas encore appliqué, on loguera après configuration
        app.config.from_object(get_config('development'))

    # Journalisation la plus tôt possible afin de capter les erreurs suivantes
    configure_logging(app)

    # Validation des configurations essentielles
    if not app.config.get('SECRET_KEY'):
        app.logger.error('SECRET_KEY non configurée - ceci est essentiel pour la sécurité!')
        raise RuntimeError('SECRET_KEY doit être configurée')
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        app.logger.error('SQLALCHEMY_DATABASE_URI non configurée - base de données indisponible')
        raise RuntimeError('SQLALCHEMY_DATABASE_URI doit être configurée')

    # Fournisseur JSON
    app.json = CustomJSONProvider(app)

    # Initialisation des extensions (imports absolus)
    from extensions import db, migrate, jwt, cors, cache, limiter, mail, redis_connection
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    # Configuration CORS plus précise (un seul init)
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', '*').split(',') if isinstance(app.config.get('CORS_ORIGINS', '*'), str) else app.config.get('CORS_ORIGINS')
        }
    })
    cache.init_app(app, config=app.config.get('CACHE_CONFIG', {}))
    limiter.init_app(app)
    mail.init_app(app)

    # Configuration des API externes (imports optionnels, sans échec de démarrage)
    try:
        import stripe
        if (stripe_key := app.config.get('STRIPE_SECRET_KEY')):
            stripe.api_key = stripe_key
        else:
            app.logger.warning("Stripe API key not configured")
    except ImportError:
        app.logger.warning("Stripe SDK non installé - fonctionnalités Stripe désactivées")

    try:
        import openai
        if (openai_key := app.config.get('OPENAI_API_KEY')):
            openai.api_key = openai_key
        else:
            app.logger.warning("OpenAI API key not configured")
    except ImportError:
        app.logger.warning("OpenAI SDK non installé - fonctionnalités OpenAI désactivées")

    # Sentry (une seule initialisation et import local)
    if app.config.get('SENTRY_DSN'):
        try:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
            from sentry_sdk.integrations.redis import RedisIntegration
            sentry_sdk.init(
                dsn=app.config['SENTRY_DSN'],
                integrations=[FlaskIntegration(), SqlalchemyIntegration(), RedisIntegration()],
                traces_sample_rate=app.config.get('SENTRY_TRACES_SAMPLE_RATE', 0.5),
                environment=app.config.get('ENV', 'development')
            )
        except ImportError:
            app.logger.warning("Sentry SDK non installé - monitoring Sentry désactivé")

    # JWT callbacks
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload.get('jti')
        return bool(jti and redis_connection.get(jti))

    # Journalisation (déjà configurée plus tôt)

    # Blueprints
    register_blueprints(app)

    # Endpoint de healthcheck minimal (utile pour load balancer)
    @app.route('/healthz')
    def health_check():
        from flask import jsonify
        return jsonify({
            'status': 'ok',
            'environment': app.config.get('ENV', 'unknown')
        })

    # Gestionnaires d'erreurs (import absolu)
    from errors import register_error_handlers as _register_error_handlers
    _register_error_handlers(app)

    # Commandes CLI
    register_commands(app)

    # Shell context
    @app.shell_context_processor
    def make_shell_context():
        from models import User, Listing, Exchange, Chat, Notification, Image
        return {
            'db': db,
            'User': User,
            'Listing': Listing,
            'Exchange': Exchange,
            'Chat': Chat,
            'Notification': Notification,
            'Image': Image
        }

    return app


# Point d'entrée principal pour exécution directe
if __name__ == '__main__':
    application = create_app()
    application.run(host='0.0.0.0', port=5000, debug=application.config.get('DEBUG', False))


