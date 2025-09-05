"""
Modèle User pour Lucky Kangaroo
Gestion des utilisateurs avec authentification, profil et préférences
"""

import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Float, JSON, ForeignKey, Index
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
import secrets
import string

from app import db, bcrypt


class UserStatus(Enum):
    """Statut de l'utilisateur"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"
    PENDING_VERIFICATION = "pending_verification"


class UserRole(Enum):
    """Rôle de l'utilisateur"""
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class User(UserMixin, db.Model):
    """
    Modèle utilisateur avec authentification, profil et préférences
    """
    __tablename__ = 'users'
    
    # Identifiants
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=True, index=True)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    
    # Authentification
    password_hash = Column(String(255), nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    phone_verified = Column(Boolean, default=False, nullable=False)
    two_factor_enabled = Column(Boolean, default=False, nullable=False)
    two_factor_secret = Column(String(32), nullable=True)
    
    # Profil personnel
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String(20), nullable=True)  # male, female, other, prefer_not_to_say
    bio = Column(Text, nullable=True)
    profile_picture = Column(String(500), nullable=True)
    cover_picture = Column(String(500), nullable=True)
    
    # Localisation
    country = Column(String(100), default='Switzerland', nullable=False)
    city = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timezone = Column(String(50), default='Europe/Zurich', nullable=False)
    language = Column(String(10), default='fr', nullable=False)
    currency = Column(String(3), default='CHF', nullable=False)
    
    # Préférences
    preferences = Column(JSON, default=dict, nullable=False)
    notification_settings = Column(JSON, default=dict, nullable=False)
    privacy_settings = Column(JSON, default=dict, nullable=False)
    
    # Statut et rôles
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_kyc_verified = Column(Boolean, default=False, nullable=False)
    kyc_verification_date = Column(DateTime, nullable=True)
    
    # Scores et statistiques
    trust_score = Column(Float, default=5.0, nullable=False)  # 0-10
    ecological_score = Column(Float, default=0.0, nullable=False)
    total_exchanges = Column(Integer, default=0, nullable=False)
    successful_exchanges = Column(Integer, default=0, nullable=False)
    total_listings = Column(Integer, default=0, nullable=False)
    active_listings = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, default=func.now(), nullable=False)
    
    # Relations
    listings = relationship("Listing", back_populates="user", cascade="all, delete-orphan")
    exchanges_as_owner = relationship("Exchange", foreign_keys="Exchange.owner_id", back_populates="owner")
    exchanges_as_participant = relationship("ExchangeParticipant", back_populates="user")
    reviews_given = relationship("Review", foreign_keys="Review.reviewer_id", back_populates="reviewer")
    reviews_received = relationship("Review", foreign_keys="Review.reviewee_id", back_populates="reviewee")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    badges = relationship("UserBadge", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user")
    chat_participations = relationship("ChatParticipant", back_populates="user")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_username', 'username'),
        Index('idx_user_phone', 'phone'),
        Index('idx_user_status', 'status'),
        Index('idx_user_created_at', 'created_at'),
        Index('idx_user_location', 'latitude', 'longitude'),
        Index('idx_user_trust_score', 'trust_score'),
    )
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.preferences:
            self.preferences = self._default_preferences()
        if not self.notification_settings:
            self.notification_settings = self._default_notification_settings()
        if not self.privacy_settings:
            self.privacy_settings = self._default_privacy_settings()
    
    def _default_preferences(self):
        """Préférences par défaut de l'utilisateur"""
        return {
            'search_radius': 50,  # km
            'max_distance': 100,  # km
            'preferred_categories': [],
            'excluded_categories': [],
            'price_range': {'min': 0, 'max': 10000},
            'condition_preferences': ['excellent', 'very_good', 'good'],
            'exchange_types': ['direct', 'chain'],
            'auto_translate': True,
            'theme': 'light',
            'language': 'fr'
        }
    
    def _default_notification_settings(self):
        """Paramètres de notification par défaut"""
        return {
            'email_notifications': True,
            'push_notifications': True,
            'sms_notifications': False,
            'whatsapp_notifications': False,
            'new_messages': True,
            'exchange_updates': True,
            'new_listings': False,
            'price_drops': True,
            'weekly_summary': True,
            'marketing_emails': False
        }
    
    def _default_privacy_settings(self):
        """Paramètres de confidentialité par défaut"""
        return {
            'profile_visibility': 'public',
            'show_email': False,
            'show_phone': False,
            'show_location': 'city_only',
            'show_last_seen': True,
            'allow_direct_messages': True,
            'show_online_status': True,
            'data_sharing': False
        }
    
    @property
    def password(self):
        """Propriété password (lecture seule)"""
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        """Définir le mot de passe avec hachage"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Vérifier le mot de passe"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        """Nom complet de l'utilisateur"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def display_name(self):
        """Nom d'affichage (username ou nom complet)"""
        return self.username or self.full_name
    
    @property
    def is_active(self):
        """Vérifier si l'utilisateur est actif"""
        return self.status == UserStatus.ACTIVE.value
    
    @property
    def is_admin(self):
        """Vérifier si l'utilisateur est administrateur"""
        return self.role in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]
    
    @property
    def is_moderator(self):
        """Vérifier si l'utilisateur est modérateur"""
        return self.role in [UserRole.MODERATOR.value, UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]
    
    @property
    def success_rate(self):
        """Taux de succès des échanges"""
        if self.total_exchanges == 0:
            return 0.0
        return (self.successful_exchanges / self.total_exchanges) * 100
    
    @property
    def age(self):
        """Âge de l'utilisateur"""
        if not self.date_of_birth:
            return None
        today = datetime.utcnow().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    def generate_username(self):
        """Générer un nom d'utilisateur unique basé sur le nom"""
        if self.username:
            return self.username
        
        base_username = f"{self.first_name.lower()}.{self.last_name.lower()}"
        username = base_username
        
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1
        
        self.username = username
        return username
    
    def generate_two_factor_secret(self):
        """Générer un secret pour l'authentification à deux facteurs"""
        self.two_factor_secret = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(32))
        return self.two_factor_secret
    
    def update_last_activity(self):
        """Mettre à jour la dernière activité"""
        self.last_activity = func.now()
        db.session.commit()
    
    def update_trust_score(self, new_score):
        """Mettre à jour le score de confiance"""
        # Calculer la moyenne pondérée avec l'historique
        old_score = self.trust_score
        total_exchanges = self.total_exchanges
        
        if total_exchanges == 0:
            self.trust_score = new_score
        else:
            # Moyenne pondérée (plus d'historique = moins de changement)
            weight = min(0.3, 1.0 / (total_exchanges + 1))
            self.trust_score = old_score * (1 - weight) + new_score * weight
        
        db.session.commit()
    
    def add_badge(self, badge_id):
        """Ajouter un badge à l'utilisateur"""
        from .badge import UserBadge
        existing_badge = UserBadge.query.filter_by(user_id=self.id, badge_id=badge_id).first()
        if not existing_badge:
            user_badge = UserBadge(user_id=self.id, badge_id=badge_id)
            db.session.add(user_badge)
            db.session.commit()
    
    def get_location_string(self):
        """Obtenir la localisation sous forme de chaîne"""
        parts = []
        if self.city:
            parts.append(self.city)
        if self.postal_code:
            parts.append(self.postal_code)
        if self.country and self.country != 'Switzerland':
            parts.append(self.country)
        return ', '.join(parts) if parts else 'Localisation non spécifiée'
    
    def to_dict(self, include_private=False):
        """Convertir l'utilisateur en dictionnaire"""
        data = {
            'id': str(self.id),
            'email': self.email if include_private else None,
            'username': self.username,
            'full_name': self.full_name,
            'display_name': self.display_name,
            'profile_picture': self.profile_picture,
            'bio': self.bio,
            'location': self.get_location_string(),
            'trust_score': self.trust_score,
            'ecological_score': self.ecological_score,
            'total_exchanges': self.total_exchanges,
            'success_rate': self.success_rate,
            'is_kyc_verified': self.is_kyc_verified,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }
        
        if include_private:
            data.update({
                'phone': self.phone,
                'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
                'gender': self.gender,
                'preferences': self.preferences,
                'notification_settings': self.notification_settings,
                'privacy_settings': self.privacy_settings,
                'status': self.status,
                'role': self.role,
                'email_verified': self.email_verified,
                'phone_verified': self.phone_verified,
                'two_factor_enabled': self.two_factor_enabled,
                'updated_at': self.updated_at.isoformat(),
                'last_login': self.last_login.isoformat() if self.last_login else None
            })
        
        return data
    
    @validates('email')
    def validate_email(self, key, email):
        """Valider l'email"""
        if not email or '@' not in email:
            raise ValueError('Invalid email address')
        return email.lower()
    
    @validates('trust_score')
    def validate_trust_score(self, key, score):
        """Valider le score de confiance"""
        if not 0 <= score <= 10:
            raise ValueError('Trust score must be between 0 and 10')
        return score
    
    def __repr__(self):
        return f'<User {self.email}>'


# Import UserMixin pour Flask-Login
try:
    from flask_login import UserMixin
except ImportError:
    class UserMixin:
        """Fallback UserMixin si Flask-Login n'est pas disponible"""
        pass
