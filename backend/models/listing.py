from backend.extensions import db
"""
Lucky Kangaroo - ModÃ¨le Listing Complet
ModÃ¨le pour les annonces d'objets Ã  Ã©changer
"""
from datetime import datetime
from enum import Enum
import uuid
class ListingStatus(Enum):
    """Statuts possibles d'une annonce"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    EXCHANGED = "exchanged"
    EXPIRED = "expired"
    DELETED = "deleted"

class ListingCondition(Enum):
    """Ã‰tats de condition d'un objet"""
    EXCELLENT = "excellent"
    VERY_GOOD = "very_good"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

class Listing(db.Model):
    """ModÃ¨le pour les annonces d'objets Ã  Ã©changer"""
    
    __tablename__ = 'listings'
    
    # Identifiants
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Informations de base
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False, index=True)
    subcategory = db.Column(db.String(100), nullable=True, index=True)
    
    # DÃ©tails de l'objet
    brand = db.Column(db.String(100), nullable=True)
    model = db.Column(db.String(100), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    size = db.Column(db.String(50), nullable=True)
    condition = db.Column(db.Enum(ListingCondition), nullable=False, default=ListingCondition.GOOD)
    condition_details = db.Column(db.Text, nullable=True)
    
    # Valeur et Ã©change
    estimated_value = db.Column(db.Float, nullable=True)  # Valeur estimÃ©e en EUR
    min_exchange_value = db.Column(db.Float, nullable=True)  # Valeur minimum acceptÃ©e
    max_exchange_value = db.Column(db.Float, nullable=True)  # Valeur maximum acceptÃ©e
    currency = db.Column(db.String(10), nullable=False, default='EUR')
    
    # PrÃ©fÃ©rences d'Ã©change
    desired_items = db.Column(db.Text, nullable=True)  # Ce que l'utilisateur souhaite en Ã©change
    desired_categories = db.Column(db.Text, nullable=True)  # CatÃ©gories souhaitÃ©es (JSON)
    exchange_type = db.Column(db.String(20), nullable=False, default='direct')  # direct, chain, both
    
    # GÃ©olocalisation
    latitude = db.Column(db.Float, nullable=True, index=True)
    longitude = db.Column(db.Float, nullable=True, index=True)
    address = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=True, index=True)
    postal_code = db.Column(db.String(20), nullable=True)
    country = db.Column(db.String(100), nullable=True, default='France')
    max_distance_km = db.Column(db.Integer, nullable=False, default=50)
    
    # Photos
    main_photo_url = db.Column(db.String(500), nullable=True)
    main_photo_id = db.Column(db.Integer, db.ForeignKey('images.id'), nullable=True)
    photo_count = db.Column(db.Integer, nullable=False, default=0)
    
    # Statut et visibilitÃ©
    status = db.Column(db.Enum(ListingStatus), nullable=False, default=ListingStatus.DRAFT, index=True)
    is_featured = db.Column(db.Boolean, nullable=False, default=False)  # Mise en avant payante
    is_urgent = db.Column(db.Boolean, nullable=False, default=False)
    is_negotiable = db.Column(db.Boolean, nullable=False, default=True)
    
    # Statistiques
    view_count = db.Column(db.Integer, nullable=False, default=0)
    like_count = db.Column(db.Integer, nullable=False, default=0)
    contact_count = db.Column(db.Integer, nullable=False, default=0)
    exchange_requests_count = db.Column(db.Integer, nullable=False, default=0)
    
    # IA et matching
    ai_tags = db.Column(db.Text, nullable=True)  # Tags gÃ©nÃ©rÃ©s par l'IA (JSON)
    ai_category_confidence = db.Column(db.Float, nullable=True)  # Confiance de la catÃ©gorisation IA
    ai_value_estimate = db.Column(db.Float, nullable=True)  # Estimation de valeur par l'IA
    ai_condition_assessment = db.Column(db.Text, nullable=True)  # Ã‰valuation condition par l'IA (JSON)
    matching_keywords = db.Column(db.Text, nullable=True)  # Mots-clÃ©s pour le matching
    
    # Dates importantes
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True, index=True)
    expires_at = db.Column(db.DateTime, nullable=True, index=True)
    last_activity_at = db.Column(db.DateTime, nullable=True)
    
    # Relations
    images = db.relationship('Image', backref='listing', lazy='dynamic', cascade='all, delete-orphan')
    exchanges_as_offered = db.relationship('Exchange', foreign_keys='Exchange.offered_listing_id', backref='offered_listing', lazy='dynamic')
    exchanges_as_requested = db.relationship('Exchange', foreign_keys='Exchange.requested_listing_id', backref='requested_listing', lazy='dynamic')
    
    def __init__(self, user_id, title, description, category, **kwargs):
        self.user_id = user_id
        self.title = title
        self.description = description
        self.category = category
        
        # DÃ©finir les autres attributs depuis kwargs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def publish(self):
        """Publie l'annonce"""
        if self.status == ListingStatus.DRAFT:
            self.status = ListingStatus.ACTIVE
            self.published_at = datetime.utcnow()
            
            # DÃ©finir une date d'expiration (90 jours par dÃ©faut)
            from datetime import timedelta
            self.expires_at = datetime.utcnow() + timedelta(days=90)
    
    def pause(self):
        """Met en pause l'annonce"""
        if self.status == ListingStatus.ACTIVE:
            self.status = ListingStatus.PAUSED
    
    def reactivate(self):
        """RÃ©active l'annonce"""
        if self.status == ListingStatus.PAUSED:
            self.status = ListingStatus.ACTIVE
    
    def mark_as_exchanged(self):
        """Marque l'annonce comme Ã©changÃ©e"""
        self.status = ListingStatus.EXCHANGED
        self.last_activity_at = datetime.utcnow()
    
    def is_active(self):
        """VÃ©rifie si l'annonce est active"""
        return (self.status == ListingStatus.ACTIVE and 
                (not self.expires_at or self.expires_at > datetime.utcnow()))
    
    def is_expired(self):
        """VÃ©rifie si l'annonce a expirÃ©"""
        return self.expires_at and self.expires_at <= datetime.utcnow()
    
    def increment_view(self):
        """IncrÃ©mente le compteur de vues"""
        self.view_count += 1
        self.last_activity_at = datetime.utcnow()
    
    def increment_like(self):
        """IncrÃ©mente le compteur de likes"""
        self.like_count += 1
        self.last_activity_at = datetime.utcnow()
    
    def increment_contact(self):
        """IncrÃ©mente le compteur de contacts"""
        self.contact_count += 1
        self.last_activity_at = datetime.utcnow()
    
    def increment_exchange_request(self):
        """IncrÃ©mente le compteur de demandes d'Ã©change"""
        self.exchange_requests_count += 1
        self.last_activity_at = datetime.utcnow()
    
    def get_location_string(self):
        """Retourne la localisation sous forme de chaÃ®ne"""
        if self.city and self.country:
            return f"{self.city}, {self.country}"
        elif self.city:
            return self.city
        elif self.address:
            return self.address
        else:
            return "Localisation non dÃ©finie"
    
    def get_distance_to(self, latitude, longitude):
        """Calcule la distance vers une position en km"""
        if not (self.latitude and self.longitude):
            return None
        
        import math
        
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(latitude), math.radians(longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance_km = 6371 * c
        
        return round(distance_km, 2)
    
    def is_near(self, latitude, longitude, max_distance_km=None):
        """VÃ©rifie si l'annonce est Ã  proximitÃ© d'une position"""
        if not max_distance_km:
            max_distance_km = self.max_distance_km
        
        distance = self.get_distance_to(latitude, longitude)
        return distance is not None and distance <= max_distance_km
    
    def get_ai_tags_list(self):
        """Retourne les tags IA sous forme de liste"""
        if self.ai_tags:
            import json
            try:
                return json.loads(self.ai_tags)
            except:
                return []
        return []
    
    def set_ai_tags(self, tags_list):
        """DÃ©finit les tags IA depuis une liste"""
        import json
        self.ai_tags = json.dumps(tags_list) if tags_list else None
    
    def get_desired_categories_list(self):
        """Retourne les catÃ©gories dÃ©sirÃ©es sous forme de liste"""
        if self.desired_categories:
            import json
            try:
                return json.loads(self.desired_categories)
            except:
                return []
        return []
    
    def set_desired_categories(self, categories_list):
        """DÃ©finit les catÃ©gories dÃ©sirÃ©es depuis une liste"""
        import json
        self.desired_categories = json.dumps(categories_list) if categories_list else None
    
    def get_ai_condition_assessment_dict(self):
        """Retourne l'Ã©valuation de condition IA sous forme de dictionnaire"""
        if self.ai_condition_assessment:
            import json
            try:
                return json.loads(self.ai_condition_assessment)
            except:
                return {}
        return {}
    
    def set_ai_condition_assessment(self, assessment_dict):
        """DÃ©finit l'Ã©valuation de condition IA depuis un dictionnaire"""
        import json
        self.ai_condition_assessment = json.dumps(assessment_dict) if assessment_dict else None
    
    def calculate_matching_score(self, other_listing):
        """Calcule un score de compatibilitÃ© avec une autre annonce"""
        score = 0.0
        
        # Score basÃ© sur les catÃ©gories dÃ©sirÃ©es
        if self.get_desired_categories_list():
            if other_listing.category in self.get_desired_categories_list():
                score += 30
        
        # Score basÃ© sur les mots-clÃ©s
        if self.desired_items and other_listing.title:
            desired_words = set(self.desired_items.lower().split())
            title_words = set(other_listing.title.lower().split())
            common_words = desired_words.intersection(title_words)
            score += len(common_words) * 5
        
        # Score basÃ© sur la valeur
        if self.estimated_value and other_listing.estimated_value:
            value_diff = abs(self.estimated_value - other_listing.estimated_value)
            max_value = max(self.estimated_value, other_listing.estimated_value)
            if max_value > 0:
                value_score = max(0, 20 - (value_diff / max_value * 20))
                score += value_score
        
        # Score basÃ© sur la distance
        if (self.latitude and self.longitude and 
            other_listing.latitude and other_listing.longitude):
            distance = self.get_distance_to(other_listing.latitude, other_listing.longitude)
            if distance is not None:
                if distance <= 10:
                    score += 20
                elif distance <= 25:
                    score += 15
                elif distance <= 50:
                    score += 10
                elif distance <= 100:
                    score += 5
        
        # Score basÃ© sur la condition
        condition_scores = {
            ListingCondition.EXCELLENT: 5,
            ListingCondition.VERY_GOOD: 4,
            ListingCondition.GOOD: 3,
            ListingCondition.FAIR: 2,
            ListingCondition.POOR: 1
        }
        
        self_condition_score = condition_scores.get(self.condition, 3)
        other_condition_score = condition_scores.get(other_listing.condition, 3)
        condition_compatibility = 5 - abs(self_condition_score - other_condition_score)
        score += condition_compatibility * 2
        
        return min(score, 100.0)  # Score maximum de 100
    
    def to_dict(self, include_user=False, include_stats=False):
        """Convertit l'annonce en dictionnaire"""
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'subcategory': self.subcategory,
            'brand': self.brand,
            'model': self.model,
            'color': self.color,
            'size': self.size,
            'condition': self.condition.value if self.condition else None,
            'condition_details': self.condition_details,
            'estimated_value': self.estimated_value,
            'currency': self.currency,
            'desired_items': self.desired_items,
            'desired_categories': self.get_desired_categories_list(),
            'exchange_type': self.exchange_type,
            'location': {
                'latitude': self.latitude,
                'longitude': self.longitude,
                'address': self.address,
                'city': self.city,
                'postal_code': self.postal_code,
                'country': self.country,
                'location_string': self.get_location_string(),
                'max_distance_km': self.max_distance_km
            },
            'main_photo_url': self.main_photo_url,
            'photo_count': self.photo_count,
            'status': self.status.value if self.status else None,
            'is_featured': self.is_featured,
            'is_urgent': self.is_urgent,
            'is_negotiable': self.is_negotiable,
            'ai_tags': self.get_ai_tags_list(),
            'ai_category_confidence': self.ai_category_confidence,
            'ai_value_estimate': self.ai_value_estimate,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active(),
            'is_expired': self.is_expired()
        }
        
        if include_user and hasattr(self, 'user'):
            data['user'] = self.user.to_public_dict()
        
        if include_stats:
            data['stats'] = {
                'view_count': self.view_count,
                'like_count': self.like_count,
                'contact_count': self.contact_count,
                'exchange_requests_count': self.exchange_requests_count
            }
        
        return data
    
    def to_search_dict(self):
        """Convertit en dictionnaire optimisÃ© pour la recherche"""
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'subcategory': self.subcategory,
            'brand': self.brand,
            'model': self.model,
            'condition': self.condition.value if self.condition else None,
            'estimated_value': self.estimated_value,
            'city': self.city,
            'country': self.country,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'main_photo_url': self.main_photo_url,
            'is_featured': self.is_featured,
            'is_urgent': self.is_urgent,
            'ai_tags': self.get_ai_tags_list(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_id': self.user_id
        }
    
    def __repr__(self):
        return f'<Listing {self.title} by User {self.user_id}>'

    @staticmethod
    def find_nearby_listings(latitude, longitude, max_distance_km=50, category=None, limit=20):
        """Trouve les annonces Ã  proximitÃ© d'une position"""
        query = Listing.query.filter(
            Listing.latitude.isnot(None),
            Listing.longitude.isnot(None),
            Listing.status == ListingStatus.ACTIVE
        )
        
        if category:
            query = query.filter(Listing.category == category)
        
        listings = query.limit(limit * 3).all()  # RÃ©cupÃ©rer plus pour filtrer ensuite
        
        nearby_listings = []
        for listing in listings:
            if listing.latitude and listing.longitude:
                distance = listing.get_distance_to(latitude, longitude)
                if distance is not None and distance <= max_distance_km:
                    listing.distance = distance
                    nearby_listings.append(listing)
        
        # Trier par distance et limiter
        nearby_listings.sort(key=lambda l: l.distance)
        return nearby_listings[:limit]
    
    @staticmethod
    def search_listings(query_text=None, category=None, min_value=None, max_value=None, 
                       condition=None, latitude=None, longitude=None, max_distance_km=50, 
                       limit=20, offset=0):
        """Recherche avancÃ©e d'annonces"""
        query = Listing.query.filter(Listing.status == ListingStatus.ACTIVE)
        
        # Filtre par texte
        if query_text:
            search_filter = db.or_(
                Listing.title.ilike(f'%{query_text}%'),
                Listing.description.ilike(f'%{query_text}%'),
                Listing.brand.ilike(f'%{query_text}%'),
                Listing.model.ilike(f'%{query_text}%'),
                Listing.desired_items.ilike(f'%{query_text}%')
            )
            query = query.filter(search_filter)
        
        # Filtre par catÃ©gorie
        if category:
            query = query.filter(Listing.category == category)
        
        # Filtre par valeur
        if min_value is not None:
            query = query.filter(Listing.estimated_value >= min_value)
        if max_value is not None:
            query = query.filter(Listing.estimated_value <= max_value)
        
        # Filtre par condition
        if condition:
            query = query.filter(Listing.condition == condition)
        
        # Tri par pertinence (featured first, puis par date)
        query = query.order_by(
            Listing.is_featured.desc(),
            Listing.is_urgent.desc(),
            Listing.published_at.desc()
        )
        
        # Pagination
        listings = query.offset(offset).limit(limit).all()
        
        # Calcul de distance si position fournie
        if latitude is not None and longitude is not None:
            for listing in listings:
                if listing.latitude and listing.longitude:
                    distance = listing.get_distance_to(latitude, longitude)
                    listing.distance = distance
                    
            # Filtrer par distance si spÃ©cifiÃ©e
            if max_distance_km:
                listings = [l for l in listings if hasattr(l, 'distance') and 
                           l.distance is not None and l.distance <= max_distance_km]
        
        return listings

