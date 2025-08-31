"""
Rate limiting utilities for API endpoints.
"""
from functools import wraps
from typing import Callable, Any, Optional, Dict

from flask import jsonify, Flask
from flask_limiter.util import get_remote_address
from ..extensions import limiter


def get_limiter_key() -> str:
    """Get rate limiter key based on user ID if authenticated, else IP.
    
    Returns:
        str: A unique identifier for rate limiting (user ID or IP address)
    """
    from flask_jwt_extended import get_jwt_identity
    
    current_identity = get_jwt_identity()
    return str(current_identity) if current_identity else get_remote_address()


def rate_limited(limit: str = "100 per minute", 
                key_func: Optional[Callable] = None, 
                **kwargs) -> Callable:
    """Decorator to apply rate limiting to a view function.
    
    Args:
        limit: Rate limit string (e.g., '100 per minute')
        key_func: Optional function to get the key for rate limiting
        **kwargs: Additional arguments to pass to the rate limiter
        
    Returns:
        Callable: Decorated function with rate limiting applied
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs_: Any) -> Any:
            if limiter.enabled:
                key_func_ = key_func or get_limiter_key
                limiter.check(f, limit=limit, key_func=key_func_, **kwargs)
            return f(*args, **kwargs_)
        return decorated_function
    return decorator


def init_rate_limiter(app: Flask) -> None:
    """Initialize rate limiting for the application.
    
    Args:
        app: Flask application instance
    """
    # Default rate limits (applied to all routes)
    limiter.init_app(app)
    
    # Exempt certain endpoints from rate limiting
    limiter.exempt('static')
    
    # Custom rate limits for specific endpoints
    custom_limits: Dict[str, str] = {
        'auth.login': '10 per minute',
        'auth.register': '5 per hour',
        'auth.reset_password': '3 per hour',
        'ai.chat': '30 per 5 minutes',
        'ai.generate_content': '20 per hour',
        'search.semantic': '60 per minute',
        'search.vector': '100 per minute',
        'listings.create': '10 per minute',
        'listings.update': '30 per minute',
        'users.update': '60 per hour',
        'users.change_password': '5 per hour',
        'payments.create_intent': '10 per minute',
    }
    
    # Apply custom limits
    for endpoint, limit in custom_limits.items():
        limiter.limit(limit, key_func=get_limiter_key, endpoint=endpoint)
    
    @app.errorhandler(429)
    def ratelimit_handler(e: Exception) -> tuple[dict[str, str], int]:
        """Handle rate limit exceeded errors.
        
        Args:
            e: The exception that was raised
            
        Returns:
            tuple: JSON response and status code
        """
        return jsonify({
            'error': 'rate_limit_exceeded',
            'message': f'Too many requests. Limit: {str(e)}'
        }), 429
