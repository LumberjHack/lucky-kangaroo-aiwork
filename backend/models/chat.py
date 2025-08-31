"""
Lucky Kangaroo - Modèles Chat Complets
Modèles pour la messagerie et chat en temps réel
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum
import uuid

db = SQLAlchemy()

class MessageType(Enum):
    """Types de messages"""
    TEXT = "text"
    IMAGE = "image"
    SYSTEM = "system"
    EXCHANGE_REQUEST = "exchange_request"
    EXCHANGE_UPDATE = "exchange_update"
    LOCATION = "location"

class MessageStatus(Enum):
    """Statuts des messages"""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    DELETED = "deleted"

class ChatRoom(db.Model):
    """Modèle pour les salles de chat"""
    
    __tablename__ = 'chat_rooms'
    
    # Identifiants
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Participants
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Échange associé (optionnel)
    exchange_id = db.Column(db.Integer, db.ForeignKey('exchanges.id'), nullable=True, index=True)
    
    # Métadonnées
    title = db.Column(db.String(200), nullable=True)  # Titre personnalisé du chat
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_archived = db.Column(db.Boolean, nullable=False, default=False)
    
    # Dernière activité
    last_message_id = db.Column(db.Integer, nullable=True)
    last_message_at = db.Column(db.DateTime, nullable=True, index=True)
    last_activity_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Compteurs
    total_messages = db.Column(db.Integer, nullable=False, default=0)
    unread_count_user1 = db.Column(db.Integer, nullable=False, default=0)
    unread_count_user2 = db.Column(db.Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    messages = db.relationship('ChatMessage', backref='chat_room', lazy='dynamic', 
                              cascade='all, delete-orphan', order_by='ChatMessage.created_at.desc()')
    
    def __init__(self, user1_id, user2_id, exchange_id=None, **kwargs):
        # S'assurer que user1_id < user2_id pour éviter les doublons
        if user1_id > user2_id:
            user1_id, user2_id = user2_id, user1_id
            
        self.user1_id = user1_id
        self.user2_id = user2_id
        self.exchange_id = exchange_id
        
        # Définir les autres attributs depuis kwargs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get_other_participant(self, user_id):
        """Retourne l'autre participant du chat"""
        if user_id == self.user1_id:
            return self.user2_id
        elif user_id == self.user2_id:
            return self.user1_id
        return None
    
    def get_unread_count(self, user_id):
        """Retourne le nombre de messages non lus pour un utilisateur"""
        if user_id == self.user1_id:
            return self.unread_count_user1
        elif user_id == self.user2_id:
            return self.unread_count_user2
        return 0
    
    def increment_unread_count(self, for_user_id):
        """Incrémente le compteur de messages non lus"""
        if for_user_id == self.user1_id:
            self.unread_count_user1 += 1
        elif for_user_id == self.user2_id:
            self.unread_count_user2 += 1
    
    def reset_unread_count(self, user_id):
        """Remet à zéro le compteur de messages non lus"""
        if user_id == self.user1_id:
            self.unread_count_user1 = 0
        elif user_id == self.user2_id:
            self.unread_count_user2 = 0
    
    def update_last_message(self, message):
        """Met à jour les informations du dernier message"""
        self.last_message_id = message.id
        self.last_message_at = message.created_at
        self.last_activity_at = datetime.utcnow()
        self.total_messages += 1
        
        # Incrémenter le compteur de non-lus pour l'autre participant
        other_user_id = self.get_other_participant(message.sender_id)
        if other_user_id:
            self.increment_unread_count(other_user_id)
    
    def archive(self):
        """Archive le chat"""
        self.is_archived = True
        self.is_active = False
    
    def unarchive(self):
        """Désarchive le chat"""
        self.is_archived = False
        self.is_active = True
    
    def get_title(self):
        """Retourne le titre du chat ou un titre par défaut"""
        if self.title:
            return self.title
        
        # Titre basé sur les participants (nécessite de charger les utilisateurs)
        if hasattr(self, 'user1') and hasattr(self, 'user2'):
            return f"Chat avec {self.user1.get_full_name()} et {self.user2.get_full_name()}"
        
        return f"Chat {self.id}"
    
    def to_dict(self, include_participants=False, include_last_message=False, user_perspective=None):
        """Convertit le chat en dictionnaire"""
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'title': self.get_title(),
            'is_active': self.is_active,
            'is_archived': self.is_archived,
            'exchange_id': self.exchange_id,
            'total_messages': self.total_messages,
            'last_message_at': self.last_message_at.isoformat() if self.last_message_at else None,
            'last_activity_at': self.last_activity_at.isoformat() if self.last_activity_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if user_perspective:
            data['unread_count'] = self.get_unread_count(user_perspective)
            data['other_participant_id'] = self.get_other_participant(user_perspective)
        
        if include_participants:
            data['participants'] = {
                'user1_id': self.user1_id,
                'user2_id': self.user2_id
            }
            
            if hasattr(self, 'user1'):
                data['participants']['user1'] = self.user1.to_public_dict()
            if hasattr(self, 'user2'):
                data['participants']['user2'] = self.user2.to_public_dict()
        
        if include_last_message and self.last_message_id:
            last_message = self.messages.filter_by(id=self.last_message_id).first()
            if last_message:
                data['last_message'] = last_message.to_dict()
        
        return data
    
    def __repr__(self):
        return f'<ChatRoom {self.id} (Users {self.user1_id}, {self.user2_id})>'

    @staticmethod
    def get_or_create_room(user1_id, user2_id, exchange_id=None):
        """Récupère ou crée une salle de chat entre deux utilisateurs"""
        # S'assurer que user1_id < user2_id
        if user1_id > user2_id:
            user1_id, user2_id = user2_id, user1_id
        
        # Chercher une salle existante
        room = ChatRoom.query.filter_by(
            user1_id=user1_id,
            user2_id=user2_id
        ).first()
        
        if not room:
            room = ChatRoom(user1_id=user1_id, user2_id=user2_id, exchange_id=exchange_id)
            db.session.add(room)
            db.session.flush()  # Pour obtenir l'ID
        
        return room
    
    @staticmethod
    def get_user_chats(user_id, include_archived=False, limit=50):
        """Récupère les chats d'un utilisateur"""
        query = ChatRoom.query.filter(
            db.or_(
                ChatRoom.user1_id == user_id,
                ChatRoom.user2_id == user_id
            )
        )
        
        if not include_archived:
            query = query.filter(ChatRoom.is_archived == False)
        
        return query.order_by(ChatRoom.last_activity_at.desc()).limit(limit).all()

class ChatMessage(db.Model):
    """Modèle pour les messages de chat"""
    
    __tablename__ = 'chat_messages'
    
    # Identifiants
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Relations
    chat_room_id = db.Column(db.Integer, db.ForeignKey('chat_rooms.id'), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    exchange_id = db.Column(db.Integer, db.ForeignKey('exchanges.id'), nullable=True, index=True)
    
    # Contenu du message
    message_type = db.Column(db.Enum(MessageType), nullable=False, default=MessageType.TEXT)
    content = db.Column(db.Text, nullable=False)
    
    # Métadonnées
    status = db.Column(db.Enum(MessageStatus), nullable=False, default=MessageStatus.SENT, index=True)
    is_edited = db.Column(db.Boolean, nullable=False, default=False)
    edited_at = db.Column(db.DateTime, nullable=True)
    
    # Pièces jointes
    image_id = db.Column(db.Integer, db.ForeignKey('images.id'), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    
    # Localisation (pour les messages de type LOCATION)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    location_name = db.Column(db.String(200), nullable=True)
    
    # Données système (pour les messages système)
    system_data = db.Column(db.Text, nullable=True)  # JSON pour données additionnelles
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    delivered_at = db.Column(db.DateTime, nullable=True)
    read_at = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, chat_room_id, sender_id, content, message_type=MessageType.TEXT, **kwargs):
        self.chat_room_id = chat_room_id
        self.sender_id = sender_id
        self.content = content
        self.message_type = message_type
        
        # Définir les autres attributs depuis kwargs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def mark_as_delivered(self):
        """Marque le message comme livré"""
        if self.status == MessageStatus.SENT:
            self.status = MessageStatus.DELIVERED
            self.delivered_at = datetime.utcnow()
    
    def mark_as_read(self):
        """Marque le message comme lu"""
        if self.status in [MessageStatus.SENT, MessageStatus.DELIVERED]:
            self.status = MessageStatus.READ
            self.read_at = datetime.utcnow()
    
    def edit(self, new_content):
        """Modifie le contenu du message"""
        if self.message_type == MessageType.TEXT:
            self.content = new_content
            self.is_edited = True
            self.edited_at = datetime.utcnow()
    
    def soft_delete(self):
        """Suppression logique du message"""
        self.status = MessageStatus.DELETED
        self.content = "[Message supprimé]"
    
    def get_system_data_dict(self):
        """Retourne les données système sous forme de dictionnaire"""
        if self.system_data:
            import json
            try:
                return json.loads(self.system_data)
            except:
                return {}
        return {}
    
    def set_system_data(self, data_dict):
        """Définit les données système depuis un dictionnaire"""
        import json
        self.system_data = json.dumps(data_dict) if data_dict else None
    
    def get_location_string(self):
        """Retourne la localisation sous forme de chaîne"""
        if self.location_name:
            return self.location_name
        elif self.latitude and self.longitude:
            return f"Lat: {self.latitude}, Lng: {self.longitude}"
        return "Localisation inconnue"
    
    def to_dict(self, include_sender=False, include_chat_room=False):
        """Convertit le message en dictionnaire"""
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'chat_room_id': self.chat_room_id,
            'sender_id': self.sender_id,
            'exchange_id': self.exchange_id,
            'message_type': self.message_type.value if self.message_type else None,
            'content': self.content,
            'status': self.status.value if self.status else None,
            'is_edited': self.is_edited,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'image_url': self.image_url,
            'location': {
                'latitude': self.latitude,
                'longitude': self.longitude,
                'name': self.location_name,
                'location_string': self.get_location_string()
            } if self.latitude and self.longitude else None,
            'system_data': self.get_system_data_dict() if self.system_data else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }
        
        if include_sender and hasattr(self, 'sender'):
            data['sender'] = self.sender.to_public_dict()
        
        if include_chat_room and hasattr(self, 'chat_room'):
            data['chat_room'] = self.chat_room.to_dict()
        
        return data
    
    def __repr__(self):
        return f'<ChatMessage {self.id} from User {self.sender_id}>'

    @staticmethod
    def get_chat_messages(chat_room_id, limit=50, offset=0, include_deleted=False):
        """Récupère les messages d'un chat"""
        query = ChatMessage.query.filter(ChatMessage.chat_room_id == chat_room_id)
        
        if not include_deleted:
            query = query.filter(ChatMessage.status != MessageStatus.DELETED)
        
        return query.order_by(ChatMessage.created_at.desc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def mark_messages_as_read(chat_room_id, user_id):
        """Marque tous les messages non lus d'un chat comme lus"""
        messages = ChatMessage.query.filter(
            ChatMessage.chat_room_id == chat_room_id,
            ChatMessage.sender_id != user_id,  # Messages des autres
            ChatMessage.status.in_([MessageStatus.SENT, MessageStatus.DELIVERED])
        ).all()
        
        for message in messages:
            message.mark_as_read()
        
        # Réinitialiser le compteur de non-lus dans la salle de chat
        chat_room = ChatRoom.query.get(chat_room_id)
        if chat_room:
            chat_room.reset_unread_count(user_id)
        
        return len(messages)
    
    @staticmethod
    def create_system_message(chat_room_id, content, system_data=None, exchange_id=None):
        """Crée un message système"""
        message = ChatMessage(
            chat_room_id=chat_room_id,
            sender_id=None,  # Messages système n'ont pas d'expéditeur
            content=content,
            message_type=MessageType.SYSTEM,
            exchange_id=exchange_id
        )
        
        if system_data:
            message.set_system_data(system_data)
        
        return message
    
    @staticmethod
    def create_exchange_request_message(chat_room_id, sender_id, exchange_id, offered_item, requested_item):
        """Crée un message de demande d'échange"""
        content = f"Demande d'échange : {offered_item} contre {requested_item}"
        
        system_data = {
            'type': 'exchange_request',
            'exchange_id': exchange_id,
            'offered_item': offered_item,
            'requested_item': requested_item
        }
        
        message = ChatMessage(
            chat_room_id=chat_room_id,
            sender_id=sender_id,
            content=content,
            message_type=MessageType.EXCHANGE_REQUEST,
            exchange_id=exchange_id
        )
        
        message.set_system_data(system_data)
        return message
    
    @staticmethod
    def create_exchange_update_message(chat_room_id, exchange_id, status_change, additional_info=None):
        """Crée un message de mise à jour d'échange"""
        status_messages = {
            'accepted': "Échange accepté ! 🎉",
            'confirmed': "Rendez-vous confirmé ! 📅",
            'completed': "Échange terminé avec succès ! ✅",
            'cancelled': "Échange annulé 😞"
        }
        
        content = status_messages.get(status_change, f"Statut de l'échange mis à jour : {status_change}")
        
        if additional_info:
            content += f" - {additional_info}"
        
        system_data = {
            'type': 'exchange_update',
            'exchange_id': exchange_id,
            'status_change': status_change,
            'additional_info': additional_info
        }
        
        message = ChatMessage(
            chat_room_id=chat_room_id,
            sender_id=None,  # Message système
            content=content,
            message_type=MessageType.EXCHANGE_UPDATE,
            exchange_id=exchange_id
        )
        
        message.set_system_data(system_data)
        return message

