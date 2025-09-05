"""
Modèles pour les échanges de Lucky Kangaroo
Gestion des échanges directs et en chaîne
"""

import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Float, JSON, ForeignKey, Index, CheckConstraint
from sqlalchemy import String
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

from app import db


class ExchangeStatus(Enum):
    """Statut de l'échange"""
    PENDING = "pending"  # En attente d'acceptation
    ACCEPTED = "accepted"  # Accepté par le propriétaire
    IN_PROGRESS = "in_progress"  # En cours
    MEETING_SCHEDULED = "meeting_scheduled"  # Rendez-vous planifié
    COMPLETED = "completed"  # Terminé avec succès
    CANCELLED = "cancelled"  # Annulé
    DISPUTED = "disputed"  # En litige
    EXPIRED = "expired"  # Expiré


class ExchangeType(Enum):
    """Type d'échange"""
    DIRECT = "direct"  # Échange direct A ↔ B
    CHAIN = "chain"  # Chaîne d'échange A → B → C → A


class ExchangeParticipantRole(Enum):
    """Rôle du participant dans l'échange"""
    INITIATOR = "initiator"  # Initiateur de l'échange
    OWNER = "owner"  # Propriétaire de l'objet/service
    RECEIVER = "receiver"  # Receveur de l'objet/service
    INTERMEDIARY = "intermediary"  # Intermédiaire dans une chaîne


class Exchange(db.Model):
    """
    Modèle principal pour les échanges
    """
    __tablename__ = 'exchanges'
    
    # Identifiants
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    listing_id = Column(String(36), ForeignKey('listings.id'), nullable=False, index=True)
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    
    # Type et statut
    exchange_type = Column(String(20), default=ExchangeType.DIRECT.value, nullable=False)
    status = Column(String(20), default=ExchangeStatus.PENDING.value, nullable=False, index=True)
    
    # Informations de l'échange
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    proposed_items = Column(Text, nullable=True)  # Objets/services proposés
    proposed_value = Column(Float, nullable=True)  # Valeur proposée
    currency = Column(String(3), default='CHF', nullable=False)
    
    # Localisation de l'échange
    meeting_location = Column(String(200), nullable=True)
    meeting_latitude = Column(Float, nullable=True)
    meeting_longitude = Column(Float, nullable=True)
    meeting_address = Column(Text, nullable=True)
    meeting_instructions = Column(Text, nullable=True)
    
    # Dates importantes
    proposed_meeting_date = Column(DateTime, nullable=True)
    confirmed_meeting_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True, index=True)
    
    # Évaluations mutuelles
    owner_rating = Column(Integer, nullable=True)  # Note donnée par le propriétaire
    owner_review = Column(Text, nullable=True)  # Avis du propriétaire
    participant_rating = Column(Integer, nullable=True)  # Note donnée par le participant
    participant_review = Column(Text, nullable=True)  # Avis du participant
    
    # Métadonnées
    exchange_metadata = Column(JSON, default=dict, nullable=False)
    dispute_reason = Column(Text, nullable=True)
    dispute_resolution = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relations
    listing = relationship("Listing", back_populates="exchanges")
    owner = relationship("User", foreign_keys=[owner_id], back_populates="exchanges_as_owner")
    participants = relationship("ExchangeParticipant", back_populates="exchange", cascade="all, delete-orphan")
    messages = relationship("ExchangeMessage", back_populates="exchange", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_exchange_listing_status', 'listing_id', 'status'),
        Index('idx_exchange_owner_status', 'owner_id', 'status'),
        Index('idx_exchange_created', 'created_at'),
        Index('idx_exchange_expires', 'expires_at'),
        CheckConstraint('owner_rating >= 1 AND owner_rating <= 5', name='check_owner_rating_range'),
        CheckConstraint('participant_rating >= 1 AND participant_rating <= 5', name='check_participant_rating_range'),
        CheckConstraint('proposed_value >= 0', name='check_proposed_value_positive'),
    )
    
    def __init__(self, **kwargs):
        super(Exchange, self).__init__(**kwargs)
        if not self.exchange_metadata:
            self.exchange_metadata = {}
        # Définir la date d'expiration par défaut (7 jours)
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(days=7)
    
    @property
    def is_active(self):
        """Vérifier si l'échange est actif"""
        return self.status in [
            ExchangeStatus.PENDING.value,
            ExchangeStatus.ACCEPTED.value,
            ExchangeStatus.IN_PROGRESS.value,
            ExchangeStatus.MEETING_SCHEDULED.value
        ]
    
    @property
    def is_completed(self):
        """Vérifier si l'échange est terminé"""
        return self.status == ExchangeStatus.COMPLETED.value
    
    @property
    def is_expired(self):
        """Vérifier si l'échange est expiré"""
        return self.expires_at and self.expires_at <= datetime.utcnow()
    
    @property
    def days_until_expiry(self):
        """Nombre de jours jusqu'à l'expiration"""
        if not self.expires_at:
            return None
        delta = self.expires_at - datetime.utcnow()
        return delta.days if delta.days > 0 else 0
    
    @property
    def initiator(self):
        """Obtenir l'initiateur de l'échange"""
        initiator_participant = next(
            (p for p in self.participants if p.role == ExchangeParticipantRole.INITIATOR.value),
            None
        )
        return initiator_participant.user if initiator_participant else None
    
    @property
    def all_participants(self):
        """Obtenir tous les participants"""
        return [p.user for p in self.participants]
    
    def add_participant(self, user_id, role, proposed_items=None):
        """Ajouter un participant à l'échange"""
        participant = ExchangeParticipant(
            exchange_id=self.id,
            user_id=user_id,
            role=role,
            proposed_items=proposed_items
        )
        db.session.add(participant)
        db.session.commit()
        return participant
    
    def accept(self):
        """Accepter l'échange"""
        if self.status == ExchangeStatus.PENDING.value:
            self.status = ExchangeStatus.ACCEPTED.value
            db.session.commit()
    
    def start(self):
        """Démarrer l'échange"""
        if self.status == ExchangeStatus.ACCEPTED.value:
            self.status = ExchangeStatus.IN_PROGRESS.value
            db.session.commit()
    
    def schedule_meeting(self, meeting_date, location=None, address=None, instructions=None):
        """Planifier un rendez-vous"""
        if self.status in [ExchangeStatus.ACCEPTED.value, ExchangeStatus.IN_PROGRESS.value]:
            self.status = ExchangeStatus.MEETING_SCHEDULED.value
            self.confirmed_meeting_date = meeting_date
            if location:
                self.meeting_location = location
            if address:
                self.meeting_address = address
            if instructions:
                self.meeting_instructions = instructions
            db.session.commit()
    
    def complete(self):
        """Marquer l'échange comme terminé"""
        if self.status in [ExchangeStatus.IN_PROGRESS.value, ExchangeStatus.MEETING_SCHEDULED.value]:
            self.status = ExchangeStatus.COMPLETED.value
            self.completed_at = datetime.utcnow()
            db.session.commit()
    
    def cancel(self, reason=None):
        """Annuler l'échange"""
        if self.status != ExchangeStatus.COMPLETED.value:
            self.status = ExchangeStatus.CANCELLED.value
            if reason:
                self.exchange_metadata['cancellation_reason'] = reason
            db.session.commit()
    
    def dispute(self, reason):
        """Ouvrir un litige"""
        if self.status in [ExchangeStatus.IN_PROGRESS.value, ExchangeStatus.MEETING_SCHEDULED.value]:
            self.status = ExchangeStatus.DISPUTED.value
            self.dispute_reason = reason
            db.session.commit()
    
    def resolve_dispute(self, resolution):
        """Résoudre un litige"""
        if self.status == ExchangeStatus.DISPUTED.value:
            self.dispute_resolution = resolution
            # Décider du statut final
            if 'favor_owner' in resolution.lower():
                self.status = ExchangeStatus.COMPLETED.value
                self.completed_at = datetime.utcnow()
            else:
                self.status = ExchangeStatus.CANCELLED.value
            db.session.commit()
    
    def extend_expiry(self, days=7):
        """Prolonger l'expiration"""
        if self.expires_at:
            self.expires_at += timedelta(days=days)
        else:
            self.expires_at = datetime.utcnow() + timedelta(days=days)
        db.session.commit()
    
    def add_message(self, user_id, message, message_type='text'):
        """Ajouter un message à l'échange"""
        exchange_message = ExchangeMessage(
            exchange_id=self.id,
            user_id=user_id,
            message=message,
            message_type=message_type
        )
        db.session.add(exchange_message)
        db.session.commit()
        return exchange_message
    
    def rate_participant(self, rating, review=None):
        """Noter le participant"""
        if 1 <= rating <= 5:
            self.participant_rating = rating
            if review:
                self.participant_review = review
            db.session.commit()
    
    def rate_owner(self, rating, review=None):
        """Noter le propriétaire"""
        if 1 <= rating <= 5:
            self.owner_rating = rating
            if review:
                self.owner_review = review
            db.session.commit()
    
    def to_dict(self, include_private=False):
        """Convertir l'échange en dictionnaire"""
        data = {
            'id': str(self.id),
            'exchange_type': self.exchange_type,
            'status': self.status,
            'title': self.title,
            'description': self.description,
            'proposed_items': self.proposed_items,
            'proposed_value': self.proposed_value,
            'currency': self.currency,
            'meeting_location': self.meeting_location,
            'meeting_address': self.meeting_address,
            'meeting_instructions': self.meeting_instructions,
            'proposed_meeting_date': self.proposed_meeting_date.isoformat() if self.proposed_meeting_date else None,
            'confirmed_meeting_date': self.confirmed_meeting_date.isoformat() if self.confirmed_meeting_date else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'days_until_expiry': self.days_until_expiry,
            'created_at': self.created_at.isoformat(),
            'listing': {
                'id': str(self.listing.id),
                'title': self.listing.title,
                'images': [img.to_dict() for img in self.listing.images[:3]]  # Limiter à 3 images
            },
            'owner': {
                'id': str(self.owner.id),
                'username': self.owner.username,
                'display_name': self.owner.display_name,
                'trust_score': self.owner.trust_score,
                'profile_picture': self.owner.profile_picture
            },
            'participants': [
                {
                    'id': str(p.user.id),
                    'username': p.user.username,
                    'display_name': p.user.display_name,
                    'role': p.role,
                    'proposed_items': p.proposed_items
                }
                for p in self.participants
            ]
        }
        
        if include_private:
            data.update({
                'metadata': self.exchange_metadata,
                'dispute_reason': self.dispute_reason,
                'dispute_resolution': self.dispute_resolution,
                'owner_rating': self.owner_rating,
                'owner_review': self.owner_review,
                'participant_rating': self.participant_rating,
                'participant_review': self.participant_review,
                'completed_at': self.completed_at.isoformat() if self.completed_at else None,
                'updated_at': self.updated_at.isoformat()
            })
        
        return data
    
    @validates('owner_rating', 'participant_rating')
    def validate_rating(self, key, rating):
        """Valider les notes"""
        if rating is not None and not (1 <= rating <= 5):
            raise ValueError('Rating must be between 1 and 5')
        return rating
    
    @validates('proposed_value')
    def validate_proposed_value(self, key, value):
        """Valider la valeur proposée"""
        if value is not None and value < 0:
            raise ValueError('Proposed value must be positive')
        return value
    
    def __repr__(self):
        return f'<Exchange {self.title}>'


class ExchangeParticipant(db.Model):
    """Participants aux échanges"""
    __tablename__ = 'exchange_participants'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    exchange_id = Column(String(36), ForeignKey('exchanges.id'), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    
    # Rôle et informations
    role = Column(String(20), nullable=False, index=True)
    proposed_items = Column(Text, nullable=True)
    proposed_value = Column(Float, nullable=True)
    currency = Column(String(3), default='CHF', nullable=False)
    
    # Statut du participant
    is_active = Column(Boolean, default=True, nullable=False)
    joined_at = Column(DateTime, default=func.now(), nullable=False)
    left_at = Column(DateTime, nullable=True)
    
    # Relations
    exchange = relationship("Exchange", back_populates="participants")
    user = relationship("User", back_populates="exchanges_as_participant")
    
    # Indexes
    __table_args__ = (
        Index('idx_exchange_participant_exchange', 'exchange_id'),
        Index('idx_exchange_participant_user', 'user_id'),
        Index('idx_exchange_participant_role', 'role'),
        CheckConstraint('proposed_value >= 0', name='check_participant_proposed_value_positive'),
    )
    
    def to_dict(self):
        """Convertir le participant en dictionnaire"""
        return {
            'id': str(self.id),
            'role': self.role,
            'proposed_items': self.proposed_items,
            'proposed_value': self.proposed_value,
            'currency': self.currency,
            'is_active': self.is_active,
            'joined_at': self.joined_at.isoformat(),
            'left_at': self.left_at.isoformat() if self.left_at else None,
            'user': {
                'id': str(self.user.id),
                'username': self.user.username,
                'display_name': self.user.display_name,
                'trust_score': self.user.trust_score,
                'profile_picture': self.user.profile_picture
            }
        }
    
    def __repr__(self):
        return f'<ExchangeParticipant {self.user.username} in {self.exchange.title}>'


class ExchangeMessage(db.Model):
    """Messages dans les échanges"""
    __tablename__ = 'exchange_messages'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    exchange_id = Column(String(36), ForeignKey('exchanges.id'), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    
    # Contenu du message
    message = Column(Text, nullable=False)
    message_type = Column(String(20), default='text', nullable=False)  # text, image, file, system
    attachment_url = Column(String(500), nullable=True)
    attachment_filename = Column(String(255), nullable=True)
    
    # Statut
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Relations
    exchange = relationship("Exchange", back_populates="messages")
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_exchange_message_exchange', 'exchange_id'),
        Index('idx_exchange_message_user', 'user_id'),
        Index('idx_exchange_message_created', 'created_at'),
    )
    
    def mark_as_read(self):
        """Marquer le message comme lu"""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
            db.session.commit()
    
    def to_dict(self):
        """Convertir le message en dictionnaire"""
        return {
            'id': str(self.id),
            'message': self.message,
            'message_type': self.message_type,
            'attachment_url': self.attachment_url,
            'attachment_filename': self.attachment_filename,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat(),
            'user': {
                'id': str(self.user.id),
                'username': self.user.username,
                'display_name': self.user.display_name,
                'profile_picture': self.user.profile_picture
            }
        }
    
    def __repr__(self):
        return f'<ExchangeMessage from {self.user.username}>'
