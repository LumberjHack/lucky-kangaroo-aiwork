"""
Modèle pour les avis et évaluations de Lucky Kangaroo
Système de notation et de confiance
"""

import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey, Index, CheckConstraint
from sqlalchemy import String
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

from app import db


class ReviewType(Enum):
    """Type d'avis"""
    EXCHANGE = "exchange"
    LISTING = "listing"
    USER = "user"


class Review(db.Model):
    """
    Modèle pour les avis
    """
    __tablename__ = 'reviews'
    
    # Identifiants
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    reviewer_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    reviewee_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    
    # Relations avec d'autres entités
    listing_id = Column(String(36), ForeignKey('listings.id'), nullable=True, index=True)
    exchange_id = Column(String(36), ForeignKey('exchanges.id'), nullable=True, index=True)
    
    # Type et contenu
    review_type = Column(String(20), default=ReviewType.EXCHANGE.value, nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 étoiles
    title = Column(String(200), nullable=True)
    comment = Column(Text, nullable=True)
    
    # Aspects spécifiques (pour les échanges)
    communication_rating = Column(Integer, nullable=True)  # 1-5
    item_condition_rating = Column(Integer, nullable=True)  # 1-5
    meeting_rating = Column(Integer, nullable=True)  # 1-5
    overall_experience_rating = Column(Integer, nullable=True)  # 1-5
    
    # Statut
    is_verified = Column(Boolean, default=False, nullable=False)
    is_public = Column(Boolean, default=True, nullable=False)
    is_anonymous = Column(Boolean, default=False, nullable=False)
    
    # Métadonnées
    review_metadata = Column(JSON, default=dict, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relations
    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="reviews_given")
    reviewee = relationship("User", foreign_keys=[reviewee_id], back_populates="reviews_received")
    listing = relationship("Listing", back_populates="reviews")
    exchange = relationship("Exchange")
    
    # Indexes
    __table_args__ = (
        Index('idx_review_reviewer', 'reviewer_id'),
        Index('idx_review_reviewee', 'reviewee_id'),
        Index('idx_review_listing', 'listing_id'),
        Index('idx_review_exchange', 'exchange_id'),
        Index('idx_review_type', 'review_type'),
        Index('idx_review_rating', 'rating'),
        Index('idx_review_created', 'created_at'),
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        CheckConstraint('communication_rating >= 1 AND communication_rating <= 5', name='check_communication_rating_range'),
        CheckConstraint('item_condition_rating >= 1 AND item_condition_rating <= 5', name='check_item_condition_rating_range'),
        CheckConstraint('meeting_rating >= 1 AND meeting_rating <= 5', name='check_meeting_rating_range'),
        CheckConstraint('overall_experience_rating >= 1 AND overall_experience_rating <= 5', name='check_overall_experience_rating_range'),
    )
    
    def __init__(self, **kwargs):
        super(Review, self).__init__(**kwargs)
        if not self.review_metadata:
            self.review_metadata = {}
    
    @property
    def average_rating(self):
        """Note moyenne si plusieurs aspects sont évalués"""
        ratings = [
            self.rating,
            self.communication_rating,
            self.item_condition_rating,
            self.meeting_rating,
            self.overall_experience_rating
        ]
        valid_ratings = [r for r in ratings if r is not None]
        return sum(valid_ratings) / len(valid_ratings) if valid_ratings else 0
    
    @property
    def rating_display(self):
        """Affichage de la note avec étoiles"""
        return "★" * self.rating + "☆" * (5 - self.rating)
    
    def verify(self):
        """Vérifier l'avis"""
        self.is_verified = True
        db.session.commit()
    
    def make_public(self):
        """Rendre l'avis public"""
        self.is_public = True
        db.session.commit()
    
    def make_private(self):
        """Rendre l'avis privé"""
        self.is_public = False
        db.session.commit()
    
    def to_dict(self, include_private=False):
        """Convertir l'avis en dictionnaire"""
        data = {
            'id': str(self.id),
            'review_type': self.review_type,
            'rating': self.rating,
            'rating_display': self.rating_display,
            'average_rating': self.average_rating,
            'title': self.title,
            'comment': self.comment,
            'is_verified': self.is_verified,
            'is_public': self.is_public,
            'is_anonymous': self.is_anonymous,
            'created_at': self.created_at.isoformat(),
            'reviewer': {
                'id': str(self.reviewer.id),
                'username': self.reviewer.username if not self.is_anonymous else 'Utilisateur anonyme',
                'display_name': self.reviewer.display_name if not self.is_anonymous else 'Utilisateur anonyme',
                'profile_picture': self.reviewer.profile_picture if not self.is_anonymous else None
            },
            'reviewee': {
                'id': str(self.reviewee.id),
                'username': self.reviewee.username,
                'display_name': self.reviewee.display_name,
                'profile_picture': self.reviewee.profile_picture
            }
        }
        
        if self.listing:
            data['listing'] = {
                'id': str(self.listing.id),
                'title': self.listing.title
            }
        
        if self.exchange:
            data['exchange'] = {
                'id': str(self.exchange.id),
                'title': self.exchange.title
            }
        
        if include_private:
            data.update({
                'communication_rating': self.communication_rating,
                'item_condition_rating': self.item_condition_rating,
                'meeting_rating': self.meeting_rating,
                'overall_experience_rating': self.overall_experience_rating,
                'metadata': self.review_metadata,
                'updated_at': self.updated_at.isoformat()
            })
        
        return data
    
    @validates('rating', 'communication_rating', 'item_condition_rating', 'meeting_rating', 'overall_experience_rating')
    def validate_rating(self, key, rating):
        """Valider les notes"""
        if rating is not None and not (1 <= rating <= 5):
            raise ValueError('Rating must be between 1 and 5')
        return rating
    
    def __repr__(self):
        return f'<Review {self.rating}★ by {self.reviewer.username}>'
