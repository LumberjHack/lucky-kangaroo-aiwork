"""
Lucky Kangaroo - Schémas de validation pour les annonces
Validation des données d'entrée avec Marshmallow
"""

from marshmallow import Schema, fields, validate, validates, ValidationError
import re
from datetime import datetime, timedelta

class ListingSchema(Schema):
    """Schéma de base pour les annonces (lecture seule)"""
    
    id = fields.Int(dump_only=True)
    uuid = fields.Str(dump_only=True)
    user_id = fields.Int(dump_only=True)
    
    # Informations de base
    title = fields.Str(dump_only=True)
    description = fields.Str(dump_only=True)
    category = fields.Str(dump_only=True)
    subcategory = fields.Str(dump_only=True, allow_none=True)
    
    # Détails de l'objet
    brand = fields.Str(dump_only=True, allow_none=True)
    model = fields.Str(dump_only=True, allow_none=True)
    color = fields.Str(dump_only=True, allow_none=True)
    size = fields.Str(dump_only=True, allow_none=True)
    condition = fields.Str(dump_only=True)
    condition_details = fields.Str(dump_only=True, allow_none=True)
    
    # Valeur et échange
    estimated_value = fields.Float(dump_only=True, allow_none=True)
    min_exchange_value = fields.Float(dump_only=True, allow_none=True)
    max_exchange_value = fields.Float(dump_only=True, allow_none=True)
    currency = fields.Str(dump_only=True)
    
    # Préférences d'échange
    desired_items = fields.Str(dump_only=True, allow_none=True)
    desired_categories = fields.Str(dump_only=True, allow_none=True)
    exchange_type = fields.Str(dump_only=True)
    
    # Géolocalisation
    latitude = fields.Float(dump_only=True, allow_none=True)
    longitude = fields.Float(dump_only=True, allow_none=True)
    address = fields.Str(dump_only=True, allow_none=True)
    city = fields.Str(dump_only=True, allow_none=True)
    postal_code = fields.Str(dump_only=True, allow_none=True)
    country = fields.Str(dump_only=True, allow_none=True)
    max_distance_km = fields.Int(dump_only=True)
    
    # Photos
    main_photo_url = fields.Str(dump_only=True, allow_none=True)
    photo_count = fields.Int(dump_only=True)
    
    # Statut et visibilité
    status = fields.Str(dump_only=True)
    is_featured = fields.Bool(dump_only=True)
    is_urgent = fields.Bool(dump_only=True)
    is_negotiable = fields.Bool(dump_only=True)
    
    # Statistiques
    view_count = fields.Int(dump_only=True)
    like_count = fields.Int(dump_only=True)
    contact_count = fields.Int(dump_only=True)
    exchange_requests_count = fields.Int(dump_only=True)
    
    # IA et matching
    ai_tags = fields.Str(dump_only=True, allow_none=True)
    ai_category_confidence = fields.Float(dump_only=True, allow_none=True)
    ai_value_estimate = fields.Float(dump_only=True, allow_none=True)
    ai_condition_assessment = fields.Str(dump_only=True, allow_none=True)
    matching_keywords = fields.Str(dump_only=True, allow_none=True)
    
    # Dates importantes
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    published_at = fields.DateTime(dump_only=True, allow_none=True)
    expires_at = fields.DateTime(dump_only=True, allow_none=True)
    last_activity_at = fields.DateTime(dump_only=True, allow_none=True)

class CreateListingSchema(Schema):
    """Schéma pour la création d'annonces"""
    
    title = fields.Str(
        required=True,
        validate=validate.Length(min=5, max=200),
        error_messages={
            'required': 'Le titre est requis',
            'validator_failed': 'Le titre doit contenir entre 5 et 200 caractères'
        }
    )
    
    description = fields.Str(
        required=True,
        validate=validate.Length(min=20, max=2000),
        error_messages={
            'required': 'La description est requise',
            'validator_failed': 'La description doit contenir entre 20 et 2000 caractères'
        }
    )
    
    category = fields.Str(
        required=True,
        validate=validate.OneOf([
            'antiquites', 'electromenager', 'art', 'vehicules_recreatifs', 'pieces_auto',
            'aviation', 'bebes_enfants', 'barter', 'beaute_sante', 'velos', 'bateaux',
            'livres', 'materiel_pro', 'voitures', 'telephones', 'vetements', 'ordinateurs',
            'electronique', 'equipement_agricole', 'meubles', 'ventes_garage', 'articles_generaux',
            'engins', 'bijoux', 'materiaux', 'pieces_moto', 'instruments', 'photo_video',
            'camping', 'sport', 'billetterie', 'jeux', 'jeux_video', 'jantes_pneus',
            'animaux', 'immobilier', 'services_auto', 'services_beaute', 'services_informatique',
            'services_creatifs', 'services_evenementiel', 'services_agricoles', 'services_financiers',
            'services_sante', 'services_maison', 'services_cours', 'services_marins',
            'services_travaux', 'services_voyages', 'services_animaliers', 'services_marketing',
            'services_medicaux'
        ]),
        error_messages={
            'required': 'La catégorie est requise',
            'validator_failed': 'Catégorie invalide'
        }
    )
    
    subcategory = fields.Str(
        required=False,
        validate=validate.Length(max=100),
        error_messages={
            'validator_failed': 'La sous-catégorie ne peut pas dépasser 100 caractères'
        }
    )
    
    brand = fields.Str(
        required=False,
        validate=validate.Length(max=100),
        error_messages={
            'validator_failed': 'La marque ne peut pas dépasser 100 caractères'
        }
    )
    
    model = fields.Str(
        required=False,
        validate=validate.Length(max=100),
        error_messages={
            'validator_failed': 'Le modèle ne peut pas dépasser 100 caractères'
        }
    )
    
    color = fields.Str(
        required=False,
        validate=validate.Length(max=50),
        error_messages={
            'validator_failed': 'La couleur ne peut pas dépasser 50 caractères'
        }
    )
    
    size = fields.Str(
        required=False,
        validate=validate.Length(max=50),
        error_messages={
            'validator_failed': 'La taille ne peut pas dépasser 50 caractères'
        }
    )
    
    condition = fields.Str(
        required=True,
        validate=validate.OneOf(['excellent', 'very_good', 'good', 'fair', 'poor']),
        error_messages={
            'required': 'L\'état de l\'objet est requis',
            'validator_failed': 'État invalide'
        }
    )
    
    condition_details = fields.Str(
        required=False,
        validate=validate.Length(max=500),
        error_messages={
            'validator_failed': 'Les détails de l\'état ne peuvent pas dépasser 500 caractères'
        }
    )
    
    estimated_value = fields.Float(
        required=True,
        validate=validate.Range(min=0, max=1000000),
        error_messages={
            'required': 'La valeur estimée est requise',
            'validator_failed': 'La valeur estimée doit être comprise entre 0 et 1 000 000'
        }
    )
    
    min_exchange_value = fields.Float(
        required=False,
        validate=validate.Range(min=0, max=1000000),
        error_messages={
            'validator_failed': 'La valeur minimum d\'échange doit être comprise entre 0 et 1 000 000'
        }
    )
    
    max_exchange_value = fields.Float(
        required=False,
        validate=validate.Range(min=0, max=1000000),
        error_messages={
            'validator_failed': 'La valeur maximum d\'échange doit être comprise entre 0 et 1 000 000'
        }
    )
    
    currency = fields.Str(
        required=False,
        validate=validate.OneOf(['CHF', 'EUR', 'USD', 'GBP', 'CAD', 'JPY']),
        missing='CHF',
        error_messages={
            'validator_failed': 'Devise non supportée'
        }
    )
    
    desired_items = fields.Str(
        required=False,
        validate=validate.Length(max=1000),
        error_messages={
            'validator_failed': 'Les objets désirés ne peuvent pas dépasser 1000 caractères'
        }
    )
    
    desired_categories = fields.Str(
        required=False,
        validate=validate.Length(max=500),
        error_messages={
            'validator_failed': 'Les catégories désirées ne peuvent pas dépasser 500 caractères'
        }
    )
    
    exchange_type = fields.Str(
        required=False,
        validate=validate.OneOf(['direct', 'chain', 'both']),
        missing='direct',
        error_messages={
            'validator_failed': 'Type d\'échange invalide'
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
        missing='France',
        error_messages={
            'validator_failed': 'Le nom de pays ne peut pas dépasser 100 caractères'
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
    @validates('title')
    def validate_title(self, value):
        """Valide le titre de l'annonce"""
        # Vérifier qu'il n'y a pas de spam
        spam_words = ['gratuit', 'free', 'urgent', 'vite', 'dernière chance', 'last chance']
        if any(word.lower() in value.lower() for word in spam_words):
            raise ValidationError('Le titre contient des mots interdits')
        
        # Vérifier qu'il n'y a pas de caractères répétitifs excessifs
        if re.search(r'(.)\1{4,}', value):
            raise ValidationError('Le titre contient trop de caractères répétés')
    
    @validates('description')
    def validate_description(self, value):
        """Valide la description de l'annonce"""
        # Vérifier qu'il n'y a pas de liens suspects
        if re.search(r'https?://[^\s]+', value):
            raise ValidationError('Les liens ne sont pas autorisés dans la description')
        
        # Vérifier qu'il n'y a pas de spam
        spam_indicators = ['$$$', '!!!', '???', 'URGENT', 'GRATUIT', 'FREE']
        if any(indicator in value.upper() for indicator in spam_indicators):
            raise ValidationError('La description contient des indicateurs de spam')
    
    @validates('estimated_value')
    def validate_estimated_value(self, value):
        """Valide la valeur estimée"""
        if value <= 0:
            raise ValidationError('La valeur estimée doit être positive')
        
        # Vérifier que la valeur n'est pas suspecte
        if value > 100000 and self.context.get('user_trust_score', 50) < 70:
            raise ValidationError('Valeur élevée requiert un trust score plus élevé')
    
    @validates('min_exchange_value')
    def validate_min_exchange_value(self, value, **kwargs):
        """Valide la valeur minimum d'échange"""
        if value is not None:
            estimated_value = kwargs.get('estimated_value')
            if estimated_value and value > estimated_value:
                raise ValidationError('La valeur minimum d\'échange ne peut pas dépasser la valeur estimée')
    
    @validates('max_exchange_value')
    def validate_max_exchange_value(self, value, **kwargs):
        """Valide la valeur maximum d'échange"""
        if value is not None:
            estimated_value = kwargs.get('estimated_value')
            if estimated_value and value < estimated_value:
                raise ValidationError('La valeur maximum d\'échange ne peut pas être inférieure à la valeur estimée')
    
    @validates('latitude')
    def validate_coordinates(self, value, **kwargs):
        """Valide les coordonnées géographiques"""
        longitude = kwargs.get('longitude')
        if value is not None and longitude is not None:
            # Vérifier que les coordonnées sont dans des limites raisonnables pour la France
            if not (-5 <= longitude <= 10 and 41 <= value <= 52):
                raise ValidationError('Coordonnées géographiques invalides pour la France')

class UpdateListingSchema(Schema):
    """Schéma pour la mise à jour d'annonces"""
    
    title = fields.Str(
        required=False,
        validate=validate.Length(min=5, max=200),
        error_messages={
            'validator_failed': 'Le titre doit contenir entre 5 et 200 caractères'
        }
    )
    
    description = fields.Str(
        required=False,
        validate=validate.Length(min=20, max=2000),
        error_messages={
            'validator_failed': 'La description doit contenir entre 20 et 2000 caractères'
        }
    )
    
    category = fields.Str(
        required=False,
        validate=validate.OneOf([
            'antiquites', 'electromenager', 'art', 'vehicules_recreatifs', 'pieces_auto',
            'aviation', 'bebes_enfants', 'barter', 'beaute_sante', 'velos', 'bateaux',
            'livres', 'materiel_pro', 'voitures', 'telephones', 'vetements', 'ordinateurs',
            'electronique', 'equipement_agricole', 'meubles', 'ventes_garage', 'articles_generaux',
            'engins', 'bijoux', 'materiaux', 'pieces_moto', 'instruments', 'photo_video',
            'camping', 'sport', 'billetterie', 'jeux', 'jeux_video', 'jantes_pneus',
            'animaux', 'immobilier', 'services_auto', 'services_beaute', 'services_informatique',
            'services_creatifs', 'services_evenementiel', 'services_agricoles', 'services_financiers',
            'services_sante', 'services_maison', 'services_cours', 'services_marins',
            'services_travaux', 'services_voyages', 'services_animaliers', 'services_marketing',
            'services_medicaux'
        ]),
        error_messages={
            'validator_failed': 'Catégorie invalide'
        }
    )
    
    subcategory = fields.Str(
        required=False,
        validate=validate.Length(max=100),
        error_messages={
            'validator_failed': 'La sous-catégorie ne peut pas dépasser 100 caractères'
        }
    )
    
    brand = fields.Str(
        required=False,
        validate=validate.Length(max=100),
        error_messages={
            'validator_failed': 'La marque ne peut pas dépasser 100 caractères'
        }
    )
    
    model = fields.Str(
        required=False,
        validate=validate.Length(max=100),
        error_messages={
            'validator_failed': 'Le modèle ne peut pas dépasser 100 caractères'
        }
    )
    
    color = fields.Str(
        required=False,
        validate=validate.Length(max=50),
        error_messages={
            'validator_failed': 'La couleur ne peut pas dépasser 50 caractères'
        }
    )
    
    size = fields.Str(
        required=False,
        validate=validate.Length(max=50),
        error_messages={
            'validator_failed': 'La taille ne peut pas dépasser 50 caractères'
        }
    )
    
    condition = fields.Str(
        required=False,
        validate=validate.OneOf(['excellent', 'very_good', 'good', 'fair', 'poor']),
        error_messages={
            'validator_failed': 'État invalide'
        }
    )
    
    condition_details = fields.Str(
        required=False,
        validate=validate.Length(max=500),
        error_messages={
            'validator_failed': 'Les détails de l\'état ne peuvent pas dépasser 500 caractères'
        }
    )
    
    estimated_value = fields.Float(
        required=False,
        validate=validate.Range(min=0, max=1000000),
        error_messages={
            'validator_failed': 'La valeur estimée doit être comprise entre 0 et 1 000 000'
        }
    )
    
    min_exchange_value = fields.Float(
        required=False,
        validate=validate.Range(min=0, max=1000000),
        error_messages={
            'validator_failed': 'La valeur minimum d\'échange doit être comprise entre 0 et 1 000 000'
        }
    )
    
    max_exchange_value = fields.Float(
        required=False,
        validate=validate.Range(min=0, max=1000000),
        error_messages={
            'validator_failed': 'La valeur maximum d\'échange doit être comprise entre 0 et 1 000 000'
        }
    )
    
    currency = fields.Str(
        required=False,
        validate=validate.OneOf(['CHF', 'EUR', 'USD', 'GBP', 'CAD', 'JPY']),
        error_messages={
            'validator_failed': 'Devise non supportée'
        }
    )
    
    desired_items = fields.Str(
        required=False,
        validate=validate.Length(max=1000),
        error_messages={
            'validator_failed': 'Les objets désirés ne peuvent pas dépasser 1000 caractères'
        }
    )
    
    desired_categories = fields.Str(
        required=False,
        validate=validate.Length(max=500),
        error_messages={
            'validator_failed': 'Les catégories désirées ne peuvent pas dépasser 500 caractères'
        }
    )
    
    exchange_type = fields.Str(
        required=False,
        validate=validate.OneOf(['direct', 'chain', 'both']),
        error_messages={
            'validator_failed': 'Type d\'échange invalide'
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
    
    max_distance_km = fields.Int(
        required=False,
        validate=validate.Range(min=1, max=1000),
        error_messages={
            'validator_failed': 'La distance maximale doit être comprise entre 1 et 1000 km'
        }
    )
    
    # Statut
    status = fields.Str(
        required=False,
        validate=validate.OneOf(['draft', 'active', 'paused', 'expired', 'deleted']),
        error_messages={
            'validator_failed': 'Statut invalide'
        }
    )
    
    # Validation personnalisée
    @validates('title')
    def validate_title(self, value):
        """Valide le titre de l'annonce"""
        # Vérifier qu'il n'y a pas de spam
        spam_words = ['gratuit', 'free', 'urgent', 'vite', 'dernière chance', 'last chance']
        if any(word.lower() in value.lower() for word in spam_words):
            raise ValidationError('Le titre contient des mots interdits')
        
        # Vérifier qu'il n'y a pas de caractères répétitifs excessifs
        if re.search(r'(.)\1{4,}', value):
            raise ValidationError('Le titre contient trop de caractères répétés')
    
    @validates('description')
    def validate_description(self, value):
        """Valide la description de l'annonce"""
        # Vérifier qu'il n'y a pas de liens suspects
        if re.search(r'https?://[^\s]+', value):
            raise ValidationError('Les liens ne sont pas autorisés dans la description')
        
        # Vérifier qu'il n'y a pas de spam
        spam_indicators = ['$$$', '!!!', '???', 'URGENT', 'GRATUIT', 'FREE']
        if any(indicator in value.upper() for indicator in spam_indicators):
            raise ValidationError('La description contient des indicateurs de spam')
