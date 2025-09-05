"""
Blueprint d'authentification pour Lucky Kangaroo
Gestion de l'inscription, connexion, et authentification
"""

import uuid
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity, get_jwt, verify_jwt_in_request
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import Schema, fields, validate, ValidationError
import secrets
import string

from app import db, bcrypt, mail
from app.models.user import User, UserStatus, UserRole
from app.models.notification import Notification, NotificationType, NotificationChannel

# Créer le blueprint
auth_bp = Blueprint('auth', __name__)

# Limiter de taux
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

# Schémas de validation
class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    first_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    last_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    date_of_birth = fields.Date(required=False)
    gender = fields.Str(required=False, validate=validate.OneOf(['male', 'female', 'other', 'prefer_not_to_say']))
    city = fields.Str(required=False, validate=validate.Length(max=100))
    postal_code = fields.Str(required=False, validate=validate.Length(max=20))
    country = fields.Str(required=False, default='Switzerland')
    language = fields.Str(required=False, default='fr')
    currency = fields.Str(required=False, default='CHF')
    accept_terms = fields.Bool(required=True, validate=validate.Equal(True))

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    remember_me = fields.Bool(required=False, default=False)

class ForgotPasswordSchema(Schema):
    email = fields.Email(required=True)

class ResetPasswordSchema(Schema):
    token = fields.Str(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))

class ChangePasswordSchema(Schema):
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=8))

# Instancier les schémas
register_schema = RegisterSchema()
login_schema = LoginSchema()
forgot_password_schema = ForgotPasswordSchema()
reset_password_schema = ResetPasswordSchema()
change_password_schema = ChangePasswordSchema()

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """Inscription d'un nouvel utilisateur"""
    try:
        # Valider les données
        data = register_schema.load(request.json)
        
        # Vérifier si l'email existe déjà
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email déjà utilisé'}), 400
        
        # Créer l'utilisateur
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            date_of_birth=data.get('date_of_birth'),
            gender=data.get('gender'),
            city=data.get('city'),
            postal_code=data.get('postal_code'),
            country=data.get('country', 'Switzerland'),
            language=data.get('language', 'fr'),
            currency=data.get('currency', 'CHF')
        )
        
        # Définir le mot de passe
        user.password = data['password']
        
        # Générer un nom d'utilisateur unique
        user.generate_username()
        
        # Sauvegarder en base
        db.session.add(user)
        db.session.commit()
        
        # Générer les tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        # Envoyer l'email de vérification
        send_verification_email(user)
        
        # Créer une notification de bienvenue
        notification = Notification(
            user_id=user.id,
            notification_type=NotificationType.SYSTEM.value,
            title="Bienvenue sur Lucky Kangaroo !",
            message="Votre compte a été créé avec succès. Vérifiez votre email pour activer votre compte.",
            action_url="/auth/verify-email"
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'message': 'Compte créé avec succès',
            'user': user.to_dict(include_private=True),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Données invalides', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors de l'inscription: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Connexion d'un utilisateur"""
    try:
        # Valider les données
        data = login_schema.load(request.json)
        
        # Trouver l'utilisateur
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
        
        # Vérifier le statut de l'utilisateur
        if user.status == UserStatus.SUSPENDED.value:
            return jsonify({'error': 'Compte suspendu'}), 403
        
        if user.status == UserStatus.BANNED.value:
            return jsonify({'error': 'Compte banni'}), 403
        
        # Mettre à jour la dernière connexion
        user.last_login = datetime.utcnow()
        user.update_last_activity()
        
        # Générer les tokens
        expires_delta = timedelta(days=30) if data.get('remember_me') else timedelta(hours=1)
        access_token = create_access_token(identity=str(user.id), expires_delta=expires_delta)
        refresh_token = create_refresh_token(identity=str(user.id))
        
        db.session.commit()
        
        return jsonify({
            'message': 'Connexion réussie',
            'user': user.to_dict(include_private=True),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Données invalides', 'details': e.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la connexion: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Rafraîchir le token d'accès"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.status != UserStatus.ACTIVE.value:
            return jsonify({'error': 'Utilisateur non trouvé ou inactif'}), 401
        
        # Générer un nouveau token d'accès
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors du rafraîchissement: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Déconnexion d'un utilisateur"""
    try:
        # Ajouter le token à la liste noire (si implémenté)
        jti = get_jwt()['jti']
        # Ici, vous pourriez ajouter le jti à Redis pour invalider le token
        
        return jsonify({'message': 'Déconnexion réussie'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la déconnexion: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@auth_bp.route('/verify-email', methods=['POST'])
@limiter.limit("5 per minute")
def verify_email():
    """Vérifier l'email d'un utilisateur"""
    try:
        token = request.json.get('token')
        if not token:
            return jsonify({'error': 'Token requis'}), 400
        
        # Ici, vous devriez vérifier le token de vérification email
        # Pour l'instant, on simule la vérification
        user_id = request.json.get('user_id')
        if not user_id:
            return jsonify({'error': 'ID utilisateur requis'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        if user.email_verified:
            return jsonify({'error': 'Email déjà vérifié'}), 400
        
        # Marquer l'email comme vérifié
        user.email_verified = True
        user.status = UserStatus.ACTIVE.value
        
        db.session.commit()
        
        return jsonify({'message': 'Email vérifié avec succès'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la vérification email: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@auth_bp.route('/resend-verification', methods=['POST'])
@limiter.limit("3 per minute")
def resend_verification():
    """Renvoyer l'email de vérification"""
    try:
        email = request.json.get('email')
        if not email:
            return jsonify({'error': 'Email requis'}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        if user.email_verified:
            return jsonify({'error': 'Email déjà vérifié'}), 400
        
        # Renvoyer l'email de vérification
        send_verification_email(user)
        
        return jsonify({'message': 'Email de vérification renvoyé'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors du renvoi de vérification: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
@limiter.limit("5 per minute")
def forgot_password():
    """Demander une réinitialisation de mot de passe"""
    try:
        # Valider les données
        data = forgot_password_schema.load(request.json)
        
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            # Ne pas révéler si l'email existe ou non
            return jsonify({'message': 'Si cet email existe, un lien de réinitialisation a été envoyé'}), 200
        
        # Générer un token de réinitialisation
        reset_token = generate_reset_token()
        
        # Stocker le token (dans la base ou Redis)
        user.metadata['reset_token'] = reset_token
        user.metadata['reset_token_expires'] = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        
        db.session.commit()
        
        # Envoyer l'email de réinitialisation
        send_reset_password_email(user, reset_token)
        
        return jsonify({'message': 'Si cet email existe, un lien de réinitialisation a été envoyé'}), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Données invalides', 'details': e.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la demande de réinitialisation: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
@limiter.limit("5 per minute")
def reset_password():
    """Réinitialiser le mot de passe"""
    try:
        # Valider les données
        data = reset_password_schema.load(request.json)
        
        # Trouver l'utilisateur avec le token
        user = User.query.filter(
            User.metadata['reset_token'].astext == data['token']
        ).first()
        
        if not user:
            return jsonify({'error': 'Token invalide ou expiré'}), 400
        
        # Vérifier l'expiration du token
        token_expires = user.metadata.get('reset_token_expires')
        if token_expires and datetime.fromisoformat(token_expires) < datetime.utcnow():
            return jsonify({'error': 'Token expiré'}), 400
        
        # Mettre à jour le mot de passe
        user.password = data['password']
        
        # Supprimer le token
        user.metadata.pop('reset_token', None)
        user.metadata.pop('reset_token_expires', None)
        
        db.session.commit()
        
        return jsonify({'message': 'Mot de passe réinitialisé avec succès'}), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Données invalides', 'details': e.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la réinitialisation: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
@limiter.limit("5 per minute")
def change_password():
    """Changer le mot de passe"""
    try:
        # Valider les données
        data = change_password_schema.load(request.json)
        
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Vérifier le mot de passe actuel
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Mot de passe actuel incorrect'}), 400
        
        # Mettre à jour le mot de passe
        user.password = data['new_password']
        
        db.session.commit()
        
        return jsonify({'message': 'Mot de passe modifié avec succès'}), 200
        
    except ValidationError as e:
        return jsonify({'error': 'Données invalides', 'details': e.messages}), 400
    except Exception as e:
        current_app.logger.error(f"Erreur lors du changement de mot de passe: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Obtenir les informations de l'utilisateur connecté"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Mettre à jour la dernière activité
        user.update_last_activity()
        
        return jsonify({
            'user': user.to_dict(include_private=True)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération du profil: {str(e)}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

# Fonctions utilitaires
def send_verification_email(user):
    """Envoyer l'email de vérification"""
    try:
        # Ici, vous implémenteriez l'envoi d'email réel
        # avec Flask-Mail ou un service externe
        current_app.logger.info(f"Email de vérification envoyé à {user.email}")
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'envoi de l'email: {str(e)}")

def send_reset_password_email(user, token):
    """Envoyer l'email de réinitialisation de mot de passe"""
    try:
        # Ici, vous implémenteriez l'envoi d'email réel
        current_app.logger.info(f"Email de réinitialisation envoyé à {user.email}")
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'envoi de l'email: {str(e)}")

def generate_reset_token():
    """Générer un token de réinitialisation"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
