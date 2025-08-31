"""
Lucky Kangaroo API v1

This package defines the RESTX Namespace `ns` for version 1 and loads
route modules so their resources are registered on `ns`.
"""

from flask_restx import Namespace

# Create API namespace used by all v1 route modules
ns = Namespace('v1', description='API version 1 operations')

# Import route modules to register resources on `ns`
# Each module uses: from . import ns
from . import (
    auth_routes,
    user_routes,
    listing_routes,
    chat_routes,
    search_routes,
    notification_routes,
    admin_routes,
    payments,
    reports,
    ai_routes,
    gamification_routes,
    exchange_routes,
)

__all__ = ['ns']
