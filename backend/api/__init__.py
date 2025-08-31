"""
Lucky Kangaroo API Package

This package contains all API-related code for the Lucky Kangaroo application,
including API blueprints, namespaces, and versioning.
"""

from flask import Blueprint, jsonify, current_app
from flask_restx import Api

# Create API blueprint
api_blueprint = Blueprint('api', __name__)

# Initialize Flask-RESTx API
authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Type in the 'Value' input box below: **'Bearer &lt;JWT&gt;'** where JWT is the token"
    }
}

api = Api(
    api_blueprint,
    version='1.0',
    title='Lucky Kangaroo API',
    description='API for Lucky Kangaroo - The Ultimate Exchange Platform',
    doc='/docs',
    authorizations=authorizations,
    security='Bearer Auth',
    default='v1',
    default_label='API v1',
    validate=True
)

# Simple healthcheck endpoint mounted at /api/health
@api_blueprint.route('/health', methods=['GET'])
def health():
    cfg = current_app.config
    return jsonify({
        'status': 'ok',
        'version': cfg.get('APP_VERSION', 'unknown'),
        'environment': cfg.get('ENV', cfg.get('FLASK_ENV', 'development')),
    }), 200

# Import API namespaces to register routes
from .v1 import ns as v1_namespace  # noqa

# Register namespaces
api.add_namespace(v1_namespace)
