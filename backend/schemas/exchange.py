"""
Lucky Kangaroo - Schémas de validation pour les échanges
Validation des données d'entrée avec Marshmallow
"""

from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime, timedelta

class ExchangeSchema(Schema):
    """Schéma de base pour les échanges (lecture seule)"""
    
    id = fields.Int(dump_only=True)
    uuid = fields.Str(dump_only=True)
    
    # Participants
    requester_id = fields.Int(dump_only=True)
    owner_id = fields.Int(dump_only=True)
    
    # Objets échangés
    offered_listing_id = fields.Int(dump_only=True)
    requested_listing_id = fields.Int(dump_only=True)
    
    # Type et statut
    exchange_type = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    
    # Détails de l'échange
    message = fields.Str(dump_only=True, allow_none=True)
    counter_message = fields.Str(dump_only=True, allow_none=True)
    
    # Valeurs et compensation
    offered_value = fields.Float(dump_only=True, allow_none=True)
    requested_value = fields.Float(dump_only=True, allow_none=True)
    compensation_amount = fields.Float(dump_only=True, allow_none=True)
    compensation_currency = fields.Str(dump_only=True, allow_none=True)
    compensation_direction = fields.Str(dump_only=True, allow_none=True)
    
    # Rendez-vous et logistique
    meeting_location = fields.Str(dump_only=True, allow_none=True)
    meeting_latitude = fields.Float(dump_only=True, allow_none=True)
    meeting_longitude = fields.Float(dump_only=True, allow_none=True)
    meeting_datetime = fields.DateTime(dump_only=True, allow_none=True)
    meeting_notes = fields.Str(dump_only=True, allow_none=True)
    
    # Évaluations
    requester_rating = fields.Int(dump_only=True, allow_none=True)
    owner_rating = fields.Int(dump_only=True, allow_none=True)
    requester_review = fields.Str(dump_only=True, allow_none=True)
    owner_review = fields.Str(dump_only=True, allow_none=True)
    
    # Chaîne d'échange
    chain_id = fields.Str(dump_only=True, allow_none=True)
    chain_position = fields.Int(dump_only=True, allow_none=True)
    chain_total_participants = fields.Int(dump_only=True, allow_none=True)
    
    # Modération et sécurité
    is_flagged = fields.Bool(dump_only=True)
    flag_reason = fields.Str(dump_only=True, allow_none=True)
    flagged_by = fields.Int(dump_only=True, allow_none=True)
    flagged_at = fields.DateTime(dump_only=True, allow_none=True)
    
    # Résolution de litige
    dispute_reason = fields.Str(dump_only=True, allow_none=True)
    dispute_resolution = fields.Str(dump_only=True, allow_none=True)
    resolved_by = fields.Int(dump_only=True, allow_none=True)
    resolved_at = fields.DateTime(dump_only=True, allow_none=True)
    
    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    accepted_at = fields.DateTime(dump_only=True, allow_none=True)
    confirmed_at = fields.DateTime(dump_only=True, allow_none=True)
    completed_at = fields.DateTime(dump_only=True, allow_none=True)
    cancelled_at = fields.DateTime(dump_only=True, allow_none=True)
    expires_at = fields.DateTime(dump_only=True, allow_none=True)

class CreateExchangeSchema(Schema):
    """Schéma pour la création d'échanges"""
    
    requested_listing_id = fields.Int(
        required=True,
        validate=validate.Range(min=1),
        error_messages={
            'required': 'L\'ID de l\'annonce demandée est requis',
            'validator_failed': 'L\'ID de l\'annonce doit être positif'
        }
    )
    
    offered_listing_id = fields.Int(
        required=True,
        validate=validate.Range(min=1),
        error_messages={
            'required': 'L\'ID de l\'annonce offerte est requis',
            'validator_failed': 'L\'ID de l\'annonce offerte doit être positif'
        }
    )
    
    message = fields.Str(
        required=False,
        validate=validate.Length(max=1000),
        error_messages={
            'validator_failed': 'Le message ne peut pas dépasser 1000 caractères'
        }
    )
    
    exchange_type = fields.Str(
        required=False,
        validate=validate.OneOf(['direct', 'chain', 'multi']),
        missing='direct',
        error_messages={
            'validator_failed': 'Type d\'échange invalide'
        }
    )
    
    # Validation personnalisée
    @validates('message')
    def validate_message(self, value):
        """Valide le message de l'échange"""
        if value:
            # Vérifier qu'il n'y a pas de spam
            spam_indicators = ['$$$', '!!!', '???', 'URGENT', 'GRATUIT', 'FREE']
            if any(indicator in value.upper() for indicator in spam_indicators):
                raise ValidationError('Le message contient des indicateurs de spam')
            
            # Vérifier qu'il n'y a pas de liens
            if 'http' in value.lower():
                raise ValidationError('Les liens ne sont pas autorisés dans le message')

class UpdateExchangeSchema(Schema):
    """Schéma pour la mise à jour d'échanges"""
    
    status = fields.Str(
        required=False,
        validate=validate.OneOf([
            'requested', 'counter_offered', 'accepted', 'confirmed', 
            'in_progress', 'completed', 'cancelled', 'disputed', 'expired'
        ]),
        error_messages={
            'validator_failed': 'Statut invalide'
        }
    )
    
    message = fields.Str(
        required=False,
        validate=validate.Length(max=1000),
        error_messages={
            'validator_failed': 'Le message ne peut pas dépasser 1000 caractères'
        }
    )
    
    counter_message = fields.Str(
        required=False,
        validate=validate.Length(max=1000),
        error_messages={
            'validator_failed': 'Le message de contre-proposition ne peut pas dépasser 1000 caractères'
        }
    )
    
    compensation_amount = fields.Float(
        required=False,
        validate=validate.Range(min=0, max=10000),
        error_messages={
            'validator_failed': 'Le montant de compensation doit être compris entre 0 et 10 000'
        }
    )
    
    compensation_currency = fields.Str(
        required=False,
        validate=validate.OneOf(['CHF', 'EUR', 'USD', 'GBP', 'CAD', 'JPY']),
        error_messages={
            'validator_failed': 'Devise non supportée'
        }
    )
    
    compensation_direction = fields.Str(
        required=False,
        validate=validate.OneOf(['to_requester', 'to_owner']),
        error_messages={
            'validator_failed': 'Direction de compensation invalide'
        }
    )
    
    # Rendez-vous
    meeting_location = fields.Str(
        required=False,
        validate=validate.Length(max=200),
        error_messages={
            'validator_failed': 'Le lieu de rendez-vous ne peut pas dépasser 200 caractères'
        }
    )
    
    meeting_latitude = fields.Float(
        required=False,
        validate=validate.Range(min=-90, max=90),
        error_messages={
            'validator_failed': 'La latitude du lieu de rendez-vous doit être comprise entre -90 et 90'
        }
    )
    
    meeting_longitude = fields.Float(
        required=False,
        validate=validate.Range(min=-180, max=180),
        error_messages={
            'validator_failed': 'La longitude du lieu de rendez-vous doit être comprise entre -180 et 180'
        }
    )
    
    meeting_datetime = fields.DateTime(
        required=False,
        error_messages={
            'invalid': 'Format de date/heure invalide'
        }
    )
    
    meeting_notes = fields.Str(
        required=False,
        validate=validate.Length(max=500),
        error_messages={
            'validator_failed': 'Les notes de rendez-vous ne peuvent pas dépasser 500 caractères'
        }
    )
    
    # Évaluations
    requester_rating = fields.Int(
        required=False,
        validate=validate.Range(min=1, max=5),
        error_messages={
            'validator_failed': 'La note doit être comprise entre 1 et 5'
        }
    )
    
    owner_rating = fields.Int(
        required=False,
        validate=validate.Range(min=1, max=5),
        error_messages={
            'validator_failed': 'La note doit être comprise entre 1 et 5'
        }
    )
    
    requester_review = fields.Str(
        required=False,
        validate=validate.Length(max=1000),
        error_messages={
            'validator_failed': 'L\'avis ne peut pas dépasser 1000 caractères'
        }
    )
    
    owner_review = fields.Str(
        required=False,
        validate=validate.Length(max=1000),
        error_messages={
            'validator_failed': 'L\'avis ne peut pas dépasser 1000 caractères'
        }
    )
    
    # Validation personnalisée
    @validates('meeting_datetime')
    def validate_meeting_datetime(self, value):
        """Valide la date/heure du rendez-vous"""
        if value:
            now = datetime.utcnow()
            if value < now:
                raise ValidationError('La date du rendez-vous ne peut pas être dans le passé')
            
            if value > now + timedelta(days=30):
                raise ValidationError('La date du rendez-vous ne peut pas être dans plus de 30 jours')
    
    @validates('compensation_amount')
    def validate_compensation(self, value, **kwargs):
        """Valide la compensation"""
        if value is not None and value > 0:
            # Vérifier que la devise est spécifiée
            if not kwargs.get('compensation_currency'):
                raise ValidationError('La devise doit être spécifiée pour une compensation')
            
            # Vérifier que la direction est spécifiée
            if not kwargs.get('compensation_direction'):
                raise ValidationError('La direction de compensation doit être spécifiée')
    
    @validates('message')
    def validate_message(self, value):
        """Valide le message de l'échange"""
        if value:
            # Vérifier qu'il n'y a pas de spam
            spam_indicators = ['$$$', '!!!', '???', 'URGENT', 'GRATUIT', 'FREE']
            if any(indicator in value.upper() for indicator in spam_indicators):
                raise ValidationError('Le message contient des indicateurs de spam')
            
            # Vérifier qu'il n'y a pas de liens
            if 'http' in value.lower():
                raise ValidationError('Les liens ne sont pas autorisés dans le message')

class ExchangeResponseSchema(Schema):
    """Schéma pour les réponses aux échanges"""
    
    action = fields.Str(
        required=True,
        validate=validate.OneOf(['accept', 'reject', 'counter_offer', 'request_info']),
        error_messages={
            'required': 'L\'action est requise',
            'validator_failed': 'Action invalide'
        }
    )
    
    message = fields.Str(
        required=False,
        validate=validate.Length(max=1000),
        error_messages={
            'validator_failed': 'Le message ne peut pas dépasser 1000 caractères'
        }
    )
    
    # Pour les contre-propositions
    counter_offered_listing_id = fields.Int(
        required=False,
        validate=validate.Range(min=1),
        error_messages={
            'validator_failed': 'L\'ID de l\'annonce de contre-proposition doit être positif'
        }
    )
    
    # Pour les demandes d'information
    requested_info = fields.Str(
        required=False,
        validate=validate.Length(max=500),
        error_messages={
            'validator_failed': 'La demande d\'information ne peut pas dépasser 500 caractères'
        }
    )
    
    # Validation personnalisée
    @validates('counter_offered_listing_id')
    def validate_counter_offer(self, value, **kwargs):
        """Valide la contre-proposition"""
        action = kwargs.get('action')
        if action == 'counter_offer' and not value:
            raise ValidationError('L\'ID de l\'annonce de contre-proposition est requis pour une contre-proposition')
    
    @validates('requested_info')
    def validate_requested_info(self, value, **kwargs):
        """Valide la demande d'information"""
        action = kwargs.get('action')
        if action == 'request_info' and not value:
            raise ValidationError('La demande d\'information est requise pour une demande d\'information')
