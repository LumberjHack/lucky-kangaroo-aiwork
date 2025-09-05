"""
Lucky Kangaroo - Schémas de validation pour les utilisateurs
Validation des données d'entrée avec Marshmallow
"""

from marshmallow import Schema, fields, validate, validates, ValidationError
import re
from datetime import date

class UserSchema(Schema):
    """Schéma de base pour les utilisateurs (lecture seule)"""
    
    id = fields.Int(dump_only=True)
    uuid = fields.Str(dump_only=True)
    username = fields.Str(dump_only=True)
    email = fields.Email(dump_only=True)
    first_name = fields.Str(dump_only=True)
    last_name = fields.Str(dump_only=True)
    bio = fields.Str(dump_only=True)
    phone = fields.Str(dump_only=True)
    date_of_birth = fields.Date(dump_only=True)
    
    # Géolocalisation
    latitude = fields.Float(dump_only=True, allow_none=True)
    longitude = fields.Float(dump_only=True, allow_none=True)
    address = fields.Str(dump_only=True, allow_none=True)
    city = fields.Str(dump_only=True, allow_none=True)
    postal_code = fields.Str(dump_only=True, allow_none=True)
    country = fields.Str(dump_only=True, allow_none=True)
    
    # Système de confiance
    trust_score = fields.Float(dump_only=True)
    reputation_score = fields.Float(dump_only=True)
    total_exchanges = fields.Int(dump_only=True)
    successful_exchanges = fields.Int(dump_only=True)
    
    # Préférences
    preferred_language = fields.Str(dump_only=True)
    preferred_currency = fields.Str(dump_only=True)
    max_distance_km = fields.Int(dump_only=True)
    
    # Statut
    is_active = fields.Bool(dump_only=True)
    is_verified = fields.Bool(dump_only=True)
    email_verified = fields.Bool(dump_only=True)
    phone_verified = fields.Bool(dump_only=True)
    
    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    last_activity_at = fields.DateTime(dump_only=True, allow_none=True)

class CreateUserSchema(Schema):
    """Schéma pour la création d'utilisateurs"""
    
    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=30),
        error_messages={
            'required': 'Le nom d\'utilisateur est requis',
            'validator_failed': 'Le nom d\'utilisateur doit contenir entre 3 et 30 caractères'
        }
    )
    
    email = fields.Email(
        required=True,
        error_messages={
            'required': 'L\'email est requis',
            'invalid': 'Format d\'email invalide'
        }
    )
    
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8, max=128),
        error_messages={
            'required': 'Le mot de passe est requis',
            'validator_failed': 'Le mot de passe doit contenir entre 8 et 128 caractères'
        }
    )
    
    first_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50),
        error_messages={
            'required': 'Le prénom est requis',
            'validator_failed': 'Le prénom doit contenir entre 1 et 50 caractères'
        }
    )
    
    last_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50),
        error_messages={
            'required': 'Le nom est requis',
            'validator_failed': 'Le nom doit contenir entre 1 et 50 caractères'
        }
    )
    
    phone = fields.Str(
        required=False,
        validate=validate.Length(max=20),
        error_messages={
            'validator_failed': 'Le numéro de téléphone ne peut pas dépasser 20 caractères'
        }
    )
    
    date_of_birth = fields.Date(
        required=False,
        error_messages={
            'invalid': 'Format de date invalide (YYYY-MM-DD)'
        }
    )
    
    # Géolocalisation optionnelle
    latitude = fields.Float(
        required=False,
        validate=validate.Range(min=-90, max=90),
        error_messages={
            'validator_failed': 'La latitude doit être comprise entre -90 et 90'
        }
    )
    
    longitude = fields.Float(
        required=False,
        validate=validate.Range(min=-180, max=180),
        error_messages={
            'validator_failed': 'La longitude doit être comprise entre -180 et 180'
        }
    )
    
    address = fields.Str(
        required=False,
        validate=validate.Length(max=200),
        error_messages={
            'validator_failed': 'L\'adresse ne peut pas dépasser 200 caractères'
        }
    )
    
    city = fields.Str(
        required=False,
        validate=validate.Length(max=100),
        error_messages={
            'validator_failed': 'Le nom de ville ne peut pas dépasser 100 caractères'
        }
    )
    
    postal_code = fields.Str(
        required=False,
        validate=validate.Length(max=20),
        error_messages={
            'validator_failed': 'Le code postal ne peut pas dépasser 20 caractères'
        }
    )
    
    country = fields.Str(
        required=False,
        validate=validate.Length(max=100),
        error_messages={
            'validator_failed': 'Le nom de pays ne peut pas dépasser 100 caractères'
        }
    )
    
    # Préférences
    preferred_language = fields.Str(
        required=False,
        validate=validate.OneOf(['fr', 'en', 'de', 'it', 'es', 'pt', 'ru', 'zh']),
        missing='fr',
        error_messages={
            'validator_failed': 'Langue non supportée'
        }
    )
    
    preferred_currency = fields.Str(
        required=False,
        validate=validate.OneOf(['CHF', 'EUR', 'USD', 'GBP', 'CAD', 'JPY']),
        missing='CHF',
        error_messages={
            'validator_failed': 'Devise non supportée'
        }
    )
    
    max_distance_km = fields.Int(
        required=False,
        validate=validate.Range(min=1, max=1000),
        missing=50,
        error_messages={
            'validator_failed': 'La distance maximale doit être comprise entre 1 et 1000 km'
        }
    )
    
    # Validation personnalisée
    @validates('username')
    def validate_username(self, value):
        """Valide le format du nom d'utilisateur"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', value):
            raise ValidationError('Le nom d\'utilisateur ne peut contenir que des lettres, chiffres, tirets et underscores')
        
        if value.lower() in ['admin', 'root', 'system', 'test', 'guest']:
            raise ValidationError('Ce nom d\'utilisateur n\'est pas autorisé')
    
    @validates('password')
    def validate_password_strength(self, value):
        """Valide la force du mot de passe"""
        if len(value) < 8:
            raise ValidationError('Le mot de passe doit contenir au moins 8 caractères')
        
        if not re.search(r'[A-Z]', value):
            raise ValidationError('Le mot de passe doit contenir au moins une majuscule')
        
        if not re.search(r'[a-z]', value):
            raise ValidationError('Le mot de passe doit contenir au moins une minuscule')
        
        if not re.search(r'\d', value):
            raise ValidationError('Le mot de passe doit contenir au moins un chiffre')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError('Le mot de passe doit contenir au moins un caractère spécial')
    
    @validates('date_of_birth')
    def validate_date_of_birth(self, value):
        """Valide la date de naissance"""
        if value:
            today = date.today()
            age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
            
            if age < 13:
                raise ValidationError('L\'utilisateur doit avoir au moins 13 ans')
            
            if age > 120:
                raise ValidationError('Date de naissance invalide')
    
    @validates('phone')
    def validate_phone(self, value):
        """Valide le format du numéro de téléphone"""
        if value:
            # Supprimer les espaces et caractères spéciaux
            clean_phone = re.sub(r'[\s\-\(\)\+]', '', value)
            
            if not re.match(r'^\+?[1-9]\d{7,14}$', clean_phone):
                raise ValidationError('Format de numéro de téléphone invalide')

class UpdateUserSchema(Schema):
    """Schéma pour la mise à jour d'utilisateurs"""
    
    username = fields.Str(
        required=False,
        validate=validate.Length(min=3, max=30),
        error_messages={
            'validator_failed': 'Le nom d\'utilisateur doit contenir entre 3 et 30 caractères'
        }
    )
    
    first_name = fields.Str(
        required=False,
        validate=validate.Length(min=1, max=50),
        error_messages={
            'validator_failed': 'Le prénom doit contenir entre 1 et 50 caractères'
        }
    )
    
    last_name = fields.Str(
        required=False,
        validate=validate.Length(min=1, max=50),
        error_messages={
            'validator_failed': 'Le nom doit contenir entre 1 et 50 caractères'
        }
    )
    
    bio = fields.Str(
        required=False,
        validate=validate.Length(max=500),
        error_messages={
            'validator_failed': 'La bio ne peut pas dépasser 500 caractères'
        }
    )
    
    phone = fields.Str(
        required=False,
        validate=validate.Length(max=20),
        error_messages={
            'validator_failed': 'Le numéro de téléphone ne peut pas dépasser 20 caractères'
        }
    )
    
    date_of_birth = fields.Date(
        required=False,
        error_messages={
            'invalid': 'Format de date invalide (YYYY-MM-DD)'
        }
    )
    
    # Géolocalisation
    latitude = fields.Float(
        required=False,
        validate=validate.Range(min=-90, max=90),
        error_messages={
            'validator_failed': 'La latitude doit être comprise entre -90 et 90'
        }
    )
    
    longitude = fields.Float(
        required=False,
        validate=validate.Range(min=-180, max=180),
        error_messages={
            'validator_failed': 'La longitude doit être comprise entre -180 et 180'
        }
    )
    
    address = fields.Str(
        required=False,
        validate=validate.Length(max=200),
        error_messages={
            'validator_failed': 'L\'adresse ne peut pas dépasser 200 caractères'
        }
    )
    
    city = fields.Str(
        required=False,
        validate=validate.Length(max=100),
        error_messages={
            'validator_failed': 'Le nom de ville ne peut pas dépasser 100 caractères'
        }
    )
    
    postal_code = fields.Str(
        required=False,
        validate=validate.Length(max=20),
        error_messages={
            'validator_failed': 'Le code postal ne peut pas dépasser 20 caractères'
        }
    )
    
    country = fields.Str(
        required=False,
        validate=validate.Length(max=100),
        error_messages={
            'validator_failed': 'Le nom de pays ne peut pas dépasser 100 caractères'
        }
    )
    
    # Préférences
    preferred_language = fields.Str(
        required=False,
        validate=validate.OneOf(['fr', 'en', 'de', 'it', 'es', 'pt', 'ru', 'zh']),
        error_messages={
            'validator_failed': 'Langue non supportée'
        }
    )
    
    preferred_currency = fields.Str(
        required=False,
        validate=validate.OneOf(['CHF', 'EUR', 'USD', 'GBP', 'CAD', 'JPY']),
        error_messages={
            'validator_failed': 'Devise non supportée'
        }
    )
    
    max_distance_km = fields.Int(
        required=False,
        validate=validate.Range(min=1, max=1000),
        error_messages={
            'validator_failed': 'La distance maximale doit être comprise entre 1 et 1000 km'
        }
    )
    
    # Validation personnalisée
    @validates('username')
    def validate_username(self, value):
        """Valide le format du nom d'utilisateur"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', value):
            raise ValidationError('Le nom d\'utilisateur ne peut contenir que des lettres, chiffres, tirets et underscores')
        
        if value.lower() in ['admin', 'root', 'system', 'test', 'guest']:
            raise ValidationError('Ce nom d\'utilisateur n\'est pas autorisé')
    
    @validates('date_of_birth')
    def validate_date_of_birth(self, value):
        """Valide la date de naissance"""
        if value:
            today = date.today()
            age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
            
            if age < 13:
                raise ValidationError('L\'utilisateur doit avoir au moins 13 ans')
            
            if age > 120:
                raise ValidationError('Date de naissance invalide')
    
    @validates('phone')
    def validate_phone(self, value):
        """Valide le format du numéro de téléphone"""
        if value:
            # Supprimer les espaces et caractères spéciaux
            clean_phone = re.sub(r'[\s\-\(\)\+]', '', value)
            
            if not re.match(r'^\+?[1-9]\d{7,14}$', clean_phone):
                raise ValidationError('Format de numéro de téléphone invalide')

class ChangePasswordSchema(Schema):
    """Schéma pour le changement de mot de passe"""
    
    current_password = fields.Str(
        required=True,
        error_messages={
            'required': 'Le mot de passe actuel est requis'
        }
    )
    
    new_password = fields.Str(
        required=True,
        validate=validate.Length(min=8, max=128),
        error_messages={
            'required': 'Le nouveau mot de passe est requis',
            'validator_failed': 'Le nouveau mot de passe doit contenir entre 8 et 128 caractères'
        }
    )
    
    confirm_password = fields.Str(
        required=True,
        error_messages={
            'required': 'La confirmation du mot de passe est requise'
        }
    )
    
    @validates('new_password')
    def validate_new_password_strength(self, value):
        """Valide la force du nouveau mot de passe"""
        if len(value) < 8:
            raise ValidationError('Le mot de passe doit contenir au moins 8 caractères')
        
        if not re.search(r'[A-Z]', value):
            raise ValidationError('Le mot de passe doit contenir au moins une majuscule')
        
        if not re.search(r'[a-z]', value):
            raise ValidationError('Le mot de passe doit contenir au moins une minuscule')
        
        if not re.search(r'\d', value):
            raise ValidationError('Le mot de passe doit contenir au moins un chiffre')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError('Le mot de passe doit contenir au moins un caractère spécial')
    
    @validates('confirm_password')
    def validate_password_confirmation(self, value, **kwargs):
        """Valide la confirmation du mot de passe"""
        if 'new_password' in kwargs and value != kwargs['new_password']:
            raise ValidationError('Les mots de passe ne correspondent pas')
