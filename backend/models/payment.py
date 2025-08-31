from backend.extensions import db
"""Payment and subscription models for Lucky Kangaroo."""
from datetime import datetime, timedelta
from enum import Enum
from ...extensions import db


class PaymentStatus(Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    CANCELED = 'canceled'


class SubscriptionStatus(Enum):
    ACTIVE = 'active'
    CANCELED = 'canceled'
    PAST_DUE = 'past_due'
    UNPAID = 'unpaid'
    TRIALING = 'trialing'
    INCOMPLETE = 'incomplete'
    INCOMPLETE_EXPIRED = 'incomplete_expired'


class PaymentMethodType(Enum):
    CARD = 'card'
    PAYPAL = 'paypal'
    BANK_ACCOUNT = 'bank_account'
    APPLE_PAY = 'apple_pay'
    GOOGLE_PAY = 'google_pay'
    OTHER = 'other'


class Payment(db.Model):
    """Payment transactions."""
    __tablename__ = 'payments'
    
    id = db.Column(db.String(50), primary_key=True)  # External payment ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='CHF')
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING)
    description = db.Column(db.Text)
    metadata = db.Column(db.JSON)  # Additional payment data
    
    # Payment method details
    payment_method_id = db.Column(db.String(50))
    payment_method_type = db.Column(db.Enum(PaymentMethodType))
    payment_method_last4 = db.Column(db.String(4))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    paid_at = db.Column(db.DateTime)
    
    # Relationships
    subscription = db.relationship('Subscription', back_populates='payments', uselist=False)
    
    def __repr__(self):
        return f'<Payment {self.id} {self.amount} {self.currency} {self.status.value}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'amount': float(self.amount) if self.amount else None,
            'currency': self.currency,
            'status': self.status.value,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'payment_method': {
                'type': self.payment_method_type.value if self.payment_method_type else None,
                'last4': self.payment_method_last4
            } if self.payment_method_type else None
        }


class SubscriptionPlan(db.Model):
    """Subscription plans."""
    __tablename__ = 'subscription_plans'
    
    id = db.Column(db.String(50), primary_key=True)  # External plan ID
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='CHF')
    billing_interval = db.Column(db.String(20), default='month')  # month, year, week, etc.
    trial_period_days = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    metadata = db.Column(db.JSON)  # Additional plan data
    
    # Features included in this plan
    features = db.Column(db.JSON)  # List of feature names
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SubscriptionPlan {self.name} {self.price} {self.currency}/{self.billing_interval}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price) if self.price else None,
            'currency': self.currency,
            'billing_interval': self.billing_interval,
            'trial_period_days': self.trial_period_days,
            'features': self.features or [],
            'is_active': self.is_active
        }


class Subscription(db.Model):
    """User subscriptions to plans."""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.String(50), primary_key=True)  # External subscription ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.String(50), db.ForeignKey('subscription_plans.id'), nullable=False)
    status = db.Column(db.Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)
    
    # Billing details
    current_period_start = db.Column(db.DateTime)
    current_period_end = db.Column(db.DateTime)
    cancel_at_period_end = db.Column(db.Boolean, default=False)
    canceled_at = db.Column(db.DateTime)
    
    # Trial period
    trial_start = db.Column(db.DateTime)
    trial_end = db.Column(db.DateTime)
    
    # Metadata
    metadata = db.Column(db.JSON)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    plan = db.relationship('SubscriptionPlan')
    payments = db.relationship('Payment', back_populates='subscription')
    
    def __repr__(self):
        return f'<Subscription {self.id} {self.status.value}>'
    
    @property
    def is_active(self):
        ""Check if subscription is currently active."""
        now = datetime.utcnow()
        return (
            self.status == SubscriptionStatus.ACTIVE and
            (self.current_period_end is None or self.current_period_end > now) and
            not self.cancel_at_period_end
        )
    
    @property
    def is_trialing(self):
        ""Check if subscription is in trial period."""
        if not self.trial_end:
            return False
        now = datetime.utcnow()
        return self.trial_start <= now <= self.trial_end
    
    def days_until_renewal(self):
        ""Get number of days until next billing date."""
        if not self.current_period_end:
            return None
        return (self.current_period_end - datetime.utcnow()).days
    
    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status.value,
            'is_active': self.is_active,
            'is_trialing': self.is_trialing(),
            'current_period_start': self.current_period_start.isoformat() if self.current_period_start else None,
            'current_period_end': self.current_period_end.isoformat() if self.current_period_end else None,
            'days_until_renewal': self.days_until_renewal(),
            'cancel_at_period_end': self.cancel_at_period_end,
            'plan': self.plan.to_dict() if self.plan else None,
            'trial_end': self.trial_end.isoformat() if self.trial_end else None
        }
