"""
Schémas de validation pour Lucky Kangaroo
"""

from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from datetime import datetime
import re

class UserRegistrationSchema(Schema):
    """Schéma de validation pour l'inscription utilisateur"""
    username = fields.Str(required=True, validate=[
        validate.Length(min=3, max=50),
        validate.Regexp(r'^[a-zA-Z0-9_-]+$', error='Le nom d\'utilisateur ne peut contenir que des lettres, chiffres, tirets et underscores')
    ])
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=[
        validate.Length(min=8, max=128),
        validate.Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]', 
                       error='Le mot de passe doit contenir au moins une minuscule, une majuscule, un chiffre et un caractère spécial')
    ])
    confirm_password = fields.Str(required=True)
    
    @validates_schema
    def validate_passwords(self, data, **kwargs):
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError('Les mots de passe ne correspondent pas', 'confirm_password')

class UserLoginSchema(Schema):
    """Schéma de validation pour la connexion utilisateur"""
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class ListingCreateSchema(Schema):
    """Schéma de validation pour la création d'annonce"""
    title = fields.Str(required=True, validate=validate.Length(min=5, max=200))
    description = fields.Str(required=True, validate=validate.Length(min=20, max=2000))
    category = fields.Str(required=True)
    condition = fields.Str(required=True, validate=validate.OneOf(['new', 'excellent', 'good', 'fair', 'poor']))
    exchange_type = fields.Str(required=True, validate=validate.OneOf(['barter', 'service_exchange', 'free', 'donation', 'sale']))
    value_estimate = fields.Float(validate=validate.Range(min=0, max=1000000))
    location = fields.Str(required=True, validate=validate.Length(min=2, max=255))
    latitude = fields.Float(validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(validate=validate.Range(min=-180, max=180))
    preferred_exchange_items = fields.Str(validate=validate.Length(max=1000))
    availability = fields.Str(validate=validate.Length(max=500))

class ExchangeProposalSchema(Schema):
    """Schéma de validation pour une proposition d'échange"""
    listing_id = fields.Int(required=True)
    message = fields.Str(validate=validate.Length(max=1000))
    proposed_item_id = fields.Int()
    proposed_service_description = fields.Str(validate=validate.Length(max=1000))
    meeting_preference = fields.Str(validate=validate.OneOf(['direct', 'shipping', 'relay_point']))

class ChatMessageSchema(Schema):
    """Schéma de validation pour un message de chat"""
    message = fields.Str(required=True, validate=validate.Length(min=1, max=2000))
    exchange_id = fields.Int(required=True)

class SearchSchema(Schema):
    """Schéma de validation pour la recherche"""
    query = fields.Str(validate=validate.Length(max=200))
    category = fields.Str()
    condition = fields.Str(validate=validate.OneOf(['new', 'excellent', 'good', 'fair', 'poor']))
    exchange_type = fields.Str(validate=validate.OneOf(['barter', 'service_exchange', 'free', 'donation', 'sale']))
    min_value = fields.Float(validate=validate.Range(min=0))
    max_value = fields.Float(validate=validate.Range(min=0))
    location = fields.Str()
    radius = fields.Int(validate=validate.Range(min=1, max=500))
    latitude = fields.Float(validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(validate=validate.Range(min=-180, max=180))
    sort_by = fields.Str(validate=validate.OneOf(['relevance', 'date', 'distance', 'value']))
    page = fields.Int(validate=validate.Range(min=1), missing=1)
    per_page = fields.Int(validate=validate.Range(min=1, max=100), missing=20)

class ReviewSchema(Schema):
    """Schéma de validation pour un avis"""
    rating = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.Str(validate=validate.Length(max=1000))
    exchange_id = fields.Int()

class UserProfileUpdateSchema(Schema):
    """Schéma de validation pour la mise à jour du profil utilisateur"""
    username = fields.Str(validate=validate.Length(min=3, max=50))
    bio = fields.Str(validate=validate.Length(max=500))
    location = fields.Str(validate=validate.Length(max=255))
    latitude = fields.Float(validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(validate=validate.Range(min=-180, max=180))
    language = fields.Str(validate=validate.OneOf(['fr', 'en', 'de', 'it', 'es', 'pt', 'ru', 'zh']))
    currency = fields.Str(validate=validate.OneOf(['CHF', 'EUR', 'USD', 'GBP', 'CAD', 'JPY']))
    notification_preferences = fields.Dict()

class PasswordResetSchema(Schema):
    """Schéma de validation pour la réinitialisation de mot de passe"""
    email = fields.Email(required=True)

class PasswordResetConfirmSchema(Schema):
    """Schéma de validation pour la confirmation de réinitialisation de mot de passe"""
    token = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=[
        validate.Length(min=8, max=128),
        validate.Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]', 
                       error='Le mot de passe doit contenir au moins une minuscule, une majuscule, un chiffre et un caractère spécial')
    ])
    confirm_password = fields.Str(required=True)
    
    @validates_schema
    def validate_passwords(self, data, **kwargs):
        if data.get('new_password') != data.get('confirm_password'):
            raise ValidationError('Les mots de passe ne correspondent pas', 'confirm_password')

class EmailVerificationSchema(Schema):
    """Schéma de validation pour la vérification d'email"""
    token = fields.Str(required=True)

class TwoFactorSetupSchema(Schema):
    """Schéma de validation pour la configuration 2FA"""
    secret = fields.Str(required=True)
    token = fields.Str(required=True, validate=validate.Length(min=6, max=6))

class TwoFactorVerifySchema(Schema):
    """Schéma de validation pour la vérification 2FA"""
    token = fields.Str(required=True, validate=validate.Length(min=6, max=6))
