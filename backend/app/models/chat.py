"""
Modèles pour le système de chat temps réel
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
import uuid

from app import db

class Chat(db.Model):
    """
    Modèle pour les chats
    """
    __tablename__ = 'chats'

    # Identifiants
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Informations de base
    chat_type = Column(String(20), nullable=False)  # 'direct', 'group', 'listing', 'exchange'
    status = Column(String(20), nullable=False, default='active')  # 'active', 'archived', 'deleted'
    name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Métadonnées
    chat_metadata = Column(JSON, nullable=False, default=dict)
    settings = Column(JSON, nullable=False, default=dict)
    
    # Relations
    exchange_id = Column(String(36), ForeignKey('exchanges.id'), nullable=True, index=True)
    listing_id = Column(String(36), ForeignKey('listings.id'), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_message_at = Column(DateTime, nullable=True)
    
    # Relations
    participants = relationship('ChatParticipant', backref='chat', lazy='dynamic', cascade='all, delete-orphan')
    messages = relationship('ChatMessage', backref='chat', lazy='dynamic', cascade='all, delete-orphan')
    exchange = relationship('Exchange', backref='chat')
    listing = relationship('Listing', backref='chat')

    def __repr__(self):
        return f'<Chat {self.id}: {self.name or self.chat_type}>'

    def to_dict(self):
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'chat_type': self.chat_type,
            'status': self.status,
            'name': self.name,
            'description': self.description,
            'avatar_url': self.avatar_url,
            'participants_count': self.participants.filter_by(is_active=True).count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_message_at': self.last_message_at.isoformat() if self.last_message_at else None
        }

class ChatParticipant(db.Model):
    """
    Modèle pour les participants d'un chat
    """
    __tablename__ = 'chat_participants'

    # Identifiants
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_id = Column(String(36), ForeignKey('chats.id'), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    
    # Rôle et permissions
    role = Column(String(20), nullable=False, default='member')  # 'admin', 'moderator', 'member'
    is_admin = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Paramètres personnalisés
    settings = Column(JSON, nullable=False, default=dict)
    
    # Timestamps
    joined_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    left_at = Column(DateTime, nullable=True)
    last_read_at = Column(DateTime, nullable=True)
    last_activity_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relations
    user = relationship('User', back_populates='chat_participations')

    def __repr__(self):
        return f'<ChatParticipant {self.user_id} in {self.chat_id}>'

    def to_dict(self):
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'user_id': self.user_id,
            'role': self.role,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'left_at': self.left_at.isoformat() if self.left_at else None,
            'last_read_at': self.last_read_at.isoformat() if self.last_read_at else None,
            'last_activity_at': self.last_activity_at.isoformat() if self.last_activity_at else None
        }

class ChatMessage(db.Model):
    """
    Modèle pour les messages de chat
    """
    __tablename__ = 'chat_messages'

    # Identifiants
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_id = Column(String(36), ForeignKey('chats.id'), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    
    # Contenu du message
    message = Column(Text, nullable=False)
    message_type = Column(String(20), nullable=False, default='text')  # 'text', 'image', 'file', 'location', 'system'
    
    # Pièces jointes
    attachment_url = Column(String(500), nullable=True)
    attachment_filename = Column(String(255), nullable=True)
    attachment_size = Column(Integer, nullable=True)
    attachment_mime_type = Column(String(100), nullable=True)
    
    # Géolocalisation
    location_latitude = Column(Float, nullable=True)
    location_longitude = Column(Float, nullable=True)
    location_name = Column(String(200), nullable=True)
    
    # Réponse à un message
    reply_to_id = Column(String(36), ForeignKey('chat_messages.id'), nullable=True, index=True)
    
    # État du message
    is_edited = Column(Boolean, nullable=False, default=False)
    edited_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime, nullable=True)
    
    # Métadonnées
    chat_metadata = Column(JSON, nullable=False, default=dict)
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relations
    user = relationship('User', backref='chat_messages')
    reply_to = relationship('ChatMessage', remote_side=[id], backref='replies')

    def __repr__(self):
        return f'<ChatMessage {self.id}: {self.message[:50]}...>'

    def to_dict(self):
        """Convertir en dictionnaire"""
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'user_id': self.user_id,
            'message': self.message,
            'message_type': self.message_type,
            'attachment_url': self.attachment_url,
            'attachment_filename': self.attachment_filename,
            'attachment_size': self.attachment_size,
            'attachment_mime_type': self.attachment_mime_type,
            'location': {
                'latitude': self.location_latitude,
                'longitude': self.location_longitude,
                'name': self.location_name
            } if self.location_latitude else None,
            'reply_to_id': self.reply_to_id,
            'is_edited': self.is_edited,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'is_deleted': self.is_deleted,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def edit_message(self, new_message):
        """Éditer un message"""
        self.message = new_message
        self.is_edited = True
        self.edited_at = datetime.utcnow()
        db.session.commit()

    def delete_message(self):
        """Supprimer un message (soft delete)"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        db.session.commit()