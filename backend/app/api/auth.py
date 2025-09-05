"""
API d'authentification pour Lucky Kangaroo
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity,
    get_jwt
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from marshmallow import Schema, fields, validate, ValidationError
from werkzeug.security import check_password_hash, generate_password_hash
from app import db, bcrypt, limiter
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
import uuid
from datetime import datetime, timedelta

# Créer le blueprint
auth_bp = Blueprint('auth', __name__)

# Services
auth_service = AuthService()
email_service = EmailService()

# Schemas de validation
class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    first_name = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    phone = fields.Str(validate=validate.Length(min=10, max=15))

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class RefreshTokenSchema(Schema):
    refresh_token = fields.Str(required=True)

class ForgotPasswordSchema(Schema):
    email = fields.Email(required=True)

class ResetPasswordSchema(Schema):
    token = fields.Str(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """Inscription d'un nouvel utilisateur"""
    try:
        schema = RegisterSchema()
        data = schema.load(request.json)
        
        # Vérifier si l'utilisateur existe déjà
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'message': 'Un utilisateur avec cet email existe déjà'
            }), 400
        
        # Créer le nouvel utilisateur
        user = User(
            id=str(uuid.uuid4()),
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone'),
            password_hash=bcrypt.generate_password_hash(data['password']).decode('utf-8'),
            is_verified=False,
            created_at=datetime.utcnow()
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Générer les tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        # Envoyer l'email de vérification
        try:
            email_service.send_verification_email(user.email, user.id)
        except Exception as e:
            # Log l'erreur mais ne pas faire échouer l'inscription
            print(f"Erreur envoi email: {e}")
        
        return jsonify({
            'message': 'Utilisateur créé avec succès',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_verified': user.is_verified
            },
            'tokens': {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'message': 'Données invalides',
            'errors': e.messages
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Erreur lors de la création de l\'utilisateur'
        }), 500

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Connexion d'un utilisateur"""
    try:
        schema = LoginSchema()
        data = schema.load(request.json)
        
        # Trouver l'utilisateur
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not bcrypt.check_password_hash(user.password_hash, data['password']):
            return jsonify({
                'message': 'Email ou mot de passe incorrect'
            }), 401
        
        # Vérifier si le compte est actif
        if not user.is_active:
            return jsonify({
                'message': 'Compte désactivé'
            }), 401
        
        # Mettre à jour la dernière connexion
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Générer les tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Connexion réussie',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_verified': user.is_verified
            },
            'tokens': {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'message': 'Données invalides',
            'errors': e.messages
        }), 400
    except Exception as e:
        return jsonify({
            'message': 'Erreur lors de la connexion'
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Rafraîchir le token d'accès"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({
                'message': 'Utilisateur non trouvé ou inactif'
            }), 401
        
        # Générer un nouveau token d'accès
        new_access_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'access_token': new_access_token
        }), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Erreur lors du rafraîchissement du token'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Déconnexion d'un utilisateur"""
    try:
        # Dans une vraie application, on ajouterait le token à une blacklist
        # Pour l'instant, on retourne juste un message de succès
        return jsonify({
            'message': 'Déconnexion réussie'
        }), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Erreur lors de la déconnexion'
        }), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Récupérer les informations de l'utilisateur connecté"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'message': 'Utilisateur non trouvé'
            }), 404
        
        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'is_verified': user.is_verified,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Erreur lors de la récupération des informations'
        }), 500

@auth_bp.route('/verify-email/<token>', methods=['POST'])
def verify_email(token):
    """Vérifier l'email d'un utilisateur"""
    try:
        user = User.query.filter_by(verification_token=token).first()
        
        if not user:
            return jsonify({
                'message': 'Token de vérification invalide'
            }), 400
        
        if user.is_verified:
            return jsonify({
                'message': 'Email déjà vérifié'
            }), 400
        
        # Vérifier l'email
        user.is_verified = True
        user.verification_token = None
        user.verified_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Email vérifié avec succès'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Erreur lors de la vérification de l\'email'
        }), 500

@auth_bp.route('/forgot-password', methods=['POST'])
@limiter.limit("3 per minute")
def forgot_password():
    """Demander une réinitialisation de mot de passe"""
    try:
        schema = ForgotPasswordSchema()
        data = schema.load(request.json)
        
        user = User.query.filter_by(email=data['email']).first()
        
        if user:
            # Générer un token de réinitialisation
            reset_token = str(uuid.uuid4())
            user.reset_token = reset_token
            user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            
            # Envoyer l'email de réinitialisation
            try:
                email_service.send_password_reset_email(user.email, reset_token)
            except Exception as e:
                print(f"Erreur envoi email: {e}")
        
        # Toujours retourner le même message pour la sécurité
        return jsonify({
            'message': 'Si l\'email existe, un lien de réinitialisation a été envoyé'
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'message': 'Données invalides',
            'errors': e.messages
        }), 400
    except Exception as e:
        return jsonify({
            'message': 'Erreur lors de la demande de réinitialisation'
        }), 500

@auth_bp.route('/reset-password', methods=['POST'])
@limiter.limit("5 per minute")
def reset_password():
    """Réinitialiser le mot de passe"""
    try:
        schema = ResetPasswordSchema()
        data = schema.load(request.json)
        
        user = User.query.filter_by(reset_token=data['token']).first()
        
        if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
            return jsonify({
                'message': 'Token de réinitialisation invalide ou expiré'
            }), 400
        
        # Mettre à jour le mot de passe
        user.password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()
        
        return jsonify({
            'message': 'Mot de passe réinitialisé avec succès'
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'message': 'Données invalides',
            'errors': e.messages
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Erreur lors de la réinitialisation du mot de passe'
        }), 500

@auth_bp.route('/health', methods=['GET'])
def health():
    """Vérification de santé du service d'authentification"""
    return jsonify({
        'status': 'healthy',
        'service': 'auth',
        'timestamp': datetime.utcnow().isoformat()
    }), 200