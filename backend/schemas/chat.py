"""
Lucky Kangaroo - Schémas de validation pour le chat
Validation des données d'entrée avec Marshmallow
"""

from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime

class ChatMessageSchema(Schema):
    """Schéma de base pour les messages de chat (lecture seule)"""
    
    id = fields.Int(dump_only=True)
    uuid = fields.Str(dump_only=True)
    chat_room_id = fields.Int(dump_only=True)
    sender_id = fields.Int(dump_only=True)
    
    # Contenu du message
    content = fields.Str(dump_only=True)
    message_type = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    
    # Médias
    media_url = fields.Str(dump_only=True, allow_none=True)
    media_type = fields.Str(dump_only=True, allow_none=True)
    media_size = fields.Int(dump_only=True, allow_none=True)
    
    # Réactions
    reactions = fields.Str(dump_only=True, allow_none=True)  # JSON
    reaction_count = fields.Int(dump_only=True)
    
    # Réponses
    reply_to_message_id = fields.Int(dump_only=True, allow_none=True)
    is_edited = fields.Bool(dump_only=True)
    edited_at = fields.DateTime(dump_only=True, allow_none=True)
    
    # Modération
    is_moderated = fields.Bool(dump_only=True)
    moderation_status = fields.Str(dump_only=True, allow_none=True)
    moderation_reason = fields.Str(dump_only=True, allow_none=True)
    
    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    read_at = fields.DateTime(dump_only=True, allow_none=True)
    delivered_at = fields.DateTime(dump_only=True, allow_none=True)

class CreateChatMessageSchema(Schema):
    """Schéma pour la création de messages de chat"""
    
    content = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=2000),
        error_messages={
            'required': 'Le contenu du message est requis',
            'validator_failed': 'Le contenu du message doit contenir entre 1 et 2000 caractères'
        }
    )
    
    message_type = fields.Str(
        required=False,
        validate=validate.OneOf(['text', 'image', 'system', 'exchange_request', 'exchange_update', 'location']),
        missing='text',
        error_messages={
            'validator_failed': 'Type de message invalide'
        }
    )
    
    media_url = fields.Str(
        required=False,
        validate=validate.URL(),
        error_messages={
            'validator_failed': 'URL de média invalide'
        }
    )
    
    media_type = fields.Str(
        required=False,
        validate=validate.OneOf(['image', 'video', 'audio', 'document']),
        error_messages={
            'validator_failed': 'Type de média invalide'
        }
    )
    
    media_size = fields.Int(
        required=False,
        validate=validate.Range(min=1, max=50*1024*1024),  # 50MB max
        error_messages={
            'validator_failed': 'La taille du média doit être comprise entre 1 et 50 MB'
        }
    )
    
    reply_to_message_id = fields.Int(
        required=False,
        validate=validate.Range(min=1),
        error_messages={
            'validator_failed': 'L\'ID du message de réponse doit être positif'
        }
    )
    
    # Validation personnalisée
    @validates('content')
    def validate_content(self, value):
        """Valide le contenu du message"""
        if value:
            # Vérifier qu'il n'y a pas de spam
            spam_indicators = ['$$$', '!!!', '???', 'URGENT', 'GRATUIT', 'FREE']
            if any(indicator in value.upper() for indicator in spam_indicators):
                raise ValidationError('Le contenu contient des indicateurs de spam')
            
            # Vérifier qu'il n'y a pas de liens suspects
            if 'http' in value.lower():
                # Autoriser seulement les liens vers des domaines de confiance
                trusted_domains = ['luckykangaroo.com', 'trusted-site.com']
                if not any(domain in value.lower() for domain in trusted_domains):
                    raise ValidationError('Les liens externes ne sont pas autorisés')
    
    @validates('media_url')
    def validate_media_url(self, value):
        """Valide l'URL du média"""
        if value:
            # Vérifier que c'est une URL sécurisée
            if not value.startswith(('https://', 'http://')):
                raise ValidationError('L\'URL du média doit commencer par http:// ou https://')
            
            # Vérifier la taille si spécifiée
            if hasattr(self, 'media_size') and self.media_size:
                if self.media_size > 50*1024*1024:  # 50MB
                    raise ValidationError('La taille du média ne peut pas dépasser 50 MB')
    
    @validates('reply_to_message_id')
    def validate_reply(self, value):
        """Valide la réponse à un message"""
        if value:
            # Vérifier que le message de réponse existe (sera fait au niveau de la logique métier)
            pass

class UpdateChatMessageSchema(Schema):
    """Schéma pour la mise à jour de messages de chat"""
    
    content = fields.Str(
        required=False,
        validate=validate.Length(min=1, max=2000),
        error_messages={
            'validator_failed': 'Le contenu du message doit contenir entre 1 et 2000 caractères'
        }
    )
    
    # Validation personnalisée
    @validates('content')
    def validate_content(self, value):
        """Valide le contenu du message"""
        if value:
            # Vérifier qu'il n'y a pas de spam
            spam_indicators = ['$$$', '!!!', '???', 'URGENT', 'GRATUIT', 'FREE']
            if any(indicator in value.upper() for indicator in spam_indicators):
                raise ValidationError('Le contenu contient des indicateurs de spam')
            
            # Vérifier qu'il n'y a pas de liens suspects
            if 'http' in value.lower():
                # Autoriser seulement les liens vers des domaines de confiance
                trusted_domains = ['luckykangaroo.com', 'trusted-site.com']
                if not any(domain in value.lower() for domain in trusted_domains):
                    raise ValidationError('Les liens externes ne sont pas autorisés')

class ChatRoomSchema(Schema):
    """Schéma de base pour les salles de chat (lecture seule)"""
    
    id = fields.Int(dump_only=True)
    uuid = fields.Str(dump_only=True)
    
    # Participants
    user1_id = fields.Int(dump_only=True)
    user2_id = fields.Int(dump_only=True)
    
    # Échange associé
    exchange_id = fields.Int(dump_only=True, allow_none=True)
    
    # Métadonnées
    title = fields.Str(dump_only=True, allow_none=True)
    is_active = fields.Bool(dump_only=True)
    is_archived = fields.Bool(dump_only=True)
    
    # Dernière activité
    last_message_id = fields.Int(dump_only=True, allow_none=True)
    last_message_at = fields.DateTime(dump_only=True, allow_none=True)
    last_activity_at = fields.DateTime(dump_only=True)
    
    # Compteurs
    total_messages = fields.Int(dump_only=True)
    unread_count_user1 = fields.Int(dump_only=True)
    unread_count_user2 = fields.Int(dump_only=True)
    
    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class CreateChatRoomSchema(Schema):
    """Schéma pour la création de salles de chat"""
    
    user2_id = fields.Int(
        required=True,
        validate=validate.Range(min=1),
        error_messages={
            'required': 'L\'ID du second utilisateur est requis',
            'validator_failed': 'L\'ID de l\'utilisateur doit être positif'
        }
    )
    
    exchange_id = fields.Int(
        required=False,
        validate=validate.Range(min=1),
        error_messages={
            'validator_failed': 'L\'ID de l\'échange doit être positif'
        }
    )
    
    title = fields.Str(
        required=False,
        validate=validate.Length(max=200),
        error_messages={
            'validator_failed': 'Le titre ne peut pas dépasser 200 caractères'
        }
    )
    
    # Validation personnalisée
    @validates('user2_id')
    def validate_user2_id(self, value):
        """Valide l'ID du second utilisateur"""
        # Vérifier que l'utilisateur n'essaie pas de créer un chat avec lui-même
        # (sera fait au niveau de la logique métier avec l'utilisateur connecté)
        pass

class ChatReactionSchema(Schema):
    """Schéma pour les réactions aux messages"""
    
    reaction_type = fields.Str(
        required=True,
        validate=validate.OneOf(['like', 'love', 'laugh', 'wow', 'sad', 'angry', 'heart', 'thumbs_up', 'thumbs_down']),
        error_messages={
            'required': 'Le type de réaction est requis',
            'validator_failed': 'Type de réaction invalide'
        }
    )
    
    # Validation personnalisée
    @validates('reaction_type')
    def validate_reaction_type(self, value):
        """Valide le type de réaction"""
        # Vérifier que la réaction est appropriée pour le contexte
        inappropriate_reactions = ['angry', 'thumbs_down']
        if value in inappropriate_reactions:
            # Log pour modération
            pass

class ChatSearchSchema(Schema):
    """Schéma pour la recherche dans le chat"""
    
    query = fields.Str(
        required=False,
        validate=validate.Length(min=1, max=100),
        error_messages={
            'validator_failed': 'La requête de recherche doit contenir entre 1 et 100 caractères'
        }
    )
    
    message_type = fields.Str(
        required=False,
        validate=validate.OneOf(['all', 'text', 'image', 'system', 'exchange_request', 'exchange_update', 'location']),
        missing='all',
        error_messages={
            'validator_failed': 'Type de message invalide'
        }
    )
    
    date_from = fields.DateTime(
        required=False,
        error_messages={
            'invalid': 'Format de date invalide'
        }
    )
    
    date_to = fields.DateTime(
        required=False,
        error_messages={
            'invalid': 'Format de date invalide'
        }
    )
    
    limit = fields.Int(
        required=False,
        validate=validate.Range(min=1, max=100),
        missing=20,
        error_messages={
            'validator_failed': 'La limite doit être comprise entre 1 et 100'
        }
    )
    
    # Validation personnalisée
    @validates('date_to')
    def validate_date_range(self, value, **kwargs):
        """Valide la plage de dates"""
        date_from = kwargs.get('date_from')
        if value and date_from and value < date_from:
            raise ValidationError('La date de fin doit être postérieure à la date de début')
    
    @validates('query')
    def validate_query(self, value):
        """Valide la requête de recherche"""
        if value:
            # Vérifier qu'il n'y a pas de caractères suspects
            suspicious_chars = ['<', '>', '&', '"', "'", ';', '--']
            if any(char in value for char in suspicious_chars):
                raise ValidationError('La requête contient des caractères non autorisés')
