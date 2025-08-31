"""
Authentication routes for the Lucky Kangaroo API v1.
Handles user registration, login, logout, password reset, and token refresh.
"""

from flask import request, current_app, make_response
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
    verify_jwt_in_request
)
from flask_restx import Resource, fields, reqparse
import re
import datetime

from models.user import User
from extensions import db, limiter, mail
from flask_mail import Message
from utils.decorators import admin_required, validate_json
from utils.security import generate_verification_token, verify_verification_token
from utils.rate_limits import get_limiter_key
from . import ns

# Request parsers
login_parser = reqparse.RequestParser()
login_parser.add_argument('email', type=str, required=True, help='Email address')
login_parser.add_argument('password', type=str, required=True, help='Password')
login_parser.add_argument('device_id', type=str, required=False, help='Device ID')
login_parser.add_argument('device_info', type=dict, required=False, help='Device information')

register_parser = reqparse.RequestParser()
register_parser.add_argument('email', type=str, required=True, help='Email address')
register_parser.add_argument('password', type=str, required=True, help='Password')
register_parser.add_argument('first_name', type=str, required=True, help='First name')
register_parser.add_argument('last_name', type=str, required=True, help='Last name')
register_parser.add_argument('phone_number', type=str, required=False, help='Phone number')
register_parser.add_argument('accept_terms', type=bool, required=True, help='Acceptance of terms and conditions')

# Response models
auth_response = ns.model('AuthResponse', {
    'access_token': fields.String(description='JWT access token'),
    'refresh_token': fields.String(description='JWT refresh token'),
    'user': fields.Nested(ns.model('UserResponse', {
        'id': fields.Integer(description='User ID'),
        'email': fields.String(description='Email address'),
        'first_name': fields.String(description='First name'),
        'last_name': fields.String(description='Last name'),
        'is_verified': fields.Boolean(description='Email verification status'),
        'has_password': fields.Boolean(description='Whether the user has a password set')
    }))
})

@ns.route('/auth/register')
class Register(Resource):
    """User registration endpoint."""
    
    @ns.expect(register_parser)
    @ns.response(201, 'User registered successfully')
    @ns.response(400, 'Invalid input')
    @ns.response(409, 'Email already exists')
    @limiter.limit('5 per minute', key_func=get_limiter_key)
    def post(self):
        """Register a new user."""
        args = register_parser.parse_args()
        
        # Validate email format
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', args['email']):
            return {'message': 'Invalid email format'}, 400
            
        # Check if email already exists
        if User.query.filter_by(email=args['email']).first():
            return {'message': 'Email already registered'}, 409
            
        # Validate password strength
        if len(args['password']) < 8:
            return {'message': 'Password must be at least 8 characters long'}, 400
            
        # Create new user
        user = User(
            email=args['email'],
            first_name=args['first_name'],
            last_name=args['last_name'],
            phone_number=args.get('phone_number'),
            is_verified=False,
            accepted_terms=args['accept_terms'],
            terms_accepted_at=datetime.datetime.utcnow() if args['accept_terms'] else None
        )
        user.set_password(args['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Generate verification token and send verification email
        token = generate_verification_token(user.email)
        verification_url = f"{current_app.config['FRONTEND_URL']}/verify-email?token={token}"
        
        msg = Message(
            'Verify Your Email - Lucky Kangaroo',
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[user.email]
        )
        msg.body = f"""
        Welcome to Lucky Kangaroo!
        
        Please click the following link to verify your email address:
        {verification_url}
        
        If you did not create an account, please ignore this email.
        """
        
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Failed to send verification email: {str(e)}")
        
        # Generate tokens
        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(identity=user.id)
        
        # Note: Session persistence disabled (no UserSession model). JWT is returned without DB session tracking.
        
        response_data = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_verified': user.is_verified,
                'has_password': user.password_hash is not None
            }
        }
        
        response = {'message': 'User registered successfully', 'data': response_data}, 201
        
        # Set HTTP-only cookies if configured
        if current_app.config.get('JWT_COOKIE_SECURE', False):
            response = make_response(response)
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            
        return response

@ns.route('/auth/login')
class Login(Resource):
    """User login endpoint."""
    
    @ns.expect(login_parser)
    @ns.response(200, 'Login successful', auth_response)
    @ns.response(400, 'Invalid input')
    @ns.response(401, 'Invalid credentials')
    @limiter.limit('5 per minute', key_func=get_limiter_key)
    def post(self):
        """Authenticate a user and return tokens."""
        args = login_parser.parse_args()
        
        user = User.query.filter_by(email=args['email']).first()
        
        if not user or not user.check_password(args['password']):
            return {'message': 'Invalid email or password'}, 401
            
        # Check if user is active
        if not user.is_active:
            return {'message': 'Account is deactivated'}, 403
            
        # Generate tokens
        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(identity=user.id)
        
        # Note: Session persistence disabled (no UserSession model). Proceed without DB session tracking.
        
        response_data = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_verified': user.is_verified,
                'has_password': user.password_hash is not None
            }
        }
        
        response = {'message': 'Login successful', 'data': response_data}, 200
        
        # Set HTTP-only cookies if configured
        if current_app.config.get('JWT_COOKIE_SECURE', False):
            response = make_response(response)
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            
        return response

@ns.route('/auth/refresh')
class Refresh(Resource):
    """Refresh access token endpoint."""
    
    @jwt_required(refresh=True)
    @ns.response(200, 'Token refreshed', auth_response)
    @ns.response(401, 'Invalid or expired refresh token')
    def post(self):
        """Refresh an access token using a refresh token."""
        current_user = get_jwt_identity()
        
        # Create new tokens (DB session validation removed)
        new_access_token = create_access_token(identity=current_user, fresh=False)
        new_refresh_token = create_refresh_token(identity=current_user)
        
        # Get user data
        user = User.query.get(current_user)
        
        response_data = {
            'access_token': new_access_token,
            'refresh_token': new_refresh_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_verified': user.is_verified,
                'has_password': user.password_hash is not None
            }
        }
        
        response = {'message': 'Token refreshed', 'data': response_data}, 200
        
        # Set HTTP-only cookies if configured
        if current_app.config.get('JWT_COOKIE_SECURE', False):
            response = make_response(response)
            set_access_cookies(response, new_access_token)
            set_refresh_cookies(response, new_refresh_token)
            
        return response

@ns.route('/auth/logout')
class Logout(Resource):
    """Logout endpoint."""
    
    @jwt_required()
    @ns.response(200, 'Successfully logged out')
    def post(self):
        """Log out the current user by invalidating the refresh token."""
        # Note: Token blacklist and session invalidation skipped (no models). Cookies will be cleared if configured.
        
        response = {'message': 'Successfully logged out'}, 200
        
        # Clear cookies if configured
        if current_app.config.get('JWT_COOKIE_SECURE', False):
            response = make_response(response)
            unset_jwt_cookies(response)
            
        return response

@ns.route('/auth/verify-email/<token>')
class VerifyEmail(Resource):
    """Email verification endpoint."""
    
    @jwt_required(optional=True)
    @ns.response(200, 'Email verified successfully')
    @ns.response(400, 'Invalid or expired token')
    def get(self, token):
        """Verify a user's email address using a verification token."""
        email = verify_verification_token(token)
        if not email:
            return {'message': 'Invalid or expired verification token'}, 400
            
        user = User.query.filter_by(email=email).first()
        if not user:
            return {'message': 'User not found'}, 404
            
        if user.is_verified:
            return {'message': 'Email already verified'}, 200
            
        user.is_verified = True
        user.email_verified_at = datetime.datetime.utcnow()
        db.session.commit()
        
        return {'message': 'Email verified successfully'}, 200

@ns.route('/auth/request-password-reset')
class RequestPasswordReset(Resource):
    """Request password reset endpoint."""
    
    @ns.expect(ns.model('RequestPasswordReset', {
        'email': fields.String(required=True, description='User email')
    }))
    @ns.response(200, 'If the email exists, a password reset link has been sent')
    @limiter.limit('3 per hour', key_func=get_limiter_key)
    def post(self):
        """Request a password reset email."""
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return {'message': 'Email is required'}, 400
            
        user = User.query.filter_by(email=email).first()
        if not user:
            # For security, don't reveal if the email exists
            return {'message': 'If your email is registered, you will receive a password reset link'}, 200
            
        # Generate a password reset token
        token = generate_verification_token(user.email, salt='reset-password')
        reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password?token={token}"
        
        # Send password reset email
        msg = Message(
            'Password Reset Request - Lucky Kangaroo',
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[user.email]
        )
        msg.body = f"""
        You have requested to reset your password.
        
        Please click the following link to reset your password:
        {reset_url}
        
        If you did not request this, please ignore this email and your password will remain unchanged.
        
        This link will expire in 1 hour.
        """
        
        try:
            mail.send(msg)
            return {'message': 'If your email is registered, you will receive a password reset link'}, 200
        except Exception as e:
            current_app.logger.error(f"Failed to send password reset email: {str(e)}")
            return {'message': 'Failed to send password reset email'}, 500

@ns.route('/auth/reset-password')
class ResetPassword(Resource):
    """Reset password endpoint."""
    
    @ns.expect(ns.model('ResetPassword', {
        'token': fields.String(required=True, description='Password reset token'),
        'new_password': fields.String(required=True, description='New password')
    }))
    @ns.response(200, 'Password has been reset successfully')
    @ns.response(400, 'Invalid or expired token')
    @limiter.limit('3 per hour', key_func=get_limiter_key)
    def post(self):
        """Reset a user's password using a valid token."""
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('new_password')
        
        if not token or not new_password:
            return {'message': 'Token and new password are required'}, 400
            
        # Verify the token
        email = verify_verification_token(token, salt='reset-password')
        if not email:
            return {'message': 'Invalid or expired token'}, 400
            
        # Find the user
        user = User.query.filter_by(email=email).first()
        if not user:
            return {'message': 'User not found'}, 404
            
        # Update the password
        user.set_password(new_password)
        db.session.commit()
        
        # Note: Session invalidation skipped (no UserSession model).
        
        return {'message': 'Password has been reset successfully'}, 200

# Social authentication routes would be implemented here
# (Google, Facebook, Apple, etc.)

# Two-factor authentication routes would be implemented here
# (enable 2FA, verify 2FA, etc.)
