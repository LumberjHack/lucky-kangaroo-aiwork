"""
Modèles pour les paiements de Lucky Kangaroo
Gestion des transactions et méthodes de paiement
"""

import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Float, JSON, ForeignKey, Index, CheckConstraint
from sqlalchemy import String
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

from app import db


class PaymentStatus(Enum):
    """Statut du paiement"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentType(Enum):
    """Type de paiement"""
    LISTING_FEE = "listing_fee"
    BOOST = "boost"
    KYC_VERIFICATION = "kyc_verification"
    EXCHANGE_INSURANCE = "exchange_insurance"
    ESCROW_FEE = "escrow_fee"
    SUBSCRIPTION = "subscription"


class PaymentMethodType(Enum):
    """Type de méthode de paiement"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    TWINT = "twint"
    POSTFINANCE = "postfinance"


class Payment(db.Model):
    """
    Modèle pour les paiements
    """
    __tablename__ = 'payments'
    
    # Identifiants
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    payment_method_id = Column(String(36), ForeignKey('payment_methods.id'), nullable=True, index=True)
    
    # Informations du paiement
    payment_type = Column(String(30), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default='CHF', nullable=False)
    description = Column(Text, nullable=True)
    
    # Statut et traitement
    status = Column(String(20), default=PaymentStatus.PENDING.value, nullable=False, index=True)
    external_payment_id = Column(String(100), nullable=True, index=True)  # ID du processeur externe
    external_transaction_id = Column(String(100), nullable=True, index=True)
    
    # Métadonnées
    payment_metadata = Column(JSON, default=dict, nullable=False)
    failure_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    processed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relations
    user = relationship("User", back_populates="payments")
    payment_method = relationship("PaymentMethod", back_populates="payments")
    
    # Indexes
    __table_args__ = (
        Index('idx_payment_user', 'user_id'),
        Index('idx_payment_type', 'payment_type'),
        Index('idx_payment_status', 'status'),
        Index('idx_payment_external', 'external_payment_id'),
        Index('idx_payment_created', 'created_at'),
        CheckConstraint('amount > 0', name='check_amount_positive'),
    )
    
    def __init__(self, **kwargs):
        super(Payment, self).__init__(**kwargs)
        if not self.payment_metadata:
            self.payment_metadata = {}
    
    @property
    def is_successful(self):
        """Vérifier si le paiement est réussi"""
        return self.status == PaymentStatus.COMPLETED.value
    
    @property
    def is_pending(self):
        """Vérifier si le paiement est en attente"""
        return self.status in [PaymentStatus.PENDING.value, PaymentStatus.PROCESSING.value]
    
    @property
    def is_failed(self):
        """Vérifier si le paiement a échoué"""
        return self.status in [PaymentStatus.FAILED.value, PaymentStatus.CANCELLED.value]
    
    def process(self):
        """Marquer comme en cours de traitement"""
        if self.status == PaymentStatus.PENDING.value:
            self.status = PaymentStatus.PROCESSING.value
            self.processed_at = datetime.utcnow()
            db.session.commit()
    
    def complete(self, external_transaction_id=None):
        """Marquer comme terminé"""
        if self.status == PaymentStatus.PROCESSING.value:
            self.status = PaymentStatus.COMPLETED.value
            self.completed_at = datetime.utcnow()
            if external_transaction_id:
                self.external_transaction_id = external_transaction_id
            db.session.commit()
    
    def fail(self, reason=None):
        """Marquer comme échoué"""
        if self.status in [PaymentStatus.PENDING.value, PaymentStatus.PROCESSING.value]:
            self.status = PaymentStatus.FAILED.value
            if reason:
                self.failure_reason = reason
            db.session.commit()
    
    def cancel(self, reason=None):
        """Annuler le paiement"""
        if self.status in [PaymentStatus.PENDING.value, PaymentStatus.PROCESSING.value]:
            self.status = PaymentStatus.CANCELLED.value
            if reason:
                self.failure_reason = reason
            db.session.commit()
    
    def refund(self, amount=None, reason=None):
        """Rembourser le paiement"""
        if self.status == PaymentStatus.COMPLETED.value:
            if amount and amount < self.amount:
                self.status = PaymentStatus.PARTIALLY_REFUNDED.value
            else:
                self.status = PaymentStatus.REFUNDED.value
            
            if reason:
                self.payment_metadata['refund_reason'] = reason
            
            db.session.commit()
    
    def to_dict(self, include_private=False):
        """Convertir le paiement en dictionnaire"""
        data = {
            'id': str(self.id),
            'payment_type': self.payment_type,
            'amount': self.amount,
            'currency': self.currency,
            'description': self.description,
            'status': self.status,
            'is_successful': self.is_successful,
            'is_pending': self.is_pending,
            'is_failed': self.is_failed,
            'created_at': self.created_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
        
        if include_private:
            data.update({
                'external_payment_id': self.external_payment_id,
                'external_transaction_id': self.external_transaction_id,
                'failure_reason': self.failure_reason,
                'metadata': self.payment_metadata,
                'updated_at': self.updated_at.isoformat()
            })
        
        return data
    
    @validates('amount')
    def validate_amount(self, key, amount):
        """Valider le montant"""
        if amount <= 0:
            raise ValueError('Amount must be positive')
        return amount
    
    def __repr__(self):
        return f'<Payment {self.amount} {self.currency} - {self.status}>'


class PaymentMethod(db.Model):
    """
    Modèle pour les méthodes de paiement
    """
    __tablename__ = 'payment_methods'
    
    # Identifiants
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    
    # Informations de la méthode
    method_type = Column(String(20), nullable=False, index=True)
    name = Column(String(100), nullable=False)  # Nom affiché par l'utilisateur
    is_default = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Informations sécurisées (chiffrées)
    encrypted_data = Column(Text, nullable=True)  # Données chiffrées du processeur
    last_four_digits = Column(String(4), nullable=True)  # 4 derniers chiffres
    expiry_month = Column(Integer, nullable=True)
    expiry_year = Column(Integer, nullable=True)
    
    # Métadonnées
    payment_metadata = Column(JSON, default=dict, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relations
    user = relationship("User")
    payments = relationship("Payment", back_populates="payment_method")
    
    # Indexes
    __table_args__ = (
        Index('idx_payment_method_user', 'user_id'),
        Index('idx_payment_method_type', 'method_type'),
        Index('idx_payment_method_active', 'is_active'),
        CheckConstraint('expiry_month >= 1 AND expiry_month <= 12', name='check_expiry_month_range'),
        CheckConstraint('expiry_year >= 2020', name='check_expiry_year_range'),
    )
    
    def __init__(self, **kwargs):
        super(PaymentMethod, self).__init__(**kwargs)
        if not self.payment_metadata:
            self.payment_metadata = {}
    
    @property
    def is_expired(self):
        """Vérifier si la méthode de paiement est expirée"""
        if not self.expiry_month or not self.expiry_year:
            return False
        
        current_date = datetime.utcnow()
        expiry_date = datetime(self.expiry_year, self.expiry_month, 1)
        return expiry_date < current_date
    
    @property
    def display_name(self):
        """Nom d'affichage de la méthode de paiement"""
        if self.last_four_digits:
            return f"{self.name} ****{self.last_four_digits}"
        return self.name
    
    def set_as_default(self):
        """Définir comme méthode par défaut"""
        # Désactiver les autres méthodes par défaut pour cet utilisateur
        PaymentMethod.query.filter_by(user_id=self.user_id, is_default=True).update({'is_default': False})
        
        # Définir cette méthode comme par défaut
        self.is_default = True
        db.session.commit()
    
    def deactivate(self):
        """Désactiver la méthode de paiement"""
        self.is_active = False
        if self.is_default:
            self.is_default = False
        db.session.commit()
    
    def update_last_used(self):
        """Mettre à jour la dernière utilisation"""
        self.last_used_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self, include_private=False):
        """Convertir la méthode de paiement en dictionnaire"""
        data = {
            'id': str(self.id),
            'method_type': self.method_type,
            'name': self.name,
            'display_name': self.display_name,
            'is_default': self.is_default,
            'is_active': self.is_active,
            'is_expired': self.is_expired,
            'created_at': self.created_at.isoformat(),
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None
        }
        
        if include_private:
            data.update({
                'expiry_month': self.expiry_month,
                'expiry_year': self.expiry_year,
                'metadata': self.payment_metadata,
                'updated_at': self.updated_at.isoformat()
            })
        
        return data
    
    @validates('expiry_month')
    def validate_expiry_month(self, key, month):
        """Valider le mois d'expiration"""
        if month is not None and not (1 <= month <= 12):
            raise ValueError('Expiry month must be between 1 and 12')
        return month
    
    @validates('expiry_year')
    def validate_expiry_year(self, key, year):
        """Valider l'année d'expiration"""
        if year is not None and year < 2020:
            raise ValueError('Expiry year must be 2020 or later')
        return year
    
    def __repr__(self):
        return f'<PaymentMethod {self.display_name}>'
