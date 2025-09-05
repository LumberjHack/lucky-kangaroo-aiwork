"""
Lucky Kangaroo - Schémas de validation pour les paiements
Validation des données d'entrée avec Marshmallow
"""

from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime, timedelta

class PaymentSchema(Schema):
    """Schéma de base pour les paiements (lecture seule)"""
    
    id = fields.Str(dump_only=True)
    user_id = fields.Int(dump_only=True)
    
    # Montant et devise
    amount = fields.Float(dump_only=True)
    currency = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    description = fields.Str(dump_only=True, allow_none=True)
    
    # Métadonnées
    metadata = fields.Str(dump_only=True, allow_none=True)  # JSON
    
    # Méthode de paiement
    payment_method_id = fields.Str(dump_only=True, allow_none=True)
    payment_method_type = fields.Str(dump_only=True, allow_none=True)
    payment_method_last4 = fields.Str(dump_only=True, allow_none=True)
    
    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    paid_at = fields.DateTime(dump_only=True, allow_none=True)
    
    # Relations
    subscription = fields.Nested('SubscriptionSchema', dump_only=True, allow_none=True)

class CreatePaymentSchema(Schema):
    """Schéma pour la création de paiements"""
    
    amount = fields.Float(
        required=True,
        validate=validate.Range(min=0.01, max=10000),
        error_messages={
            'required': 'Le montant est requis',
            'validator_failed': 'Le montant doit être compris entre 0.01 et 10 000'
        }
    )
    
    currency = fields.Str(
        required=True,
        validate=validate.OneOf(['CHF', 'EUR', 'USD', 'GBP', 'CAD', 'JPY']),
        error_messages={
            'required': 'La devise est requise',
            'validator_failed': 'Devise non supportée'
        }
    )
    
    description = fields.Str(
        required=False,
        validate=validate.Length(max=500),
        error_messages={
            'validator_failed': 'La description ne peut pas dépasser 500 caractères'
        }
    )
    
    payment_method_id = fields.Str(
        required=False,
        validate=validate.Length(max=100),
        error_messages={
            'validator_failed': 'L\'ID de la méthode de paiement ne peut pas dépasser 100 caractères'
        }
    )
    
    metadata = fields.Str(
        required=False,
        validate=validate.Length(max=1000),
        error_messages={
            'validator_failed': 'Les métadonnées ne peuvent pas dépasser 1000 caractères'
        }
    )
    
    # Validation personnalisée
    @validates('amount')
    def validate_amount(self, value):
        """Valide le montant du paiement"""
        if value <= 0:
            raise ValidationError('Le montant doit être positif')
        
        # Vérifier que le montant est raisonnable selon la devise
        if self.context.get('currency') == 'CHF' and value > 1000:
            # Log pour modération des gros montants
            pass
    
    @validates('description')
    def validate_description(self, value):
        """Valide la description du paiement"""
        if value:
            # Vérifier qu'il n'y a pas de caractères suspects
            suspicious_chars = ['<', '>', '&', '"', "'", ';', '--']
            if any(char in value for char in suspicious_chars):
                raise ValidationError('La description contient des caractères non autorisés')

class SubscriptionPlanSchema(Schema):
    """Schéma de base pour les plans d'abonnement (lecture seule)"""
    
    id = fields.Str(dump_only=True)
    name = fields.Str(dump_only=True)
    description = fields.Str(dump_only=True, allow_none=True)
    price = fields.Float(dump_only=True)
    currency = fields.Str(dump_only=True)
    billing_interval = fields.Str(dump_only=True)
    trial_period_days = fields.Int(dump_only=True)
    is_active = fields.Bool(dump_only=True)
    features = fields.Str(dump_only=True, allow_none=True)  # JSON
    metadata = fields.Str(dump_only=True, allow_none=True)  # JSON
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class CreateSubscriptionSchema(Schema):
    """Schéma pour la création d'abonnements"""
    
    plan_id = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={
            'required': 'L\'ID du plan est requis',
            'validator_failed': 'L\'ID du plan doit contenir entre 1 et 100 caractères'
        }
    )
    
    payment_method_id = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={
            'required': 'L\'ID de la méthode de paiement est requis',
            'validator_failed': 'L\'ID de la méthode de paiement doit contenir entre 1 et 100 caractères'
        }
    )
    
    trial_period_days = fields.Int(
        required=False,
        validate=validate.Range(min=0, max=30),
        error_messages={
            'validator_failed': 'La période d\'essai doit être comprise entre 0 et 30 jours'
        }
    )
    
    # Validation personnalisée
    @validates('plan_id')
    def validate_plan_id(self, value):
        """Valide l'ID du plan d'abonnement"""
        # Vérifier que le plan existe et est actif (sera fait au niveau de la logique métier)
        pass

class UpdateSubscriptionSchema(Schema):
    """Schéma pour la mise à jour d'abonnements"""
    
    payment_method_id = fields.Str(
        required=False,
        validate=validate.Length(min=1, max=100),
        error_messages={
            'validator_failed': 'L\'ID de la méthode de paiement doit contenir entre 1 et 100 caractères'
        }
    )
    
    # Validation personnalisée
    @validates('payment_method_id')
    def validate_payment_method_id(self, value):
        """Valide l'ID de la méthode de paiement"""
        if value:
            # Vérifier que la méthode de paiement existe (sera fait au niveau de la logique métier)
            pass

class PaymentMethodSchema(Schema):
    """Schéma de base pour les méthodes de paiement (lecture seule)"""
    
    id = fields.Str(dump_only=True)
    user_id = fields.Int(dump_only=True)
    
    # Détails de la méthode
    type = fields.Str(dump_only=True)
    brand = fields.Str(dump_only=True, allow_none=True)
    last4 = fields.Str(dump_only=True, allow_none=True)
    exp_month = fields.Int(dump_only=True, allow_none=True)
    exp_year = fields.Int(dump_only=True, allow_none=True)
    
    # Statut
    is_default = fields.Bool(dump_only=True)
    is_active = fields.Bool(dump_only=True)
    
    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class CreatePaymentMethodSchema(Schema):
    """Schéma pour la création de méthodes de paiement"""
    
    type = fields.Str(
        required=True,
        validate=validate.OneOf(['card', 'paypal', 'bank_account', 'apple_pay', 'google_pay']),
        error_messages={
            'required': 'Le type de méthode de paiement est requis',
            'validator_failed': 'Type de méthode de paiement invalide'
        }
    )
    
    token = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=500),
        error_messages={
            'required': 'Le token de paiement est requis',
            'validator_failed': 'Le token ne peut pas dépasser 500 caractères'
        }
    )
    
    is_default = fields.Bool(
        required=False,
        missing=False,
        error_messages={
            'validator_failed': 'La valeur par défaut doit être un booléen'
        }
    )
    
    # Validation personnalisée
    @validates('token')
    def validate_token(self, value):
        """Valide le token de paiement"""
        if value:
            # Vérifier que le token est valide (sera fait au niveau de la logique métier)
            pass

class UpdatePaymentMethodSchema(Schema):
    """Schéma pour la mise à jour de méthodes de paiement"""
    
    is_default = fields.Bool(
        required=False,
        error_messages={
            'validator_failed': 'La valeur par défaut doit être un booléen'
        }
    )
    
    is_active = fields.Bool(
        required=False,
        error_messages={
            'validator_failed': 'Le statut actif doit être un booléen'
        }
    )

class RefundSchema(Schema):
    """Schéma pour les remboursements"""
    
    payment_id = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={
            'required': 'L\'ID du paiement est requis',
            'validator_failed': 'L\'ID du paiement doit contenir entre 1 et 100 caractères'
        }
    )
    
    amount = fields.Float(
        required=False,
        validate=validate.Range(min=0.01),
        error_messages={
            'validator_failed': 'Le montant du remboursement doit être positif'
        }
    )
    
    reason = fields.Str(
        required=True,
        validate=validate.OneOf([
            'duplicate', 'fraudulent', 'requested_by_customer', 'defective_product',
            'service_not_as_described', 'other'
        ]),
        error_messages={
            'required': 'La raison du remboursement est requise',
            'validator_failed': 'Raison de remboursement invalide'
        }
    )
    
    description = fields.Str(
        required=False,
        validate=validate.Length(max=500),
        error_messages={
            'validator_failed': 'La description ne peut pas dépasser 500 caractères'
        }
    )
    
    # Validation personnalisée
    @validates('amount')
    def validate_refund_amount(self, value, **kwargs):
        """Valide le montant du remboursement"""
        if value is not None:
            payment_id = kwargs.get('payment_id')
            # Vérifier que le montant ne dépasse pas le montant du paiement (sera fait au niveau de la logique métier)
            pass

class InvoiceSchema(Schema):
    """Schéma de base pour les factures (lecture seule)"""
    
    id = fields.Str(dump_only=True)
    user_id = fields.Int(dump_only=True)
    
    # Détails de la facture
    number = fields.Str(dump_only=True)
    amount = fields.Float(dump_only=True)
    currency = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    
    # Période de facturation
    period_start = fields.DateTime(dump_only=True)
    period_end = fields.DateTime(dump_only=True)
    
    # Paiement
    payment_id = fields.Str(dump_only=True, allow_none=True)
    paid_at = fields.DateTime(dump_only=True, allow_none=True)
    
    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    due_date = fields.DateTime(dump_only=True)
    
    # Relations
    subscription = fields.Nested('SubscriptionSchema', dump_only=True, allow_none=True)
    items = fields.Str(dump_only=True, allow_none=True)  # JSON

class CreateInvoiceSchema(Schema):
    """Schéma pour la création de factures"""
    
    user_id = fields.Int(
        required=True,
        validate=validate.Range(min=1),
        error_messages={
            'required': 'L\'ID de l\'utilisateur est requis',
            'validator_failed': 'L\'ID de l\'utilisateur doit être positif'
        }
    )
    
    amount = fields.Float(
        required=True,
        validate=validate.Range(min=0.01),
        error_messages={
            'required': 'Le montant est requis',
            'validator_failed': 'Le montant doit être positif'
        }
    )
    
    currency = fields.Str(
        required=True,
        validate=validate.OneOf(['CHF', 'EUR', 'USD', 'GBP', 'CAD', 'JPY']),
        error_messages={
            'required': 'La devise est requise',
            'validator_failed': 'Devise non supportée'
        }
    )
    
    period_start = fields.DateTime(
        required=False,
        error_messages={
            'invalid': 'Format de date/heure invalide'
        }
    )
    
    period_end = fields.DateTime(
        required=False,
        error_messages={
            'invalid': 'Format de date/heure invalide'
        }
    )
    
    due_date = fields.DateTime(
        required=False,
        error_messages={
            'invalid': 'Format de date/heure invalide'
        }
    )
    
    # Validation personnalisée
    @validates('period_end')
    def validate_period(self, value, **kwargs):
        """Valide la période de facturation"""
        period_start = kwargs.get('period_start')
        if value and period_start and value <= period_start:
            raise ValidationError('La fin de période doit être postérieure au début')
    
    @validates('due_date')
    def validate_due_date(self, value):
        """Valide la date d'échéance"""
        if value:
            now = datetime.utcnow()
            if value < now:
                raise ValidationError('La date d\'échéance ne peut pas être dans le passé')
