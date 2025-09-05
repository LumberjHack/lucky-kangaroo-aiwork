"""
Modèles pour les badges et récompenses de Lucky Kangaroo
Système de gamification
"""

import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy import String
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

from app import db


class BadgeType(Enum):
    """Type de badge"""
    ACTIVITY = "activity"
    ECOLOGICAL = "ecological"
    SOCIAL = "social"
    QUALITY = "quality"
    GEOGRAPHIC = "geographic"
    TEMPORAL = "temporal"
    SPECIAL = "special"


class BadgeRarity(Enum):
    """Rareté du badge"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class Badge(db.Model):
    """
    Modèle pour les badges
    """
    __tablename__ = 'badges'
    
    # Identifiants
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Informations du badge
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    icon = Column(String(100), nullable=True)
    color = Column(String(7), nullable=True)  # Code couleur hex
    
    # Type et rareté
    badge_type = Column(String(20), nullable=False, index=True)
    rarity = Column(String(20), default=BadgeRarity.COMMON.value, nullable=False)
    
    # Critères d'obtention
    criteria = Column(JSON, default=dict, nullable=False)
    points_required = Column(Integer, default=0, nullable=False)
    
    # Statut
    is_active = Column(Boolean, default=True, nullable=False)
    is_hidden = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relations
    user_badges = relationship("UserBadge", back_populates="badge", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_badge_type', 'badge_type'),
        Index('idx_badge_rarity', 'rarity'),
        Index('idx_badge_active', 'is_active'),
    )
    
    def __init__(self, **kwargs):
        super(Badge, self).__init__(**kwargs)
        if not self.criteria:
            self.criteria = {}
    
    @property
    def user_count(self):
        """Nombre d'utilisateurs ayant ce badge"""
        return len([ub for ub in self.user_badges if ub.is_active])
    
    def to_dict(self):
        """Convertir le badge en dictionnaire"""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'badge_type': self.badge_type,
            'rarity': self.rarity,
            'criteria': self.criteria,
            'points_required': self.points_required,
            'is_active': self.is_active,
            'is_hidden': self.is_hidden,
            'user_count': self.user_count,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Badge {self.name}>'


class UserBadge(db.Model):
    """
    Association entre utilisateurs et badges
    """
    __tablename__ = 'user_badges'
    
    # Identifiants
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    badge_id = Column(String(36), ForeignKey('badges.id'), nullable=False, index=True)
    
    # Statut
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Métadonnées
    badge_metadata = Column(JSON, default=dict, nullable=False)
    
    # Timestamps
    earned_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relations
    user = relationship("User", back_populates="badges")
    badge = relationship("Badge", back_populates="user_badges")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_badge_user', 'user_id'),
        Index('idx_user_badge_badge', 'badge_id'),
        Index('idx_user_badge_active', 'is_active'),
        Index('idx_user_badge_earned', 'earned_at'),
    )
    
    def __init__(self, **kwargs):
        super(UserBadge, self).__init__(**kwargs)
        if not self.badge_metadata:
            self.badge_metadata = {}
    
    def to_dict(self):
        """Convertir l'association en dictionnaire"""
        return {
            'id': str(self.id),
            'is_active': self.is_active,
            'earned_at': self.earned_at.isoformat(),
            'metadata': self.badge_metadata,
            'badge': self.badge.to_dict()
        }
    
    def __repr__(self):
        return f'<UserBadge {self.user.username} - {self.badge.name}>'
