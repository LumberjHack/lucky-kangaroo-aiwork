"""
Lucky Kangaroo - Gestionnaire d'erreurs centralisé
Gestion centralisée des erreurs HTTP et des exceptions
"""

import logging
from flask import jsonify, current_app, request
from werkzeug.exceptions import HTTPException, BadRequest, Unauthorized, Forbidden, NotFound
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from marshmallow import ValidationError
from flask_jwt_extended.exceptions import JWTExtendedException
import traceback

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Classe de base pour les erreurs API personnalisées"""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = True
        rv['message'] = self.message
        rv['status_code'] = self.status_code
        return rv

class ValidationError(APIError):
    """Erreur de validation des données"""
    def __init__(self, message="Données invalides", payload=None):
        super().__init__(message, 400, payload)

class AuthenticationError(APIError):
    """Erreur d'authentification"""
    def __init__(self, message="Authentification requise", payload=None):
        super().__init__(message, 401, payload)

class AuthorizationError(APIError):
    """Erreur d'autorisation"""
    def __init__(self, message="Accès non autorisé", payload=None):
        super().__init__(message, 403, payload)

class ResourceNotFoundError(APIError):
    """Ressource non trouvée"""
    def __init__(self, message="Ressource non trouvée", payload=None):
        super().__init__(message, 404, payload)

class ConflictError(APIError):
    """Conflit de ressources"""
    def __init__(self, message="Conflit de ressources", payload=None):
        super().__init__(message, 409, payload)

class RateLimitError(APIError):
    """Limite de taux dépassée"""
    def __init__(self, message="Trop de requêtes", payload=None):
        super().__init__(message, 429, payload)

def register_error_handlers(app):
    """Enregistre tous les gestionnaires d'erreurs"""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Gère les erreurs API personnalisées"""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        """Gère les erreurs HTTP standard"""
        if isinstance(error, BadRequest):
            message = "Requête invalide"
        elif isinstance(error, Unauthorized):
            message = "Authentification requise"
        elif isinstance(error, Forbidden):
            message = "Accès interdit"
        elif isinstance(error, NotFound):
            message = "Ressource non trouvée"
        else:
            message = error.description or "Erreur HTTP"
        
        response = jsonify({
            'error': True,
            'message': message,
            'status_code': error.code,
            'type': 'http_error'
        })
        response.status_code = error.code
        return response

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Gère les erreurs de validation Marshmallow"""
        response = jsonify({
            'error': True,
            'message': 'Erreur de validation',
            'status_code': 400,
            'type': 'validation_error',
            'details': error.messages
        })
        response.status_code = 400
        return response

    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(error):
        """Gère les erreurs de base de données"""
        logger.error(f"Database error: {str(error)}")
        
        if isinstance(error, IntegrityError):
            message = "Violation de contrainte de base de données"
        else:
            message = "Erreur de base de données"
        
        response = jsonify({
            'error': True,
            'message': message,
            'status_code': 500,
            'type': 'database_error'
        })
        response.status_code = 500
        return response

    @app.errorhandler(JWTExtendedException)
    def handle_jwt_error(error):
        """Gère les erreurs JWT"""
        response = jsonify({
            'error': True,
            'message': 'Erreur d\'authentification',
            'status_code': 401,
            'type': 'jwt_error'
        })
        response.status_code = 401
        return response

    @app.errorhandler(429)
    def handle_rate_limit_error(error):
        """Gère les erreurs de limite de taux"""
        response = jsonify({
            'error': True,
            'message': 'Trop de requêtes. Veuillez ralentir.',
            'status_code': 429,
            'type': 'rate_limit_error'
        })
        response.status_code = 429
        return response

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        """Gère toutes les autres exceptions non gérées"""
        # Log l'erreur complète pour le débogage
        logger.error(f"Unhandled error: {str(error)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # En production, ne pas exposer les détails de l'erreur
        if current_app.config.get('DEBUG', False):
            message = f"Erreur interne: {str(error)}"
        else:
            message = "Une erreur interne s'est produite"
        
        response = jsonify({
            'error': True,
            'message': message,
            'status_code': 500,
            'type': 'internal_error'
        })
        response.status_code = 500
        return response

    @app.errorhandler(404)
    def not_found(error):
        """Gère les routes non trouvées"""
        return jsonify({
            'error': True,
            'message': 'Endpoint non trouvé',
            'status_code': 404,
            'type': 'not_found',
            'available_endpoints': [
                '/api/v1/auth/login',
                '/api/v1/auth/register',
                '/api/v1/listings',
                '/api/v1/exchanges',
                '/api/v1/chat',
                '/api/v1/search',
                '/api/v1/users',
                '/api/v1/admin'
            ]
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Gère les méthodes HTTP non autorisées"""
        return jsonify({
            'error': True,
            'message': 'Méthode HTTP non autorisée',
            'status_code': 405,
            'type': 'method_not_allowed'
        }), 405

    # Log des erreurs pour le monitoring
    @app.before_request
    def log_request_info():
        """Log les informations de requête pour le debugging"""
        if current_app.config.get('DEBUG', False):
            logger.debug(f"Request: {request.method} {request.path} - {request.remote_addr}")

    @app.after_request
    def log_response_info(response):
        """Log les informations de réponse pour le debugging"""
        if current_app.config.get('DEBUG', False):
            logger.debug(f"Response: {response.status_code} for {request.method} {request.path}")
        return response
