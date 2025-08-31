"""
Lucky Kangaroo - Modèle Notification Complet
Modèle pour la gestion des notifications multi-canal
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum
import uuid

db = SQLAlchemy()

class NotificationType(Enum):
    """Types de notifications"""
    # Échanges
    EXCHANGE_REQUEST = "exchange_request"
    EXCHANGE_ACCEPTED = "exchange_accepted"
    EXCHANGE_CONFIRMED = "exchange_confirmed"
    EXCHANGE_COMPLETED = "exchange_completed"
    EXCHANGE_CANCELLED = "exchange_cancelled"
    EXCHANGE_REMINDER = "exchange_reminder"
    
    # Messages
    NEW_MESSAGE = "new_message"
    MESSAGE_READ = "message_read"
    
    # Annonces
    LISTING_LIKED = "listing_liked"
    LISTING_VIEWED = "listing_viewed"
    LISTING_EXPIRED = "listing_expired"
    LISTING_FEATURED = "listing_featured"
    
    # Système
    WELCOME = "welcome"
    ACCOUNT_VERIFIED = "account_verified"
    TRUST_SCORE_UPDATED = "trust_score_updated"
    PREMIUM_ACTIVATED = "premium_activated"
    PREMIUM_EXPIRED = "premium_expired"
    
    # Sécurité
    LOGIN_ALERT = "login_alert"
    PASSWORD_CHANGED = "password_changed"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    
    # Marketing
    PROMOTION = "promotion"
    NEWSLETTER = "newsletter"
    FEATURE_ANNOUNCEMENT = "feature_announcement"

class NotificationChannel(Enum):
    """Canaux de notification"""
    IN_APP = "in_app"
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    WHATSAPP = "whatsapp"

class NotificationPriority(Enum):
    """Priorités de notification"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class NotificationStatus(Enum):
    """Statuts de notification"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Notification(db.Model):
    """Modèle pour les notifications"""
    
    __tablename__ = 'notifications'
    
    # Identifiants
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Type et contenu
    notification_type = db.Column(db.Enum(NotificationType), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Canaux et priorité
    channels = db.Column(db.Text, nullable=False)  # JSON array des canaux
    priority = db.Column(db.Enum(NotificationPriority), nullable=False, default=NotificationPriority.NORMAL)
    
    # Statut et suivi
    status = db.Column(db.Enum(NotificationStatus), nullable=False, default=NotificationStatus.PENDING, index=True)
    is_read = db.Column(db.Boolean, nullable=False, default=False, index=True)
    
    # Données contextuelles
    related_object_type = db.Column(db.String(50), nullable=True)  # 'exchange', 'listing', 'user', etc.
    related_object_id = db.Column(db.Integer, nullable=True, index=True)
    action_url = db.Column(db.String(500), nullable=True)  # URL pour action directe
    
    # Métadonnées
    metadata = db.Column(db.Text, nullable=True)  # JSON pour données additionnelles
    
    # Planification
    scheduled_for = db.Column(db.DateTime, nullable=True, index=True)  # Envoi programmé
    expires_at = db.Column(db.DateTime, nullable=True, index=True)  # Expiration
    
    # Suivi des canaux
    sent_via_email = db.Column(db.Boolean, nullable=False, default=False)
    sent_via_push = db.Column(db.Boolean, nullable=False, default=False)
    sent_via_sms = db.Column(db.Boolean, nullable=False, default=False)
    sent_via_whatsapp = db.Column(db.Boolean, nullable=False, default=False)
    
    # Timestamps des envois
    email_sent_at = db.Column(db.DateTime, nullable=True)
    push_sent_at = db.Column(db.DateTime, nullable=True)
    sms_sent_at = db.Column(db.DateTime, nullable=True)
    whatsapp_sent_at = db.Column(db.DateTime, nullable=True)
    
    # Erreurs d'envoi
    email_error = db.Column(db.Text, nullable=True)
    push_error = db.Column(db.Text, nullable=True)
    sms_error = db.Column(db.Text, nullable=True)
    whatsapp_error = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    sent_at = db.Column(db.DateTime, nullable=True)
    delivered_at = db.Column(db.DateTime, nullable=True)
    read_at = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, user_id, notification_type, title, message, channels=None, **kwargs):
        self.user_id = user_id
        self.notification_type = notification_type
        self.title = title
        self.message = message
        
        # Définir les canaux par défaut si non spécifiés
        if channels is None:
            channels = [NotificationChannel.IN_APP]
        self.set_channels(channels)
        
        # Définir les autres attributs depuis kwargs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get_channels_list(self):
        """Retourne la liste des canaux"""
        if self.channels:
            import json
            try:
                return [NotificationChannel(ch) for ch in json.loads(self.channels)]
            except:
                return [NotificationChannel.IN_APP]
        return [NotificationChannel.IN_APP]
    
    def set_channels(self, channels_list):
        """Définit les canaux depuis une liste"""
        import json
        if isinstance(channels_list[0], NotificationChannel):
            channels_values = [ch.value for ch in channels_list]
        else:
            channels_values = channels_list
        self.channels = json.dumps(channels_values)
    
    def get_metadata_dict(self):
        """Retourne les métadonnées sous forme de dictionnaire"""
        if self.metadata:
            import json
            try:
                return json.loads(self.metadata)
            except:
                return {}
        return {}
    
    def set_metadata(self, metadata_dict):
        """Définit les métadonnées depuis un dictionnaire"""
        import json
        self.metadata = json.dumps(metadata_dict) if metadata_dict else None
    
    def mark_as_sent(self, channel=None):
        """Marque la notification comme envoyée"""
        self.status = NotificationStatus.SENT
        self.sent_at = datetime.utcnow()
        
        if channel:
            if channel == NotificationChannel.EMAIL:
                self.sent_via_email = True
                self.email_sent_at = datetime.utcnow()
            elif channel == NotificationChannel.PUSH:
                self.sent_via_push = True
                self.push_sent_at = datetime.utcnow()
            elif channel == NotificationChannel.SMS:
                self.sent_via_sms = True
                self.sms_sent_at = datetime.utcnow()
            elif channel == NotificationChannel.WHATSAPP:
                self.sent_via_whatsapp = True
                self.whatsapp_sent_at = datetime.utcnow()
    
    def mark_as_delivered(self):
        """Marque la notification comme livrée"""
        if self.status == NotificationStatus.SENT:
            self.status = NotificationStatus.DELIVERED
            self.delivered_at = datetime.utcnow()
    
    def mark_as_read(self):
        """Marque la notification comme lue"""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
            if self.status in [NotificationStatus.SENT, NotificationStatus.DELIVERED]:
                self.status = NotificationStatus.READ
    
    def mark_as_failed(self, channel=None, error_message=None):
        """Marque la notification comme échouée"""
        self.status = NotificationStatus.FAILED
        
        if channel and error_message:
            if channel == NotificationChannel.EMAIL:
                self.email_error = error_message
            elif channel == NotificationChannel.PUSH:
                self.push_error = error_message
            elif channel == NotificationChannel.SMS:
                self.sms_error = error_message
            elif channel == NotificationChannel.WHATSAPP:
                self.whatsapp_error = error_message
    
    def cancel(self):
        """Annule la notification"""
        if self.status == NotificationStatus.PENDING:
            self.status = NotificationStatus.CANCELLED
    
    def is_expired(self):
        """Vérifie si la notification a expiré"""
        return self.expires_at and self.expires_at <= datetime.utcnow()
    
    def should_be_sent_now(self):
        """Vérifie si la notification doit être envoyée maintenant"""
        if self.status != NotificationStatus.PENDING:
            return False
        
        if self.is_expired():
            return False
        
        if self.scheduled_for and self.scheduled_for > datetime.utcnow():
            return False
        
        return True
    
    def get_channel_status(self):
        """Retourne le statut d'envoi par canal"""
        return {
            'email': {
                'sent': self.sent_via_email,
                'sent_at': self.email_sent_at.isoformat() if self.email_sent_at else None,
                'error': self.email_error
            },
            'push': {
                'sent': self.sent_via_push,
                'sent_at': self.push_sent_at.isoformat() if self.push_sent_at else None,
                'error': self.push_error
            },
            'sms': {
                'sent': self.sent_via_sms,
                'sent_at': self.sms_sent_at.isoformat() if self.sms_sent_at else None,
                'error': self.sms_error
            },
            'whatsapp': {
                'sent': self.sent_via_whatsapp,
                'sent_at': self.whatsapp_sent_at.isoformat() if self.whatsapp_sent_at else None,
                'error': self.whatsapp_error
            }
        }
    
    def to_dict(self, include_user=False, include_errors=False):
        """Convertit la notification en dictionnaire"""
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'user_id': self.user_id,
            'notification_type': self.notification_type.value if self.notification_type else None,
            'title': self.title,
            'message': self.message,
            'channels': [ch.value for ch in self.get_channels_list()],
            'priority': self.priority.value if self.priority else None,
            'status': self.status.value if self.status else None,
            'is_read': self.is_read,
            'related_object': {
                'type': self.related_object_type,
                'id': self.related_object_id
            } if self.related_object_type else None,
            'action_url': self.action_url,
            'metadata': self.get_metadata_dict(),
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'is_expired': self.is_expired()
        }
        
        if include_user and hasattr(self, 'user'):
            data['user'] = self.user.to_public_dict()
        
        if include_errors:
            data['channel_status'] = self.get_channel_status()
        
        return data
    
    def __repr__(self):
        return f'<Notification {self.id} ({self.notification_type.value if self.notification_type else "unknown"}) for User {self.user_id}>'

    @staticmethod
    def create_exchange_notification(user_id, exchange, notification_type, additional_data=None):
        """Crée une notification liée à un échange"""
        titles = {
            NotificationType.EXCHANGE_REQUEST: "Nouvelle demande d'échange",
            NotificationType.EXCHANGE_ACCEPTED: "Échange accepté !",
            NotificationType.EXCHANGE_CONFIRMED: "Rendez-vous confirmé",
            NotificationType.EXCHANGE_COMPLETED: "Échange terminé",
            NotificationType.EXCHANGE_CANCELLED: "Échange annulé",
            NotificationType.EXCHANGE_REMINDER: "Rappel d'échange"
        }
        
        messages = {
            NotificationType.EXCHANGE_REQUEST: "Quelqu'un souhaite échanger avec vous",
            NotificationType.EXCHANGE_ACCEPTED: "Votre demande d'échange a été acceptée",
            NotificationType.EXCHANGE_CONFIRMED: "Le rendez-vous pour votre échange est confirmé",
            NotificationType.EXCHANGE_COMPLETED: "Votre échange s'est bien déroulé",
            NotificationType.EXCHANGE_CANCELLED: "L'échange a été annulé",
            NotificationType.EXCHANGE_REMINDER: "N'oubliez pas votre rendez-vous d'échange"
        }
        
        # Déterminer les canaux selon le type
        channels = [NotificationChannel.IN_APP, NotificationChannel.PUSH]
        if notification_type in [NotificationType.EXCHANGE_CONFIRMED, NotificationType.EXCHANGE_REMINDER]:
            channels.append(NotificationChannel.EMAIL)
        
        # Déterminer la priorité
        priority = NotificationPriority.NORMAL
        if notification_type == NotificationType.EXCHANGE_REMINDER:
            priority = NotificationPriority.HIGH
        elif notification_type == NotificationType.EXCHANGE_REQUEST:
            priority = NotificationPriority.HIGH
        
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=titles.get(notification_type, "Notification d'échange"),
            message=messages.get(notification_type, "Mise à jour de votre échange"),
            channels=channels,
            priority=priority,
            related_object_type='exchange',
            related_object_id=exchange.id,
            action_url=f"/exchanges/{exchange.uuid}"
        )
        
        # Ajouter des métadonnées
        metadata = {
            'exchange_uuid': exchange.uuid,
            'exchange_status': exchange.status.value if exchange.status else None
        }
        
        if additional_data:
            metadata.update(additional_data)
        
        notification.set_metadata(metadata)
        
        return notification
    
    @staticmethod
    def create_message_notification(user_id, chat_room, sender, message_preview):
        """Crée une notification pour un nouveau message"""
        notification = Notification(
            user_id=user_id,
            notification_type=NotificationType.NEW_MESSAGE,
            title=f"Nouveau message de {sender.get_full_name()}",
            message=message_preview[:100] + "..." if len(message_preview) > 100 else message_preview,
            channels=[NotificationChannel.IN_APP, NotificationChannel.PUSH],
            priority=NotificationPriority.NORMAL,
            related_object_type='chat_room',
            related_object_id=chat_room.id,
            action_url=f"/chat/{chat_room.uuid}"
        )
        
        metadata = {
            'chat_room_uuid': chat_room.uuid,
            'sender_id': sender.id,
            'sender_name': sender.get_full_name()
        }
        
        notification.set_metadata(metadata)
        
        return notification
    
    @staticmethod
    def create_listing_notification(user_id, listing, notification_type, actor_user=None):
        """Crée une notification liée à une annonce"""
        titles = {
            NotificationType.LISTING_LIKED: "Votre annonce a été likée",
            NotificationType.LISTING_VIEWED: "Votre annonce a été consultée",
            NotificationType.LISTING_EXPIRED: "Votre annonce a expiré",
            NotificationType.LISTING_FEATURED: "Votre annonce est mise en avant"
        }
        
        messages = {
            NotificationType.LISTING_LIKED: f"Quelqu'un a liké votre annonce '{listing.title}'",
            NotificationType.LISTING_VIEWED: f"Votre annonce '{listing.title}' a été consultée",
            NotificationType.LISTING_EXPIRED: f"Votre annonce '{listing.title}' a expiré",
            NotificationType.LISTING_FEATURED: f"Votre annonce '{listing.title}' est maintenant mise en avant"
        }
        
        if actor_user:
            if notification_type == NotificationType.LISTING_LIKED:
                messages[notification_type] = f"{actor_user.get_full_name()} a liké votre annonce '{listing.title}'"
            elif notification_type == NotificationType.LISTING_VIEWED:
                messages[notification_type] = f"{actor_user.get_full_name()} a consulté votre annonce '{listing.title}'"
        
        # Canaux selon le type
        channels = [NotificationChannel.IN_APP]
        if notification_type in [NotificationType.LISTING_EXPIRED, NotificationType.LISTING_FEATURED]:
            channels.append(NotificationChannel.EMAIL)
        
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=titles.get(notification_type, "Notification d'annonce"),
            message=messages.get(notification_type, "Mise à jour de votre annonce"),
            channels=channels,
            priority=NotificationPriority.LOW,
            related_object_type='listing',
            related_object_id=listing.id,
            action_url=f"/listings/{listing.uuid}"
        )
        
        metadata = {
            'listing_uuid': listing.uuid,
            'listing_title': listing.title
        }
        
        if actor_user:
            metadata.update({
                'actor_user_id': actor_user.id,
                'actor_user_name': actor_user.get_full_name()
            })
        
        notification.set_metadata(metadata)
        
        return notification
    
    @staticmethod
    def get_user_notifications(user_id, unread_only=False, notification_type=None, limit=50, offset=0):
        """Récupère les notifications d'un utilisateur"""
        query = Notification.query.filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        if notification_type:
            query = query.filter(Notification.notification_type == notification_type)
        
        return query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def get_unread_count(user_id):
        """Retourne le nombre de notifications non lues"""
        return Notification.query.filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
            Notification.status != NotificationStatus.CANCELLED
        ).count()
    
    @staticmethod
    def mark_all_as_read(user_id):
        """Marque toutes les notifications comme lues"""
        notifications = Notification.query.filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).all()
        
        for notification in notifications:
            notification.mark_as_read()
        
        return len(notifications)
    
    @staticmethod
    def get_pending_notifications():
        """Récupère les notifications en attente d'envoi"""
        return Notification.query.filter(
            Notification.status == NotificationStatus.PENDING,
            db.or_(
                Notification.scheduled_for.is_(None),
                Notification.scheduled_for <= datetime.utcnow()
            ),
            db.or_(
                Notification.expires_at.is_(None),
                Notification.expires_at > datetime.utcnow()
            )
        ).order_by(Notification.priority.desc(), Notification.created_at.asc()).all()
    
    @staticmethod
    def cleanup_old_notifications(days=90):
        """Nettoie les anciennes notifications"""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        old_notifications = Notification.query.filter(
            Notification.created_at < cutoff_date,
            Notification.is_read == True
        ).all()
        
        for notification in old_notifications:
            db.session.delete(notification)
        
        return len(old_notifications)

