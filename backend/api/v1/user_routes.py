"""
User routes for the Lucky Kangaroo API v1.
Handles user profile management, preferences, and account settings.
"""

from flask import request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Resource, fields, reqparse
from datetime import datetime

from ...models.user import User
from ...extensions import db, limiter
from . import ns

# Request parsers
update_profile_parser = reqparse.RequestParser()
update_profile_parser.add_argument('first_name', type=str, required=False, help='First name')
update_profile_parser.add_argument('last_name', type=str, required=False, help='Last name')
update_profile_parser.add_argument('phone', type=str, required=False, help='Phone number')
update_profile_parser.add_argument('bio', type=str, required=False, help='User bio')
update_profile_parser.add_argument('date_of_birth', type=str, required=False, help='Date of birth (YYYY-MM-DD)')
update_profile_parser.add_argument('address', type=dict, required=False, help='Address information {address, city, postal_code, country}')

update_preferences_parser = reqparse.RequestParser()
update_preferences_parser.add_argument('email_notifications', type=bool, required=False, help='Enable/disable email notifications')
update_preferences_parser.add_argument('push_notifications', type=bool, required=False, help='Enable/disable push notifications')
update_preferences_parser.add_argument('preferred_language', type=str, required=False, help='Preferred language code')
update_preferences_parser.add_argument('preferred_currency', type=str, required=False, help='Preferred currency code')
update_preferences_parser.add_argument('max_distance_km', type=int, required=False, help='Search radius in kilometers')

change_password_parser = reqparse.RequestParser()
change_password_parser.add_argument('current_password', type=str, required=True, help='Current password')
change_password_parser.add_argument('new_password', type=str, required=True, help='New password')

# Avatar update parser (URL-based to avoid missing S3 client)
avatar_parser = reqparse.RequestParser()
avatar_parser.add_argument('avatar_url', type=str, required=True, help='Public URL of the avatar image')

# Response models
user_profile_model = ns.model('UserProfile', {
    'id': fields.Integer(description='User ID'),
    'email': fields.String(description='Email address'),
    'first_name': fields.String(description='First name'),
    'last_name': fields.String(description='Last name'),
    'phone': fields.String(description='Phone number'),
    'is_verified': fields.Boolean(description='Email verification status'),
    'profile_photo_url': fields.String(description='URL to profile picture'),
    'bio': fields.String(description='User bio'),
    'date_of_birth': fields.Date(description='Date of birth'),
    'address': fields.Raw(description='Address information'),
    'created_at': fields.DateTime(description='Account creation date'),
    'updated_at': fields.DateTime(description='Last profile update date'),
    'trust_score': fields.Float(description='User trust score (0-100)'),
    'preferences': fields.Raw(description='Flattened preferences from User model')
})

@ns.route('/users/me')
class CurrentUser(Resource):
    """Current user profile endpoint."""
    
    @jwt_required()
    @ns.marshal_with(user_profile_model)
    def get(self):
        """Get the current user's profile."""
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        return user.to_dict(include_sensitive=True)
    
    @jwt_required()
    @ns.expect(update_profile_parser)
    @ns.marshal_with(user_profile_model)
    def put(self):
        """Update the current user's profile."""
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        
        args = update_profile_parser.parse_args()
        
        # Update direct user fields
        if args.get('first_name') is not None:
            user.first_name = args['first_name']
        if args.get('last_name') is not None:
            user.last_name = args['last_name']
        if 'phone' in args and args['phone'] is not None:
            user.phone = args['phone']
        if 'bio' in args and args['bio'] is not None:
            user.bio = args['bio']
        if 'date_of_birth' in args and args['date_of_birth']:
            try:
                user.date_of_birth = datetime.strptime(args['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                return {'message': 'Invalid date format. Use YYYY-MM-DD'}, 400
        if 'address' in args and args['address']:
            addr = args['address'] or {}
            if isinstance(addr, dict):
                if 'address' in addr:
                    user.address = addr.get('address')
                if 'city' in addr:
                    user.city = addr.get('city')
                if 'postal_code' in addr:
                    user.postal_code = addr.get('postal_code')
                if 'country' in addr:
                    user.country = addr.get('country')
            else:
                user.address = str(addr)
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return user.to_dict(include_sensitive=True)

@ns.route('/users/me/preferences')
class UserPreferencesResource(Resource):
    """User preferences endpoint."""
    
    @jwt_required()
    @ns.marshal_with(user_profile_model)
    def get(self):
        """Get the current user's preferences."""
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        
        return user.to_dict(include_sensitive=True)
    
    @jwt_required()
    @ns.expect(update_preferences_parser)
    @ns.marshal_with(user_profile_model)
    def put(self):
        """Update the current user's preferences."""
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        
        args = update_preferences_parser.parse_args()
        
        # Update flat preference fields on User
        if 'email_notifications' in args and args['email_notifications'] is not None:
            user.email_notifications = args['email_notifications']
        if 'push_notifications' in args and args['push_notifications'] is not None:
            user.push_notifications = args['push_notifications']
        if 'preferred_language' in args and args['preferred_language'] is not None:
            user.preferred_language = args['preferred_language']
        if 'preferred_currency' in args and args['preferred_currency'] is not None:
            user.preferred_currency = args['preferred_currency']
        if 'max_distance_km' in args and args['max_distance_km'] is not None:
            user.max_distance_km = args['max_distance_km']
        
        db.session.commit()
        
        return user.to_dict(include_sensitive=True)

@ns.route('/users/me/password')
class ChangePassword(Resource):
    """Change password endpoint."""
    
    @jwt_required()
    @ns.expect(change_password_parser)
    def put(self):
        """Change the current user's password."""
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        
        args = change_password_parser.parse_args()
        
        # Verify current password
        if not user.check_password(args['current_password']):
            return {'message': 'Current password is incorrect'}, 400
        
        # Update password
        user.set_password(args['new_password'])
        db.session.commit()
        return {'message': 'Password changed successfully'}, 200

@ns.route('/users/me/avatar')
class UserAvatar(Resource):
    """User avatar management endpoint."""
    
    @jwt_required()
    @ns.expect(avatar_parser)
    @ns.response(200, 'Avatar URL updated successfully')
    @ns.response(400, 'Invalid payload')
    def post(self):
        """Set the user's profile picture via public URL (no file upload)."""
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        
        args = avatar_parser.parse_args()
        avatar_url = args.get('avatar_url')
        if not avatar_url:
            return {'message': 'avatar_url is required'}, 400
        
        user.profile_photo_url = avatar_url
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {'avatar_url': avatar_url}, 200
    
    @jwt_required()
    def delete(self):
        """Remove the current user's profile picture."""
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        
        if not user.profile_photo_url:
            return {'message': 'No profile picture to remove'}, 400
        
        try:
            user.profile_photo_url = None
            user.updated_at = datetime.utcnow()
            db.session.commit()
            return {'message': 'Profile picture removed successfully'}, 200
        except Exception as e:
            current_app.logger.error(f"Failed to remove avatar: {str(e)}")
            return {'message': 'Failed to remove profile picture'}, 500

@ns.route('/users/me/sessions')
class UserSessions(Resource):
    """User sessions management endpoint (disabled - no DB model)."""
    
    @jwt_required()
    def get(self):
        """Get the current user's active sessions (not implemented)."""
        return {'sessions': []}, 200
    
    @jwt_required()
    def delete(self, session_id=None):
        """Revoke a specific session or all other sessions (not implemented)."""
        return {'message': 'Session management is disabled'}, 200

@ns.route('/users/<int:user_id>')
class UserResource(Resource):
    """Public user profile endpoint."""
    
    @jwt_required()
    @ns.marshal_with(user_profile_model)
    def get(self, user_id):
        """Get a user's public profile."""
        user = User.query.get_or_404(user_id)
        return user.to_public_dict()

# Admin-only endpoints
@ns.route('/admin/users')
class AdminUserList(Resource):
    """Admin endpoint for user management (no admin guard)."""
    
    @jwt_required()
    def get(self):
        """Get a list of all users (admin only)."""
        users = User.query.all()
        return {
            'users': [{
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'is_verified': user.is_verified,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login_at.isoformat() if user.last_login_at else None
            } for user in users]
        }, 200

@ns.route('/admin/users/<int:user_id>/status')
class AdminUserStatus(Resource):
    """Admin endpoint for updating user status (no admin guard)."""
    
    @jwt_required()
    @ns.expect(ns.model('UpdateUserStatus', {
        'is_active': fields.Boolean(required=True, description='Whether the user account should be active')
    }))
    def put(self, user_id):
        """Update a user's active status (admin only)."""
        current_user_id = get_jwt_identity()
        if user_id == current_user_id:
            return {'message': 'Cannot modify your own status'}, 400
            
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        user.is_active = data['is_active']
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {'message': 'User status updated successfully'}, 200
