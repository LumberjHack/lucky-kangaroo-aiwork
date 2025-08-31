"""
Gestion des erreurs personnalisées et des gestionnaires d'erreurs globaux.
"""
from typing import Dict, Any, Optional, Tuple
from http import HTTPStatus
import logging
from flask import jsonify, request, Response
from werkzeug.exceptions import HTTPException

# Initialisation du logger
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Classe de base pour les erreurs de l'API."""
    
    def __init__(
        self,
        message: str = "Une erreur inattendue s'est produite",
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        payload: Optional[Dict[str, Any]] = None,
        error_type: Optional[str] = None
    ) -> None:
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}
        self.error_type = error_type or self.__class__.__name__
        
        # Journalisation de l'erreur
        logger.error(
            "%s: %s (status_code=%d, payload=%s, path=%s, method=%s)",
            self.error_type,
            self.message,
            self.status_code,
            self.payload,
            request.path if request else None,
            request.method if request else None,
            exc_info=True
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'erreur en dictionnaire pour la réponse JSON."""
        rv = dict(self.payload or {})
        rv['status'] = 'error'
        rv['code'] = self.status_code
        rv['error'] = self.error_type
        rv['message'] = self.message
        
        # Ajout des métadonnées de débogage en mode développement
        if self.status_code >= 500:
            from flask import current_app
            if current_app and current_app.debug:
                import traceback
                rv['traceback'] = traceback.format_exc()
        
        return rv
    
    def to_response(self) -> Tuple[Dict[str, Any], int]:
        """Retourne un tuple (dict, status_code) pour les réponses Flask."""
        return self.to_dict(), self.status_code

# Erreurs spécifiques
class ValidationError(APIError):
    """Erreur de validation des données."""
    def __init__(self, errors: Dict[str, Any], message: str = "Erreur de validation"):
        super().__init__(
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
            payload={'errors': errors}
        )

class AuthenticationError(APIError):
    """Erreur d'authentification."""
    def __init__(self, message: str = "Authentification requise"):
        super().__init__(
            message=message,
            status_code=HTTPStatus.UNAUTHORIZED,
            headers={'WWW-Authenticate': 'Bearer'}
        )

class ForbiddenError(APIError):
    """Accès refusé."""
    def __init__(self, message: str = "Accès refusé"):
        super().__init__(
            message=message,
            status_code=HTTPStatus.FORBIDDEN
        )

class NotFoundError(APIError):
    """Ressource non trouvée."""
    def __init__(self, resource: str = "ressource", id: Any = None):
        message = f"{resource.capitalize()} non trouvé"
        if id is not None:
            message += f" avec l'ID {id}"
        super().__init__(
            message=message,
            status_code=HTTPStatus.NOT_FOUND
        )

class ConflictError(APIError):
    """Conflit de données."""
    def __init__(self, message: str = "Conflit de données"):
        super().__init__(
            message=message,
            status_code=HTTPStatus.CONFLICT
        )

class RateLimitError(APIError):
    """Limite de requêtes dépassée."""
    def __init__(self, message: str = "Trop de requêtes"):
        super().__init__(
            message=message,
            status_code=HTTPStatus.TOO_MANY_REQUESTS
        )
        self.retry_after = 60  # secondes

# Gestionnaire d'erreurs global
def register_error_handlers(app) -> None:
    """Enregistre les gestionnaires d'erreurs globaux pour l'application Flask."""
    
    @app.errorhandler(APIError)
    def handle_api_error(error: APIError) -> Tuple[Response, int]:
        """Gère les erreurs API personnalisées."""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        
        # Ajout des en-têtes si nécessaire
        if hasattr(error, 'headers'):
            for key, value in error.headers.items():
                response.headers[key] = value
                
        return response, error.status_code
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException) -> Tuple[Response, int]:
        """Gère les exceptions HTTP standard de Werkzeug."""
        if isinstance(error.description, dict):
            # Si l'erreur a déjà une description structurée
            response = jsonify({
                'status': 'error',
                'code': error.code,
                'error': error.name.lower().replace(' ', '_'),
                'message': error.description.get('message', error.description),
                **error.description
            })
        else:
            response = jsonify({
                'status': 'error',
                'code': error.code,
                'error': error.name.lower().replace(' ', '_'),
                'message': error.description or error.name
            })
        
        response.status_code = error.code
        return response, error.code
    
    @app.errorhandler(404)
    def not_found_error(error: Exception) -> Tuple[Response, int]:
        """Gère les erreurs 404 personnalisées."""
        return jsonify({
            'status': 'error',
            'code': 404,
            'error': 'not_found',
            'message': 'La ressource demandée est introuvable',
            'path': request.path
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error: Exception) -> Tuple[Response, int]:
        """Gère les erreurs 500 internes."""
        logger.exception("Erreur interne du serveur")
        
        response = {
            'status': 'error',
            'code': 500,
            'error': 'internal_server_error',
            'message': 'Une erreur interne est survenue',
        }
        
        # Ajout des détails de débogage en mode développement
        if app.debug:
            import traceback
            response['traceback'] = traceback.format_exc()
        
        return jsonify(response), 500
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error: Exception) -> Tuple[Response, int]:
        """Gestionnaire d'erreurs générique pour toutes les exceptions non gérées."""
        logger.exception("Exception non gérée")
        
        # Si c'est une erreur HTTP, laisser le gestionnaire par défaut s'en occuper
        if isinstance(error, HTTPException):
            return error
        
        # Sinon, retourner une erreur 500
        response = {
            'status': 'error',
            'code': 500,
            'error': 'internal_server_error',
            'message': 'Une erreur inattendue est survenue',
        }
        
        # Ajout des détails de débogage en mode développement
        if app.debug:
            import traceback
            response['traceback'] = traceback.format_exc()
        
        return jsonify(response), 500
