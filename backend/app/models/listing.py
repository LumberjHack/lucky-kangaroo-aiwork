"""
Modèles pour les annonces (listings) de Lucky Kangaroo
Gestion des objets et services à échanger
"""

import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Float, JSON, ForeignKey, Index, CheckConstraint
from sqlalchemy import String
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from sqlalchemy import event

from app import db


class ListingStatus(Enum):
    """Statut de l'annonce"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    SOLD = "sold"
    EXPIRED = "expired"
    DELETED = "deleted"
    MODERATION = "moderation"


class ListingType(Enum):
    """Type d'annonce"""
    GOOD = "good"  # Objet
    SERVICE = "service"  # Service


class ExchangeType(Enum):
    """Type d'échange accepté"""
    DIRECT = "direct"  # Échange direct
    CHAIN = "chain"  # Chaîne d'échange
    BOTH = "both"  # Les deux


class Condition(Enum):
    """État de l'objet"""
    EXCELLENT = "excellent"
    VERY_GOOD = "very_good"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    NEW = "new"


class ListingCategory(db.Model):
    """Catégories d'annonces"""
    __tablename__ = 'listing_categories'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)
    parent_id = Column(String(36), ForeignKey('listing_categories.id'), nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relations
    parent = relationship("ListingCategory", remote_side=[id], backref="children")
    listings = relationship("Listing", back_populates="category")
    
    def __repr__(self):
        return f'<ListingCategory {self.name}>'


class Listing(db.Model):
    """
    Modèle principal pour les annonces
    """
    __tablename__ = 'listings'
    
    # Identifiants
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    category_id = Column(String(36), ForeignKey('listing_categories.id'), nullable=False, index=True)
    
    # Informations de base
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    listing_type = Column(String(20), default=ListingType.GOOD.value, nullable=False)
    condition = Column(String(20), nullable=True)  # Pour les objets uniquement
    brand = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    year = Column(Integer, nullable=True)
    
    # Prix et valeur
    estimated_value = Column(Float, nullable=True)  # Valeur estimée en CHF
    price_range_min = Column(Float, nullable=True)
    price_range_max = Column(Float, nullable=True)
    currency = Column(String(3), default='CHF', nullable=False)
    
    # Localisation
    location_name = Column(String(200), nullable=True)
    latitude = Column(Float, nullable=True, index=True)
    longitude = Column(Float, nullable=True, index=True)
    city = Column(String(100), nullable=True, index=True)
    postal_code = Column(String(20), nullable=True, index=True)
    country = Column(String(100), default='Switzerland', nullable=False)
    
    # Échange
    exchange_type = Column(String(20), default=ExchangeType.BOTH.value, nullable=False)
    desired_items = Column(Text, nullable=True)  # Types d'objets/services souhaités
    excluded_items = Column(Text, nullable=True)  # Types d'objets/services exclus
    
    # Statut et visibilité
    status = Column(String(20), default=ListingStatus.DRAFT.value, nullable=False, index=True)
    is_featured = Column(Boolean, default=False, nullable=False)
    is_boosted = Column(Boolean, default=False, nullable=False)
    boost_expires_at = Column(DateTime, nullable=True)
    views_count = Column(Integer, default=0, nullable=False)
    likes_count = Column(Integer, default=0, nullable=False)
    shares_count = Column(Integer, default=0, nullable=False)
    
    # Dates importantes
    published_at = Column(DateTime, nullable=True, index=True)
    expires_at = Column(DateTime, nullable=True, index=True)
    sold_at = Column(DateTime, nullable=True)
    
    # Métadonnées
    tags = Column(Text, nullable=True)
    listing_metadata = Column(JSON, default=dict, nullable=False)
    ai_analysis = Column(JSON, nullable=True)  # Résultats de l'analyse IA
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Recherche full-text
    search_vector = Column(Text, nullable=True)
    
    # Relations
    user = relationship("User", back_populates="listings")
    category = relationship("ListingCategory", back_populates="listings")
    images = relationship("ListingImage", back_populates="listing", cascade="all, delete-orphan")
    exchanges = relationship("Exchange", back_populates="listing")
    reviews = relationship("Review", back_populates="listing")
    
    # Indexes
    __table_args__ = (
        Index('idx_listing_user_status', 'user_id', 'status'),
        Index('idx_listing_category_status', 'category_id', 'status'),
        Index('idx_listing_location', 'latitude', 'longitude'),
        Index('idx_listing_published', 'published_at'),
        Index('idx_listing_expires', 'expires_at'),
        Index('idx_listing_featured', 'is_featured', 'published_at'),
        Index('idx_listing_boosted', 'is_boosted', 'boost_expires_at'),
        Index('idx_listing_search', 'search_vector'),
        CheckConstraint('estimated_value >= 0', name='check_estimated_value_positive'),
        CheckConstraint('price_range_min >= 0', name='check_price_range_min_positive'),
        CheckConstraint('price_range_max >= 0', name='check_price_range_max_positive'),
        CheckConstraint('price_range_min <= price_range_max', name='check_price_range_valid'),
    )
    
    def __init__(self, **kwargs):
        super(Listing, self).__init__(**kwargs)
        if not self.listing_metadata:
            self.listing_metadata = {}
        # Définir la date d'expiration par défaut (14 jours)
        if not self.expires_at and self.status == ListingStatus.ACTIVE.value:
            self.expires_at = datetime.utcnow() + timedelta(days=14)
    
    @property
    def is_active(self):
        """Vérifier si l'annonce est active"""
        return (
            self.status == ListingStatus.ACTIVE.value and
            (not self.expires_at or self.expires_at > datetime.utcnow())
        )
    
    @property
    def is_expired(self):
        """Vérifier si l'annonce est expirée"""
        return self.expires_at and self.expires_at <= datetime.utcnow()
    
    @property
    def is_boosted_active(self):
        """Vérifier si le boost est actif"""
        return self.is_boosted and self.boost_expires_at and self.boost_expires_at > datetime.utcnow()
    
    @property
    def days_until_expiry(self):
        """Nombre de jours jusqu'à l'expiration"""
        if not self.expires_at:
            return None
        delta = self.expires_at - datetime.utcnow()
        return delta.days if delta.days > 0 else 0
    
    @property
    def main_image(self):
        """Image principale de l'annonce"""
        main_img = next((img for img in self.images if img.is_main), None)
        return main_img or (self.images[0] if self.images else None)
    
    @property
    def price_display(self):
        """Affichage du prix"""
        if self.estimated_value:
            return f"{self.estimated_value:.0f} {self.currency}"
        elif self.price_range_min and self.price_range_max:
            return f"{self.price_range_min:.0f} - {self.price_range_max:.0f} {self.currency}"
        elif self.price_range_min:
            return f"À partir de {self.price_range_min:.0f} {self.currency}"
        else:
            return "Prix à négocier"
    
    def publish(self):
        """Publier l'annonce"""
        if self.status == ListingStatus.DRAFT.value:
            self.status = ListingStatus.ACTIVE.value
            self.published_at = datetime.utcnow()
            if not self.expires_at:
                self.expires_at = datetime.utcnow() + timedelta(days=14)
            db.session.commit()
    
    def pause(self):
        """Mettre en pause l'annonce"""
        if self.status == ListingStatus.ACTIVE.value:
            self.status = ListingStatus.PAUSED.value
            db.session.commit()
    
    def resume(self):
        """Reprendre l'annonce"""
        if self.status == ListingStatus.PAUSED.value:
            self.status = ListingStatus.ACTIVE.value
            db.session.commit()
    
    def mark_as_sold(self):
        """Marquer comme vendu"""
        if self.status == ListingStatus.ACTIVE.value:
            self.status = ListingStatus.SOLD.value
            self.sold_at = datetime.utcnow()
            db.session.commit()
    
    def extend_expiry(self, days=14):
        """Prolonger l'expiration"""
        if self.expires_at:
            self.expires_at += timedelta(days=days)
        else:
            self.expires_at = datetime.utcnow() + timedelta(days=days)
        db.session.commit()
    
    def boost(self, days=7):
        """Booster l'annonce"""
        self.is_boosted = True
        if self.boost_expires_at and self.boost_expires_at > datetime.utcnow():
            self.boost_expires_at += timedelta(days=days)
        else:
            self.boost_expires_at = datetime.utcnow() + timedelta(days=days)
        db.session.commit()
    
    def increment_views(self):
        """Incrémenter le compteur de vues"""
        self.views_count += 1
        db.session.commit()
    
    def increment_likes(self):
        """Incrémenter le compteur de likes"""
        self.likes_count += 1
        db.session.commit()
    
    def increment_shares(self):
        """Incrémenter le compteur de partages"""
        self.shares_count += 1
        db.session.commit()
    
    def update_search_vector(self):
        """Mettre à jour le vecteur de recherche full-text"""
        search_text = f"{self.title} {self.description} {self.brand or ''} {self.model or ''} {' '.join(self.tags or [])}"
        self.search_vector = func.to_tsvector('french', search_text)
        db.session.flush()
    
    def to_dict(self, include_private=False):
        """Convertir l'annonce en dictionnaire"""
        data = {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'listing_type': self.listing_type,
            'condition': self.condition,
            'brand': self.brand,
            'model': self.model,
            'year': self.year,
            'estimated_value': self.estimated_value,
            'price_display': self.price_display,
            'location': {
                'name': self.location_name,
                'city': self.city,
                'postal_code': self.postal_code,
                'country': self.country
            },
            'exchange_type': self.exchange_type,
            'desired_items': self.desired_items,
            'excluded_items': self.excluded_items,
            'status': self.status,
            'is_featured': self.is_featured,
            'is_boosted': self.is_boosted_active,
            'views_count': self.views_count,
            'likes_count': self.likes_count,
            'shares_count': self.shares_count,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'days_until_expiry': self.days_until_expiry,
            'images': [img.to_dict() for img in self.images],
            'main_image': self.main_image.to_dict() if self.main_image else None,
            'user': {
                'id': str(self.user.id),
                'username': self.user.username,
                'display_name': self.user.display_name,
                'trust_score': self.user.trust_score,
                'profile_picture': self.user.profile_picture
            },
            'category': {
                'id': str(self.category.id),
                'name': self.category.name,
                'slug': self.category.slug
            }
        }
        
        if include_private:
            data.update({
                'metadata': self.listing_metadata,
                'ai_analysis': self.ai_analysis,
                'updated_at': self.updated_at.isoformat(),
                'sold_at': self.sold_at.isoformat() if self.sold_at else None
            })
        
        return data
    
    @validates('estimated_value', 'price_range_min', 'price_range_max')
    def validate_price(self, key, value):
        """Valider les prix"""
        if value is not None and value < 0:
            raise ValueError('Price must be positive')
        return value
    
    @validates('year')
    def validate_year(self, key, year):
        """Valider l'année"""
        if year is not None and (year < 1900 or year > datetime.utcnow().year + 1):
            raise ValueError('Invalid year')
        return year
    
    def __repr__(self):
        return f'<Listing {self.title}>'


class ListingImage(db.Model):
    """Images des annonces"""
    __tablename__ = 'listing_images'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    listing_id = Column(String(36), ForeignKey('listings.id'), nullable=False, index=True)
    
    # Informations de l'image
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    
    # Métadonnées
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    alt_text = Column(String(255), nullable=True)
    is_main = Column(Boolean, default=False, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    
    # IA et analyse
    ai_tags = Column(Text, nullable=True)
    ai_confidence = Column(Float, nullable=True)
    object_detection = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relations
    listing = relationship("Listing", back_populates="images")
    
    # Indexes
    __table_args__ = (
        Index('idx_listing_image_listing', 'listing_id'),
        Index('idx_listing_image_main', 'listing_id', 'is_main'),
        Index('idx_listing_image_order', 'listing_id', 'sort_order'),
    )
    
    def to_dict(self):
        """Convertir l'image en dictionnaire"""
        return {
            'id': str(self.id),
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'width': self.width,
            'height': self.height,
            'alt_text': self.alt_text,
            'is_main': self.is_main,
            'sort_order': self.sort_order,
            'ai_tags': self.ai_tags,
            'ai_confidence': self.ai_confidence,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<ListingImage {self.filename}>'


# Événements pour mettre à jour automatiquement le vecteur de recherche
# Temporairement désactivé pour éviter les conflits de session
# @event.listens_for(Listing, 'after_insert')
# @event.listens_for(Listing, 'after_update')
# def update_listing_search_vector(mapper, connection, target):
#     """Mettre à jour le vecteur de recherche après insertion/mise à jour"""
#     if target.status == 'active':
#         target.update_search_vector()
