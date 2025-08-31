from flask import Blueprint

api_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Import and register feature blueprints
from .auth import auth_bp
from .listings import listings_bp
from .ai import ai_bp
from .matching import matching_bp

api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(listings_bp, url_prefix='/listings')
api_bp.register_blueprint(ai_bp, url_prefix='/ai')
api_bp.register_blueprint(matching_bp, url_prefix='/matching')
