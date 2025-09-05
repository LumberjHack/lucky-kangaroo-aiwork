"""
Modèles pour la géolocalisation de Lucky Kangaroo
Gestion des lieux et points de rencontre
"""

import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Float, JSON, ForeignKey, Index, CheckConstraint
from sqlalchemy import String
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

from app import db


class LocationType(Enum):
    """Type de lieu"""
    USER_HOME = "user_home"
    PUBLIC_PLACE = "public_place"
    MEETING_POINT = "meeting_point"
    BUSINESS = "business"
    CUSTOM = "custom"


class Location(db.Model):
    """
    Modèle pour les lieux
    """
    __tablename__ = 'locations'
    
    # Identifiants
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=True, index=True)
    
    # Informations du lieu
    name = Column(String(200), nullable=False)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True, index=True)
    postal_code = Column(String(20), nullable=True, index=True)
    country = Column(String(100), default='Switzerland', nullable=False)
    
    # Coordonnées géographiques
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    
    # Type et métadonnées
    location_type = Column(String(20), default=LocationType.CUSTOM.value, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Informations supplémentaires
    description = Column(Text, nullable=True)
    opening_hours = Column(JSON, nullable=True)
    contact_info = Column(JSON, nullable=True)
    amenities = Column(JSON, nullable=True)
    
    # Métadonnées
    location_metadata = Column(JSON, default=dict, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relations
    user = relationship("User")
    meeting_points = relationship("MeetingPoint", back_populates="location")
    
    # Indexes
    __table_args__ = (
        Index('idx_location_user', 'user_id'),
        Index('idx_location_coordinates', 'latitude', 'longitude'),
        Index('idx_location_city', 'city'),
        Index('idx_location_type', 'location_type'),
        Index('idx_location_public', 'is_public'),
        CheckConstraint('latitude >= -90 AND latitude <= 90', name='check_latitude_range'),
        CheckConstraint('longitude >= -180 AND longitude <= 180', name='check_longitude_range'),
    )
    
    def __init__(self, **kwargs):
        super(Location, self).__init__(**kwargs)
        if not self.location_metadata:
            self.location_metadata = {}
        if not self.amenities:
            self.amenities = []
        if not self.contact_info:
            self.contact_info = {}
        if not self.opening_hours:
            self.opening_hours = {}
    
    @property
    def full_address(self):
        """Adresse complète"""
        parts = []
        if self.address:
            parts.append(self.address)
        if self.postal_code:
            parts.append(self.postal_code)
        if self.city:
            parts.append(self.city)
        if self.country and self.country != 'Switzerland':
            parts.append(self.country)
        return ', '.join(parts) if parts else 'Adresse non spécifiée'
    
    def distance_to(self, other_latitude, other_longitude):
        """Calculer la distance vers un autre point (en km)"""
        from math import radians, cos, sin, asin, sqrt
        
        # Formule de Haversine
        lat1, lon1 = radians(self.latitude), radians(self.longitude)
        lat2, lon2 = radians(other_latitude), radians(other_longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Rayon de la Terre en km
        r = 6371
        return c * r
    
    def verify(self):
        """Vérifier le lieu"""
        self.is_verified = True
        db.session.commit()
    
    def make_public(self):
        """Rendre le lieu public"""
        self.is_public = True
        db.session.commit()
    
    def make_private(self):
        """Rendre le lieu privé"""
        self.is_public = False
        db.session.commit()
    
    def to_dict(self, include_private=False):
        """Convertir le lieu en dictionnaire"""
        data = {
            'id': str(self.id),
            'name': self.name,
            'address': self.address,
            'full_address': self.full_address,
            'city': self.city,
            'postal_code': self.postal_code,
            'country': self.country,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'location_type': self.location_type,
            'is_public': self.is_public,
            'is_verified': self.is_verified,
            'description': self.description,
            'amenities': self.amenities,
            'created_at': self.created_at.isoformat()
        }
        
        if include_private:
            data.update({
                'opening_hours': self.opening_hours,
                'contact_info': self.contact_info,
                'metadata': self.location_metadata,
                'updated_at': self.updated_at.isoformat()
            })
        
        return data
    
    @validates('latitude')
    def validate_latitude(self, key, latitude):
        """Valider la latitude"""
        if not (-90 <= latitude <= 90):
            raise ValueError('Latitude must be between -90 and 90')
        return latitude
    
    @validates('longitude')
    def validate_longitude(self, key, longitude):
        """Valider la longitude"""
        if not (-180 <= longitude <= 180):
            raise ValueError('Longitude must be between -180 and 180')
        return longitude
    
    def __repr__(self):
        return f'<Location {self.name}>'


class MeetingPoint(db.Model):
    """
    Modèle pour les points de rencontre
    """
    __tablename__ = 'meeting_points'
    
    # Identifiants
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    location_id = Column(String(36), ForeignKey('locations.id'), nullable=False, index=True)
    
    # Informations du point de rencontre
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    
    # Statut
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Métadonnées
    location_metadata = Column(JSON, default=dict, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relations
    location = relationship("Location", back_populates="meeting_points")
    
    # Indexes
    __table_args__ = (
        Index('idx_meeting_point_location', 'location_id'),
        Index('idx_meeting_point_active', 'is_active'),
    )
    
    def __init__(self, **kwargs):
        super(MeetingPoint, self).__init__(**kwargs)
        if not self.location_metadata:
            self.location_metadata = {}
    
    @property
    def full_address(self):
        """Adresse complète du point de rencontre"""
        return self.location.full_address
    
    @property
    def coordinates(self):
        """Coordonnées du point de rencontre"""
        return {
            'latitude': self.location.latitude,
            'longitude': self.location.longitude
        }
    
    def verify(self):
        """Vérifier le point de rencontre"""
        self.is_verified = True
        db.session.commit()
    
    def activate(self):
        """Activer le point de rencontre"""
        self.is_active = True
        db.session.commit()
    
    def deactivate(self):
        """Désactiver le point de rencontre"""
        self.is_active = False
        db.session.commit()
    
    def to_dict(self):
        """Convertir le point de rencontre en dictionnaire"""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'instructions': self.instructions,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'location': self.location.to_dict()
        }
    
    def __repr__(self):
        return f'<MeetingPoint {self.name}>'
