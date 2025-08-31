import os
from flask import Flask
from dotenv import load_dotenv
from .config import config
from .extensions import init_extensions, db, jwt
from .errors import register_error_handlers

load_dotenv()

def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])

    # Also load env vars with APP_ prefix if present
    app.config.from_prefixed_env()

    # Init extensions
    init_extensions(app)

    # JWT blocklist example using redis
    from .utils import redis_connection

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token_in_redis = redis_connection.get(jti)
        return token_in_redis is not None

    # Blueprints
    from .api.v1 import api_bp
    app.register_blueprint(api_bp)

    # Errors
    register_error_handlers(app)

    # Shell context
    @app.shell_context_processor
    def make_shell_context():
        from .models import User, Listing, Image
        return {
            'db': db,
            'User': User,
            'Listing': Listing,
            'Image': Image,
        }

    return app
