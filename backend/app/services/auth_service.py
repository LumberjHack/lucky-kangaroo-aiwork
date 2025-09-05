"""
Service d'authentification pour Lucky Kangaroo
Gestion complète de l'authentification : JWT, 2FA, social auth
"""

import uuid
import secrets
import pyotp
import qrcode
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import Session
from app.models.user import User, UserStatus, UserRole
from app import db

class AuthService:
    """Service d'authentification centralisé"""
    
    def __init__(self):
        self.bcrypt = Bcrypt()
    
    def register_user(self, email: str, password: str, first_name: str, 
                     last_name: str, country: str = "CH", **kwargs) -> Tuple[User, Dict[str, str]]:
        """
        Inscription d'un nouvel utilisateur
        
        Args:
            email: Email de l'utilisateur
            password: Mot de passe en clair
            first_name: Prénom
            last_name: Nom
            country: Pays (défaut: CH)
            **kwargs: Autres champs optionnels
            
        Returns:
            Tuple[User, Dict]: Utilisateur créé et tokens JWT
        """
        # Vérifier si l'utilisateur existe déjà
        if User.query.filter_by(email=email).first():
            raise ValueError("Un utilisateur avec cet email existe déjà")
        
        # Créer l'utilisateur
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            password_hash=self.bcrypt.generate_password_hash(password).decode('utf-8'),
            first_name=first_name,
            last_name=last_name,
            country=country,
            status=UserStatus.PENDING_VERIFICATION,
            role=UserRole.USER,
            trust_score=0.0,
            ecological_score=0.0,
            total_exchanges=0,
            successful_exchanges=0,
            total_listings=0,
            active_listings=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            **kwargs
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Générer les tokens JWT
        tokens = self._generate_tokens(user)
        
        return user, tokens
    
    def authenticate_user(self, email: str, password: str) -> Tuple[Optional[User], Dict[str, str]]:
        """
        Authentification d'un utilisateur
        
        Args:
            email: Email de l'utilisateur
            password: Mot de passe en clair
            
        Returns:
            Tuple[Optional[User], Dict]: Utilisateur et tokens si succès, None sinon
        """
        user = User.query.filter_by(email=email).first()
        
        if not user or not self.bcrypt.check_password_hash(user.password_hash, password):
            return None, {}
        
        # Vérifier le statut de l'utilisateur
        if user.status == UserStatus.SUSPENDED:
            raise ValueError("Votre compte a été suspendu")
        
        if user.status == UserStatus.PENDING_VERIFICATION:
            raise ValueError("Veuillez vérifier votre email avant de vous connecter")
        
        # Mettre à jour la dernière activité
        user.last_login = datetime.utcnow()
        user.last_activity = datetime.utcnow()
        db.session.commit()
        
        # Générer les tokens JWT
        tokens = self._generate_tokens(user)
        
        return user, tokens
    
    def verify_email(self, token: str) -> bool:
        """
        Vérification de l'email avec un token
        
        Args:
            token: Token de vérification
            
        Returns:
            bool: True si succès
        """
        try:
            # Décoder le token (simplifié pour l'exemple)
            # En production, utiliser un système de tokens sécurisé
            user_id = token  # Simplification
            
            user = User.query.get(user_id)
            if not user:
                return False
            
            user.email_verified = True
            user.status = UserStatus.ACTIVE
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return True
            
        except Exception:
            return False
    
    def reset_password_request(self, email: str) -> bool:
        """
        Demande de réinitialisation de mot de passe
        
        Args:
            email: Email de l'utilisateur
            
        Returns:
            bool: True si l'email existe
        """
        user = User.query.filter_by(email=email).first()
        if not user:
            return False  # Ne pas révéler si l'email existe
        
        # Générer un token de réinitialisation
        reset_token = secrets.token_urlsafe(32)
        
        # Stocker le token (en production, utiliser Redis ou base de données)
        # Pour l'exemple, on stocke dans les métadonnées utilisateur
        user.preferences = {
            **user.preferences,
            'reset_token': reset_token,
            'reset_token_expires': (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Envoyer l'email (à implémenter)
        # self._send_reset_email(user.email, reset_token)
        
        return True
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """
        Réinitialisation du mot de passe
        
        Args:
            token: Token de réinitialisation
            new_password: Nouveau mot de passe
            
        Returns:
            bool: True si succès
        """
        # Trouver l'utilisateur avec ce token
        users = User.query.all()
        user = None
        
        for u in users:
            if (u.preferences.get('reset_token') == token and 
                u.preferences.get('reset_token_expires') and
                datetime.fromisoformat(u.preferences['reset_token_expires']) > datetime.utcnow()):
                user = u
                break
        
        if not user:
            return False
        
        # Mettre à jour le mot de passe
        user.password_hash = self.bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.preferences = {k: v for k, v in user.preferences.items() 
                          if k not in ['reset_token', 'reset_token_expires']}
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return True
    
    def setup_2fa(self, user_id: str) -> Dict[str, str]:
        """
        Configuration de l'authentification à deux facteurs
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dict: Informations pour configurer 2FA
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError("Utilisateur non trouvé")
        
        # Générer une clé secrète
        secret = pyotp.random_base32()
        
        # Créer l'URL TOTP
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name="Lucky Kangaroo"
        )
        
        # Générer le QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        # Stocker temporairement la clé secrète
        user.two_factor_secret = secret
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {
            'secret': secret,
            'qr_code_url': totp_uri,
            'backup_codes': self._generate_backup_codes()
        }
    
    def verify_2fa(self, user_id: str, token: str) -> bool:
        """
        Vérification du code 2FA
        
        Args:
            user_id: ID de l'utilisateur
            token: Code 2FA
            
        Returns:
            bool: True si valide
        """
        user = User.query.get(user_id)
        if not user or not user.two_factor_secret:
            return False
        
        totp = pyotp.TOTP(user.two_factor_secret)
        return totp.verify(token, valid_window=1)
    
    def enable_2fa(self, user_id: str, token: str) -> bool:
        """
        Activation de l'authentification à deux facteurs
        
        Args:
            user_id: ID de l'utilisateur
            token: Code de vérification
            
        Returns:
            bool: True si succès
        """
        if not self.verify_2fa(user_id, token):
            return False
        
        user = User.query.get(user_id)
        user.two_factor_enabled = True
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return True
    
    def disable_2fa(self, user_id: str, password: str) -> bool:
        """
        Désactivation de l'authentification à deux facteurs
        
        Args:
            user_id: ID de l'utilisateur
            password: Mot de passe de confirmation
            
        Returns:
            bool: True si succès
        """
        user = User.query.get(user_id)
        if not user or not self.bcrypt.check_password_hash(user.password_hash, password):
            return False
        
        user.two_factor_enabled = False
        user.two_factor_secret = None
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return True
    
    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Renouvellement du token d'accès
        
        Args:
            refresh_token: Token de rafraîchissement
            
        Returns:
            Dict: Nouveaux tokens
        """
        try:
            # Décoder le refresh token
            decoded = decode_token(refresh_token)
            user_id = decoded['sub']
            
            user = User.query.get(user_id)
            if not user or user.status != UserStatus.ACTIVE:
                raise ValueError("Utilisateur invalide")
            
            # Générer de nouveaux tokens
            return self._generate_tokens(user)
            
        except Exception:
            raise ValueError("Token de rafraîchissement invalide")
    
    def _generate_tokens(self, user: User) -> Dict[str, str]:
        """
        Génération des tokens JWT
        
        Args:
            user: Utilisateur
            
        Returns:
            Dict: Tokens d'accès et de rafraîchissement
        """
        # Données supplémentaires pour le token
        additional_claims = {
            'user_id': user.id,
            'email': user.email,
            'role': user.role.value,
            'trust_score': user.trust_score,
            'two_factor_enabled': user.two_factor_enabled
        }
        
        # Créer les tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims=additional_claims,
            expires_delta=timedelta(hours=1)
        )
        
        refresh_token = create_refresh_token(
            identity=user.id,
            expires_delta=timedelta(days=30)
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 3600
        }
    
    def _generate_backup_codes(self) -> list:
        """
        Génération de codes de sauvegarde pour 2FA
        
        Returns:
            list: Codes de sauvegarde
        """
        return [secrets.token_hex(4).upper() for _ in range(10)]
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupération du profil utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dict: Profil utilisateur
        """
        user = User.query.get(user_id)
        if not user:
            return None
        
        return {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'bio': user.bio,
            'profile_picture': user.profile_picture,
            'country': user.country,
            'city': user.city,
            'trust_score': user.trust_score,
            'ecological_score': user.ecological_score,
            'total_exchanges': user.total_exchanges,
            'successful_exchanges': user.successful_exchanges,
            'total_listings': user.total_listings,
            'active_listings': user.active_listings,
            'created_at': user.created_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'two_factor_enabled': user.two_factor_enabled,
            'is_kyc_verified': user.is_kyc_verified
        }
    
    def update_user_profile(self, user_id: str, **kwargs) -> bool:
        """
        Mise à jour du profil utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            **kwargs: Champs à mettre à jour
            
        Returns:
            bool: True si succès
        """
        user = User.query.get(user_id)
        if not user:
            return False
        
        # Champs autorisés pour la mise à jour
        allowed_fields = [
            'username', 'first_name', 'last_name', 'bio', 'profile_picture',
            'city', 'postal_code', 'language', 'currency', 'preferences',
            'notification_settings', 'privacy_settings'
        ]
        
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(user, field):
                setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return True