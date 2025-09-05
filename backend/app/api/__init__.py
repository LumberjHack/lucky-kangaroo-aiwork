"""
API Blueprints pour Lucky Kangaroo
"""

from flask import Blueprint

# Créer le blueprint principal de l'API
api_bp = Blueprint('api', __name__)

# Importer tous les blueprints
from .auth import auth_bp
from .users import users_bp
from .listings import listings_bp
from .exchanges import exchanges_bp
from .chat import chat_bp
from .search import search_bp
from .admin import admin_bp
from .ai import ai_bp

# Enregistrer les blueprints
api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(users_bp, url_prefix='/users')
api_bp.register_blueprint(listings_bp, url_prefix='/listings')
api_bp.register_blueprint(exchanges_bp, url_prefix='/exchanges')
api_bp.register_blueprint(chat_bp, url_prefix='/chat')
api_bp.register_blueprint(search_bp, url_prefix='/search')
api_bp.register_blueprint(admin_bp, url_prefix='/admin')
api_bp.register_blueprint(ai_bp, url_prefix='/ai')