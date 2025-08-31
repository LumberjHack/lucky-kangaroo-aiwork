from backend.extensions import db
"""
Lucky Kangaroo - ModÃ¨le Exchange Complet
ModÃ¨le pour la gestion des Ã©changes entre utilisateurs
"""
from datetime import datetime
from enum import Enum
import uuid
class ExchangeStatus(Enum):
    """Statuts possibles d'un Ã©change"""
    REQUESTED = "requested"        # Demande initiale
    COUNTER_OFFERED = "counter_offered"  # Contre-proposition
    ACCEPTED = "accepted"          # AcceptÃ© par les deux parties
    CONFIRMED = "confirmed"        # ConfirmÃ© (rendez-vous fixÃ©)
    IN_PROGRESS = "in_progress"    # En cours (Ã©change physique)
    COMPLETED = "completed"        # TerminÃ© avec succÃ¨s
    CANCELLED = "cancelled"        # AnnulÃ©
    DISPUTED = "disputed"          # En litige
    EXPIRED = "expired"            # ExpirÃ©

class ExchangeType(Enum):
    """Types d'Ã©change"""
    DIRECT = "direct"              # Ã‰change direct A â†” B
    CHAIN = "chain"                # Ã‰change en chaÃ®ne A â†’ B â†’ C â†’ A
    MULTI = "multi"                # Ã‰change multiple (plusieurs objets)

class Exchange(db.Model):
    """ModÃ¨le pour les Ã©changes entre utilisateurs"""
    
    __tablename__ = 'exchanges'
    
    # Identifiants
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Participants
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Objets Ã©changÃ©s
    offered_listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=False, index=True)
    requested_listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=False, index=True)
    
    # Type et statut
    exchange_type = db.Column(db.Enum(ExchangeType), nullable=False, default=ExchangeType.DIRECT)
    status = db.Column(db.Enum(ExchangeStatus), nullable=False, default=ExchangeStatus.REQUESTED, index=True)
    
    # DÃ©tails de l'Ã©change
    message = db.Column(db.Text, nullable=True)  # Message initial du demandeur
    counter_message = db.Column(db.Text, nullable=True)  # RÃ©ponse du propriÃ©taire
    
    # Valeurs et compensation
    offered_value = db.Column(db.Float, nullable=True)  # Valeur de l'objet offert
    requested_value = db.Column(db.Float, nullable=True)  # Valeur de l'objet demandÃ©
    compensation_amount = db.Column(db.Float, nullable=True)  # Compensation monÃ©taire si nÃ©cessaire
    compensation_currency = db.Column(db.String(10), nullable=False, default='EUR')
    compensation_direction = db.Column(db.String(20), nullable=True)  # 'to_requester' ou 'to_owner'
    
    # Rendez-vous et logistique
    meeting_location = db.Column(db.String(200), nullable=True)
    meeting_latitude = db.Column(db.Float, nullable=True)
    meeting_longitude = db.Column(db.Float, nullable=True)
    meeting_datetime = db.Column(db.DateTime, nullable=True)
    meeting_notes = db.Column(db.Text, nullable=True)
    
    # Ã‰valuations
    requester_rating = db.Column(db.Integer, nullable=True)  # Note donnÃ©e par le demandeur (1-5)
    owner_rating = db.Column(db.Integer, nullable=True)  # Note donnÃ©e par le propriÃ©taire (1-5)
    requester_review = db.Column(db.Text, nullable=True)  # Avis du demandeur
    owner_review = db.Column(db.Text, nullable=True)  # Avis du propriÃ©taire
    
    # ChaÃ®ne d'Ã©change (pour les Ã©changes complexes)
    chain_id = db.Column(db.String(36), nullable=True, index=True)  # ID de la chaÃ®ne d'Ã©change
    chain_position = db.Column(db.Integer, nullable=True)  # Position dans la chaÃ®ne
    chain_total_participants = db.Column(db.Integer, nullable=True)  # Nombre total de participants
    
    # ModÃ©ration et sÃ©curitÃ©
    is_flagged = db.Column(db.Boolean, nullable=False, default=False)
    flag_reason = db.Column(db.String(200), nullable=True)
    flagged_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    flagged_at = db.Column(db.DateTime, nullable=True)
    
    # RÃ©solution de litige
    dispute_reason = db.Column(db.Text, nullable=True)
    dispute_resolution = db.Column(db.Text, nullable=True)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    accepted_at = db.Column(db.DateTime, nullable=True)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True, index=True)
    
    # Relations
    chat_messages = db.relationship('ChatMessage', backref='exchange', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, requester_id, owner_id, offered_listing_id, requested_listing_id, **kwargs):
        self.requester_id = requester_id
        self.owner_id = owner_id
        self.offered_listing_id = offered_listing_id
        self.requested_listing_id = requested_listing_id
        
        # DÃ©finir une date d'expiration (7 jours par dÃ©faut)
        from datetime import timedelta
        self.expires_at = datetime.utcnow() + timedelta(days=7)
        
        # DÃ©finir les autres attributs depuis kwargs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def accept(self, message=None):
        """Accepte l'Ã©change"""
        if self.status == ExchangeStatus.REQUESTED:
            self.status = ExchangeStatus.ACCEPTED
            self.accepted_at = datetime.utcnow()
            if message:
                self.counter_message = message
            
            # Ã‰tendre la date d'expiration
            from datetime import timedelta
            self.expires_at = datetime.utcnow() + timedelta(days=14)
    
    def counter_offer(self, message, compensation_amount=None, compensation_direction=None):
        """Fait une contre-proposition"""
        if self.status in [ExchangeStatus.REQUESTED, ExchangeStatus.COUNTER_OFFERED]:
            self.status = ExchangeStatus.COUNTER_OFFERED
            self.counter_message = message
            
            if compensation_amount is not None:
                self.compensation_amount = compensation_amount
                self.compensation_direction = compensation_direction
    
    def confirm(self, meeting_location=None, meeting_datetime=None, meeting_notes=None):
        """Confirme l'Ã©change avec dÃ©tails du rendez-vous"""
        if self.status == ExchangeStatus.ACCEPTED:
            self.status = ExchangeStatus.CONFIRMED
            self.confirmed_at = datetime.utcnow()
            
            if meeting_location:
                self.meeting_location = meeting_location
            if meeting_datetime:
                self.meeting_datetime = meeting_datetime
            if meeting_notes:
                self.meeting_notes = meeting_notes
    
    def start_exchange(self):
        """DÃ©marre l'Ã©change physique"""
        if self.status == ExchangeStatus.CONFIRMED:
            self.status = ExchangeStatus.IN_PROGRESS
    
    def complete(self, requester_rating=None, owner_rating=None, 
                requester_review=None, owner_review=None):
        """Termine l'Ã©change avec Ã©valuations"""
        if self.status == ExchangeStatus.IN_PROGRESS:
            self.status = ExchangeStatus.COMPLETED
            self.completed_at = datetime.utcnow()
            
            # Enregistrer les Ã©valuations
            if requester_rating is not None:
                self.requester_rating = max(1, min(5, requester_rating))
            if owner_rating is not None:
                self.owner_rating = max(1, min(5, owner_rating))
            if requester_review:
                self.requester_review = requester_review
            if owner_review:
                self.owner_review = owner_review
            
            # Mettre Ã  jour les statistiques des utilisateurs
            self._update_user_stats()
            
            # Marquer les annonces comme Ã©changÃ©es
            if hasattr(self, 'offered_listing'):
                self.offered_listing.mark_as_exchanged()
            if hasattr(self, 'requested_listing'):
                self.requested_listing.mark_as_exchanged()
    
    def cancel(self, reason=None):
        """Annule l'Ã©change"""
        if self.status not in [ExchangeStatus.COMPLETED, ExchangeStatus.CANCELLED]:
            self.status = ExchangeStatus.CANCELLED
            self.cancelled_at = datetime.utcnow()
            if reason:
                self.dispute_reason = reason
    
    def flag(self, user_id, reason):
        """Signale l'Ã©change"""
        self.is_flagged = True
        self.flagged_by = user_id
        self.flag_reason = reason
        self.flagged_at = datetime.utcnow()
    
    def dispute(self, reason):
        """Met l'Ã©change en litige"""
        self.status = ExchangeStatus.DISPUTED
        self.dispute_reason = reason
    
    def resolve_dispute(self, resolution, resolved_by):
        """RÃ©sout un litige"""
        if self.status == ExchangeStatus.DISPUTED:
            self.dispute_resolution = resolution
            self.resolved_by = resolved_by
            self.resolved_at = datetime.utcnow()
            # Le statut peut Ãªtre changÃ© vers COMPLETED ou CANCELLED selon la rÃ©solution
    
    def is_expired(self):
        """VÃ©rifie si l'Ã©change a expirÃ©"""
        return self.expires_at and self.expires_at <= datetime.utcnow()
    
    def can_be_rated_by(self, user_id):
        """VÃ©rifie si un utilisateur peut noter cet Ã©change"""
        if self.status != ExchangeStatus.COMPLETED:
            return False
        
        if user_id == self.requester_id:
            return self.requester_rating is None
        elif user_id == self.owner_id:
            return self.owner_rating is None
        
        return False
    
    def get_other_participant(self, user_id):
        """Retourne l'autre participant de l'Ã©change"""
        if user_id == self.requester_id:
            return self.owner_id
        elif user_id == self.owner_id:
            return self.requester_id
        return None
    
    def get_user_role(self, user_id):
        """Retourne le rÃ´le de l'utilisateur dans l'Ã©change"""
        if user_id == self.requester_id:
            return 'requester'
        elif user_id == self.owner_id:
            return 'owner'
        return None
    
    def calculate_value_difference(self):
        """Calcule la diffÃ©rence de valeur entre les objets"""
        if self.offered_value and self.requested_value:
            return self.requested_value - self.offered_value
        return 0
    
    def get_meeting_location_string(self):
        """Retourne la localisation du rendez-vous sous forme de chaÃ®ne"""
        if self.meeting_location:
            return self.meeting_location
        elif self.meeting_latitude and self.meeting_longitude:
            return f"Lat: {self.meeting_latitude}, Lng: {self.meeting_longitude}"
        return "Lieu non dÃ©fini"
    
    def get_average_rating(self):
        """Calcule la note moyenne de l'Ã©change"""
        ratings = [r for r in [self.requester_rating, self.owner_rating] if r is not None]
        if ratings:
            return sum(ratings) / len(ratings)
        return None
    
    def _update_user_stats(self):
        """Met Ã  jour les statistiques des utilisateurs aprÃ¨s un Ã©change rÃ©ussi"""
        # Mettre Ã  jour les stats du demandeur
        if hasattr(self, 'requester'):
            self.requester.total_exchanges += 1
            self.requester.successful_exchanges += 1
            self.requester.update_trust_score()
        
        # Mettre Ã  jour les stats du propriÃ©taire
        if hasattr(self, 'owner'):
            self.owner.total_exchanges += 1
            self.owner.successful_exchanges += 1
            self.owner.update_trust_score()
    
    def to_dict(self, include_participants=False, include_listings=False, user_perspective=None):
        """Convertit l'Ã©change en dictionnaire"""
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'exchange_type': self.exchange_type.value if self.exchange_type else None,
            'status': self.status.value if self.status else None,
            'message': self.message,
            'counter_message': self.counter_message,
            'values': {
                'offered_value': self.offered_value,
                'requested_value': self.requested_value,
                'value_difference': self.calculate_value_difference(),
                'compensation_amount': self.compensation_amount,
                'compensation_currency': self.compensation_currency,
                'compensation_direction': self.compensation_direction
            },
            'meeting': {
                'location': self.meeting_location,
                'latitude': self.meeting_latitude,
                'longitude': self.meeting_longitude,
                'datetime': self.meeting_datetime.isoformat() if self.meeting_datetime else None,
                'notes': self.meeting_notes,
                'location_string': self.get_meeting_location_string()
            },
            'ratings': {
                'requester_rating': self.requester_rating,
                'owner_rating': self.owner_rating,
                'average_rating': self.get_average_rating(),
                'requester_review': self.requester_review,
                'owner_review': self.owner_review
            },
            'chain': {
                'chain_id': self.chain_id,
                'position': self.chain_position,
                'total_participants': self.chain_total_participants
            } if self.chain_id else None,
            'flags': {
                'is_flagged': self.is_flagged,
                'flag_reason': self.flag_reason,
                'flagged_at': self.flagged_at.isoformat() if self.flagged_at else None
            } if self.is_flagged else None,
            'dispute': {
                'reason': self.dispute_reason,
                'resolution': self.dispute_resolution,
                'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
            } if self.status == ExchangeStatus.DISPUTED or self.dispute_reason else None,
            'timestamps': {
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
                'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None,
                'confirmed_at': self.confirmed_at.isoformat() if self.confirmed_at else None,
                'completed_at': self.completed_at.isoformat() if self.completed_at else None,
                'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
                'expires_at': self.expires_at.isoformat() if self.expires_at else None
            },
            'is_expired': self.is_expired()
        }
        
        if include_participants:
            data['participants'] = {
                'requester_id': self.requester_id,
                'owner_id': self.owner_id
            }
            
            if hasattr(self, 'requester'):
                data['participants']['requester'] = self.requester.to_public_dict()
            if hasattr(self, 'owner'):
                data['participants']['owner'] = self.owner.to_public_dict()
        
        if include_listings:
            data['listings'] = {
                'offered_listing_id': self.offered_listing_id,
                'requested_listing_id': self.requested_listing_id
            }
            
            if hasattr(self, 'offered_listing'):
                data['listings']['offered_listing'] = self.offered_listing.to_dict()
            if hasattr(self, 'requested_listing'):
                data['listings']['requested_listing'] = self.requested_listing.to_dict()
        
        # Perspective utilisateur (masquer certaines infos selon le rÃ´le)
        if user_perspective:
            user_role = self.get_user_role(user_perspective)
            data['user_role'] = user_role
            data['can_rate'] = self.can_be_rated_by(user_perspective)
            data['other_participant_id'] = self.get_other_participant(user_perspective)
        
        return data
    
    def to_summary_dict(self):
        """Convertit en dictionnaire rÃ©sumÃ© pour les listes"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'status': self.status.value if self.status else None,
            'exchange_type': self.exchange_type.value if self.exchange_type else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired(),
            'average_rating': self.get_average_rating(),
            'participants': {
                'requester_id': self.requester_id,
                'owner_id': self.owner_id
            }
        }
    
    def __repr__(self):
        return f'<Exchange {self.id} ({self.status.value if self.status else "unknown"})>'

    @staticmethod
    def get_user_exchanges(user_id, status=None, limit=50):
        """RÃ©cupÃ¨re les Ã©changes d'un utilisateur"""
        query = Exchange.query.filter(
            db.or_(
                Exchange.requester_id == user_id,
                Exchange.owner_id == user_id
            )
        )
        
        if status:
            if isinstance(status, list):
                query = query.filter(Exchange.status.in_(status))
            else:
                query = query.filter(Exchange.status == status)
        
        return query.order_by(Exchange.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_active_exchanges(user_id):
        """RÃ©cupÃ¨re les Ã©changes actifs d'un utilisateur"""
        active_statuses = [
            ExchangeStatus.REQUESTED,
            ExchangeStatus.COUNTER_OFFERED,
            ExchangeStatus.ACCEPTED,
            ExchangeStatus.CONFIRMED,
            ExchangeStatus.IN_PROGRESS
        ]
        
        return Exchange.get_user_exchanges(user_id, status=active_statuses)
    
    @staticmethod
    def get_completed_exchanges(user_id):
        """RÃ©cupÃ¨re les Ã©changes terminÃ©s d'un utilisateur"""
        return Exchange.get_user_exchanges(user_id, status=ExchangeStatus.COMPLETED)
    
    @staticmethod
    def get_exchange_stats(user_id):
        """Calcule les statistiques d'Ã©change d'un utilisateur"""
        exchanges = Exchange.get_user_exchanges(user_id)
        
        stats = {
            'total': len(exchanges),
            'completed': 0,
            'cancelled': 0,
            'in_progress': 0,
            'average_rating_given': 0,
            'average_rating_received': 0,
            'success_rate': 0
        }
        
        ratings_given = []
        ratings_received = []
        
        for exchange in exchanges:
            if exchange.status == ExchangeStatus.COMPLETED:
                stats['completed'] += 1
            elif exchange.status == ExchangeStatus.CANCELLED:
                stats['cancelled'] += 1
            elif exchange.status in [ExchangeStatus.REQUESTED, ExchangeStatus.ACCEPTED, 
                                   ExchangeStatus.CONFIRMED, ExchangeStatus.IN_PROGRESS]:
                stats['in_progress'] += 1
            
            # Ratings donnÃ©s et reÃ§us
            if exchange.requester_id == user_id and exchange.requester_rating:
                ratings_given.append(exchange.requester_rating)
            if exchange.owner_id == user_id and exchange.owner_rating:
                ratings_given.append(exchange.owner_rating)
            
            if exchange.requester_id == user_id and exchange.owner_rating:
                ratings_received.append(exchange.owner_rating)
            if exchange.owner_id == user_id and exchange.requester_rating:
                ratings_received.append(exchange.requester_rating)
        
        if ratings_given:
            stats['average_rating_given'] = sum(ratings_given) / len(ratings_given)
        if ratings_received:
            stats['average_rating_received'] = sum(ratings_received) / len(ratings_received)
        
        if stats['total'] > 0:
            stats['success_rate'] = (stats['completed'] / stats['total']) * 100
        
        return stats
    
    @staticmethod
    def cleanup_expired_exchanges():
        """Nettoie les Ã©changes expirÃ©s"""
        expired_exchanges = Exchange.query.filter(
            Exchange.expires_at <= datetime.utcnow(),
            Exchange.status.in_([
                ExchangeStatus.REQUESTED,
                ExchangeStatus.COUNTER_OFFERED,
                ExchangeStatus.ACCEPTED
            ])
        ).all()
        
        for exchange in expired_exchanges:
            exchange.status = ExchangeStatus.EXPIRED
        
        return len(expired_exchanges)

