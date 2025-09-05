"""
Modèles pour l'analyse IA de Lucky Kangaroo
Gestion des analyses d'objets, de valeur et de contenu
"""

import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Float, JSON, ForeignKey, Index, CheckConstraint
from sqlalchemy import String
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

from app import db


class AnalysisType(Enum):
    """Type d'analyse IA"""
    OBJECT_DETECTION = "object_detection"
    VALUE_ESTIMATION = "value_estimation"
    CONTENT_MODERATION = "content_moderation"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    CATEGORY_CLASSIFICATION = "category_classification"
    BRAND_DETECTION = "brand_detection"
    CONDITION_ANALYSIS = "condition_analysis"


class AnalysisStatus(Enum):
    """Statut de l'analyse"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AIAnalysis(db.Model):
    """
    Modèle principal pour les analyses IA
    """
    __tablename__ = 'ai_analyses'
    
    # Identifiants
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    listing_id = Column(String(36), ForeignKey('listings.id'), nullable=True, index=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=True, index=True)
    
    # Type et statut
    analysis_type = Column(String(30), nullable=False, index=True)
    status = Column(String(20), default=AnalysisStatus.PENDING.value, nullable=False, index=True)
    
    # Données d'entrée
    input_data = Column(JSON, nullable=False)
    input_files = Column(Text, nullable=True)  # URLs des fichiers
    
    # Résultats
    results = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)  # 0-1
    processing_time = Column(Float, nullable=True)  # en secondes
    
    # Métadonnées
    model_version = Column(String(50), nullable=True)
    ai_metadata = Column(JSON, default=dict, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relations
    listing = relationship("Listing")
    user = relationship("User")
    object_detections = relationship("ObjectDetection", back_populates="analysis", cascade="all, delete-orphan")
    value_estimations = relationship("ValueEstimation", back_populates="analysis", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_ai_analysis_listing', 'listing_id'),
        Index('idx_ai_analysis_user', 'user_id'),
        Index('idx_ai_analysis_type', 'analysis_type'),
        Index('idx_ai_analysis_status', 'status'),
        Index('idx_ai_analysis_created', 'created_at'),
        CheckConstraint('confidence_score >= 0 AND confidence_score <= 1', name='check_confidence_score_range'),
        CheckConstraint('processing_time >= 0', name='check_processing_time_positive'),
    )
    
    def __init__(self, **kwargs):
        super(AIAnalysis, self).__init__(**kwargs)
        if not self.input_data:
            self.input_data = {}
        if not self.ai_metadata:
            self.ai_metadata = {}
    
    @property
    def is_completed(self):
        """Vérifier si l'analyse est terminée"""
        return self.status == AnalysisStatus.COMPLETED.value
    
    @property
    def is_failed(self):
        """Vérifier si l'analyse a échoué"""
        return self.status == AnalysisStatus.FAILED.value
    
    @property
    def is_processing(self):
        """Vérifier si l'analyse est en cours"""
        return self.status == AnalysisStatus.PROCESSING.value
    
    def start_processing(self):
        """Démarrer le traitement"""
        if self.status == AnalysisStatus.PENDING.value:
            self.status = AnalysisStatus.PROCESSING.value
            self.started_at = datetime.utcnow()
            db.session.commit()
    
    def complete(self, results, confidence_score=None, processing_time=None):
        """Marquer comme terminé"""
        if self.status == AnalysisStatus.PROCESSING.value:
            self.status = AnalysisStatus.COMPLETED.value
            self.results = results
            self.confidence_score = confidence_score
            self.processing_time = processing_time
            self.completed_at = datetime.utcnow()
            db.session.commit()
    
    def fail(self, error_message):
        """Marquer comme échoué"""
        if self.status in [AnalysisStatus.PENDING.value, AnalysisStatus.PROCESSING.value]:
            self.status = AnalysisStatus.FAILED.value
            self.error_message = error_message
            self.completed_at = datetime.utcnow()
            db.session.commit()
    
    def cancel(self):
        """Annuler l'analyse"""
        if self.status in [AnalysisStatus.PENDING.value, AnalysisStatus.PROCESSING.value]:
            self.status = AnalysisStatus.CANCELLED.value
            self.completed_at = datetime.utcnow()
            db.session.commit()
    
    def to_dict(self, include_private=False):
        """Convertir l'analyse en dictionnaire"""
        data = {
            'id': str(self.id),
            'analysis_type': self.analysis_type,
            'status': self.status,
            'is_completed': self.is_completed,
            'is_failed': self.is_failed,
            'is_processing': self.is_processing,
            'confidence_score': self.confidence_score,
            'processing_time': self.processing_time,
            'model_version': self.model_version,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
        
        if include_private:
            data.update({
                'input_data': self.input_data,
                'input_files': self.input_files,
                'results': self.results,
                'error_message': self.error_message,
                'metadata': self.ai_metadata,
                'updated_at': self.updated_at.isoformat()
            })
        
        return data
    
    @validates('confidence_score')
    def validate_confidence_score(self, key, score):
        """Valider le score de confiance"""
        if score is not None and not (0 <= score <= 1):
            raise ValueError('Confidence score must be between 0 and 1')
        return score
    
    @validates('processing_time')
    def validate_processing_time(self, key, time):
        """Valider le temps de traitement"""
        if time is not None and time < 0:
            raise ValueError('Processing time must be positive')
        return time
    
    def __repr__(self):
        return f'<AIAnalysis {self.analysis_type} - {self.status}>'


class ObjectDetection(db.Model):
    """
    Modèle pour la détection d'objets
    """
    __tablename__ = 'object_detections'
    
    # Identifiants
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey('ai_analyses.id'), nullable=False, index=True)
    
    # Objet détecté
    object_name = Column(String(100), nullable=False, index=True)
    object_category = Column(String(50), nullable=True, index=True)
    confidence = Column(Float, nullable=False)  # 0-1
    
    # Position dans l'image
    bounding_box = Column(JSON, nullable=True)  # {x, y, width, height}
    
    # Métadonnées
    ai_metadata = Column(JSON, default=dict, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relations
    analysis = relationship("AIAnalysis", back_populates="object_detections")
    
    # Indexes
    __table_args__ = (
        Index('idx_object_detection_analysis', 'analysis_id'),
        Index('idx_object_detection_name', 'object_name'),
        Index('idx_object_detection_category', 'object_category'),
        Index('idx_object_detection_confidence', 'confidence'),
        CheckConstraint('confidence >= 0 AND confidence <= 1', name='check_object_confidence_range'),
    )
    
    def __init__(self, **kwargs):
        super(ObjectDetection, self).__init__(**kwargs)
        if not self.ai_metadata:
            self.ai_metadata = {}
    
    def to_dict(self):
        """Convertir la détection en dictionnaire"""
        return {
            'id': str(self.id),
            'object_name': self.object_name,
            'object_category': self.object_category,
            'confidence': self.confidence,
            'bounding_box': self.bounding_box,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }
    
    @validates('confidence')
    def validate_confidence(self, key, confidence):
        """Valider la confiance"""
        if not (0 <= confidence <= 1):
            raise ValueError('Confidence must be between 0 and 1')
        return confidence
    
    def __repr__(self):
        return f'<ObjectDetection {self.object_name} ({self.confidence:.2f})>'


class ValueEstimation(db.Model):
    """
    Modèle pour l'estimation de valeur
    """
    __tablename__ = 'value_estimations'
    
    # Identifiants
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey('ai_analyses.id'), nullable=False, index=True)
    
    # Estimation
    estimated_value = Column(Float, nullable=False)
    currency = Column(String(3), default='CHF', nullable=False)
    confidence = Column(Float, nullable=False)  # 0-1
    
    # Fourchette de prix
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    
    # Facteurs d'estimation
    condition_factor = Column(Float, nullable=True)
    brand_factor = Column(Float, nullable=True)
    rarity_factor = Column(Float, nullable=True)
    market_demand_factor = Column(Float, nullable=True)
    
    # Métadonnées
    ai_metadata = Column(JSON, default=dict, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relations
    analysis = relationship("AIAnalysis", back_populates="value_estimations")
    
    # Indexes
    __table_args__ = (
        Index('idx_value_estimation_analysis', 'analysis_id'),
        Index('idx_value_estimation_value', 'estimated_value'),
        Index('idx_value_estimation_confidence', 'confidence'),
        CheckConstraint('estimated_value >= 0', name='check_estimated_value_positive'),
        CheckConstraint('confidence >= 0 AND confidence <= 1', name='check_value_confidence_range'),
        CheckConstraint('min_value >= 0', name='check_min_value_positive'),
        CheckConstraint('max_value >= 0', name='check_max_value_positive'),
        CheckConstraint('min_value <= max_value', name='check_value_range_valid'),
    )
    
    def __init__(self, **kwargs):
        super(ValueEstimation, self).__init__(**kwargs)
        if not self.ai_metadata:
            self.ai_metadata = {}
    
    @property
    def value_range(self):
        """Fourchette de prix"""
        if self.min_value and self.max_value:
            return f"{self.min_value:.0f} - {self.max_value:.0f} {self.currency}"
        return f"{self.estimated_value:.0f} {self.currency}"
    
    def to_dict(self):
        """Convertir l'estimation en dictionnaire"""
        return {
            'id': str(self.id),
            'estimated_value': self.estimated_value,
            'currency': self.currency,
            'confidence': self.confidence,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'value_range': self.value_range,
            'condition_factor': self.condition_factor,
            'brand_factor': self.brand_factor,
            'rarity_factor': self.rarity_factor,
            'market_demand_factor': self.market_demand_factor,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }
    
    @validates('estimated_value', 'min_value', 'max_value')
    def validate_value(self, key, value):
        """Valider les valeurs"""
        if value is not None and value < 0:
            raise ValueError('Value must be positive')
        return value
    
    @validates('confidence')
    def validate_confidence(self, key, confidence):
        """Valider la confiance"""
        if not (0 <= confidence <= 1):
            raise ValueError('Confidence must be between 0 and 1')
        return confidence
    
    def __repr__(self):
        return f'<ValueEstimation {self.estimated_value} {self.currency} ({self.confidence:.2f})>'
