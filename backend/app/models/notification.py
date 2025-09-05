"""
Modèle pour les notifications de Lucky Kangaroo
Gestion des notifications utilisateur
"""

import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy import String
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

from app import db


class NotificationType(Enum):
    """Type de notification"""
    MESSAGE = "message"
    EXCHANGE = "exchange"
    LISTING = "listing"
    REVIEW = "review"
    SYSTEM = "system"
    MARKETING = "marketing"
    SECURITY = "security"


class NotificationChannel(Enum):
    """Canal de notification"""
    IN_APP = "in_app"
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    WHATSAPP = "whatsapp"


class NotificationPriority(Enum):
    """Priorité de la notification"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Notification(db.Model):
    """
    Modèle pour les notifications
    """
    __tablename__ = 'notifications'
    
    # Identifiants
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    
    # Type et canal
    notification_type = Column(String(20), nullable=False, index=True)
    channel = Column(String(20), default=NotificationChannel.IN_APP.value, nullable=False)
    priority = Column(String(20), default=NotificationPriority.NORMAL.value, nullable=False)
    
    # Contenu
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    action_url = Column(String(500), nullable=True)
    action_text = Column(String(100), nullable=True)
    
    # Métadonnées
    notification_metadata = Column(JSON, default=dict, nullable=False)
    
    # Statut
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    is_sent = Column(Boolean, default=False, nullable=False)
    is_delivered = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    read_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True, index=True)
    
    # Relations
    user = relationship("User", back_populates="notifications")
    
    # Indexes
    __table_args__ = (
        Index('idx_notification_user_type', 'user_id', 'notification_type'),
        Index('idx_notification_user_read', 'user_id', 'is_read'),
        Index('idx_notification_created', 'created_at'),
        Index('idx_notification_expires', 'expires_at'),
    )
    
    def __init__(self, **kwargs):
        super(Notification, self).__init__(**kwargs)
        if not self.notification_metadata:
            self.notification_metadata = {}
        # Définir l'expiration par défaut (30 jours)
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(days=30)
    
    @property
    def is_expired(self):
        """Vérifier si la notification est expirée"""
        return self.expires_at and self.expires_at <= datetime.utcnow()
    
    @property
    def days_until_expiry(self):
        """Nombre de jours jusqu'à l'expiration"""
        if not self.expires_at:
            return None
        delta = self.expires_at - datetime.utcnow()
        return delta.days if delta.days > 0 else 0
    
    def mark_as_read(self):
        """Marquer comme lu"""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
            db.session.commit()
    
    def mark_as_sent(self):
        """Marquer comme envoyé"""
        if not self.is_sent:
            self.is_sent = True
            self.sent_at = datetime.utcnow()
            db.session.commit()
    
    def mark_as_delivered(self):
        """Marquer comme livré"""
        if not self.is_delivered:
            self.is_delivered = True
            self.delivered_at = datetime.utcnow()
            db.session.commit()
    
    def extend_expiry(self, days=30):
        """Prolonger l'expiration"""
        if self.expires_at:
            self.expires_at += timedelta(days=days)
        else:
            self.expires_at = datetime.utcnow() + timedelta(days=days)
        db.session.commit()
    
    def to_dict(self):
        """Convertir la notification en dictionnaire"""
        return {
            'id': str(self.id),
            'notification_type': self.notification_type,
            'channel': self.channel,
            'priority': self.priority,
            'title': self.title,
            'message': self.message,
            'action_url': self.action_url,
            'action_text': self.action_text,
            'is_read': self.is_read,
            'is_sent': self.is_sent,
            'is_delivered': self.is_delivered,
            'created_at': self.created_at.isoformat(),
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'days_until_expiry': self.days_until_expiry,
            'metadata': self.notification_metadata
        }
    
    def __repr__(self):
        return f'<Notification {self.title}>'
