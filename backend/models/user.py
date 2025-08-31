"""
Lucky Kangaroo - Modèle User Complet
Modèle utilisateur avec tous les champs requis pour une plateforme fonctionnelle
"""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    """Modèle utilisateur complet pour Lucky Kangaroo"""
    
    __tablename__ = 'users'
    
    # Identifiants
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Informations personnelles
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    
    # Photo de profil
    profile_photo_url = db.Column(db.String(500), nullable=True)
    profile_photo_id = db.Column(db.Integer, db.ForeignKey('images.id'), nullable=True)
    
    # Géolocalisation
    latitude = db.Column(db.Float, nullable=True, index=True)
    longitude = db.Column(db.Float, nullable=True, index=True)
    address = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=True, index=True)
    postal_code = db.Column(db.String(20), nullable=True)
    country = db.Column(db.String(100), nullable=True, default='France')
    
    # Système de confiance et réputation
    trust_score = db.Column(db.Float, nullable=False, default=50.0)  # 0-100
    reputation_score = db.Column(db.Float, nullable=False, default=0.0)
    total_exchanges = db.Column(db.Integer, nullable=False, default=0)
    successful_exchanges = db.Column(db.Integer, nullable=False, default=0)
    
    # Préférences utilisateur
    preferred_language = db.Column(db.String(10), nullable=False, default='fr')
    preferred_currency = db.Column(db.String(10), nullable=False, default='EUR')
    max_distance_km = db.Column(db.Integer, nullable=False, default=50)  # Rayon de recherche
    
    # Notifications
    email_notifications = db.Column(db.Boolean, nullable=False, default=True)
    push_notifications = db.Column(db.Boolean, nullable=False, default=True)
    sms_notifications = db.Column(db.Boolean, nullable=False, default=False)
    whatsapp_notifications = db.Column(db.Boolean, nullable=False, default=False)
    
    # Compte premium
    is_premium = db.Column(db.Boolean, nullable=False, default=False)
    premium_expires_at = db.Column(db.DateTime, nullable=True)
    
    # Statut du compte
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    phone_verified = db.Column(db.Boolean, nullable=False, default=False)
    
    # Sécurité
    last_login_at = db.Column(db.DateTime, nullable=True)
    login_count = db.Column(db.Integer, nullable=False, default=0)
    failed_login_attempts = db.Column(db.Integer, nullable=False, default=0)
    account_locked_until = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity_at = db.Column(db.DateTime, nullable=True)
    
    # Relations
    listings = db.relationship('Listing', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    exchanges_as_requester = db.relationship('Exchange', foreign_keys='Exchange.requester_id', backref='requester', lazy='dynamic')
    exchanges_as_owner = db.relationship('Exchange', foreign_keys='Exchange.owner_id', backref='owner', lazy='dynamic')
    sent_messages = db.relationship('ChatMessage', foreign_keys='ChatMessage.sender_id', backref='sender', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, username, email, password, **kwargs):
        self.username = username
        self.email = email
        self.set_password(password)
        
        # Définir les autres attributs depuis kwargs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_password(self, password):
        """Définit le mot de passe hashé"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Vérifie le mot de passe"""
        return check_password_hash(self.password_hash, password)
    
    def update_trust_score(self):
        """Met à jour le score de confiance basé sur les échanges"""
        if self.total_exchanges == 0:
            self.trust_score = 50.0
        else:
            success_rate = self.successful_exchanges / self.total_exchanges
            # Score basé sur le taux de succès et le nombre d'échanges
            base_score = success_rate * 80  # 80% max pour le taux de succès
            experience_bonus = min(self.total_exchanges * 2, 20)  # 20% max pour l'expérience
            self.trust_score = min(base_score + experience_bonus, 100.0)
    
    def get_full_name(self):
        """Retourne le nom complet"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return self.username
    
    def get_location_string(self):
        """Retourne la localisation sous forme de chaîne"""
        if self.city and self.country:
            return f"{self.city}, {self.country}"
        elif self.city:
            return self.city
        elif self.address:
            return self.address
        else:
            return "Localisation non définie"
    
    def is_near(self, other_user, max_distance_km=None):
        """Vérifie si un autre utilisateur est à proximité"""
        if not max_distance_km:
            max_distance_km = self.max_distance_km
        
        if not (self.latitude and self.longitude and other_user.latitude and other_user.longitude):
            return False
        
        # Calcul de distance Haversine (simplifié)
        import math
        
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other_user.latitude), math.radians(other_user.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance_km = 6371 * c  # Rayon de la Terre en km
        
        return distance_km <= max_distance_km
    
    def get_distance_to(self, other_user):
        """Calcule la distance vers un autre utilisateur en km"""
        if not (self.latitude and self.longitude and other_user.latitude and other_user.longitude):
            return None
        
        import math
        
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other_user.latitude), math.radians(other_user.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance_km = 6371 * c
        
        return round(distance_km, 2)
    
    def can_login(self):
        """Vérifie si l'utilisateur peut se connecter"""
        if not self.is_active:
            return False, "Compte désactivé"
        
        if self.account_locked_until and self.account_locked_until > datetime.utcnow():
            return False, "Compte temporairement verrouillé"
        
        return True, "OK"
    
    def record_login_attempt(self, success=True):
        """Enregistre une tentative de connexion"""
        if success:
            self.last_login_at = datetime.utcnow()
            self.login_count += 1
            self.failed_login_attempts = 0
            self.account_locked_until = None
            self.last_activity_at = datetime.utcnow()
        else:
            self.failed_login_attempts += 1
            if self.failed_login_attempts >= 5:
                # Verrouiller le compte pour 30 minutes
                from datetime import timedelta
                self.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    def update_activity(self):
        """Met à jour la dernière activité"""
        self.last_activity_at = datetime.utcnow()
    
    def to_dict(self, include_sensitive=False):
        """Convertit l'utilisateur en dictionnaire"""
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'username': self.username,
            'email': self.email if include_sensitive else None,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'bio': self.bio,
            'profile_photo_url': self.profile_photo_url,
            'location': {
                'latitude': self.latitude,
                'longitude': self.longitude,
                'address': self.address,
                'city': self.city,
                'postal_code': self.postal_code,
                'country': self.country,
                'location_string': self.get_location_string()
            },
            'trust_score': self.trust_score,
            'reputation_score': self.reputation_score,
            'total_exchanges': self.total_exchanges,
            'successful_exchanges': self.successful_exchanges,
            'success_rate': (self.successful_exchanges / self.total_exchanges * 100) if self.total_exchanges > 0 else 0,
            'preferences': {
                'language': self.preferred_language,
                'currency': self.preferred_currency,
                'max_distance_km': self.max_distance_km
            },
            'is_premium': self.is_premium,
            'is_verified': self.is_verified,
            'email_verified': self.email_verified,
            'phone_verified': self.phone_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity_at': self.last_activity_at.isoformat() if self.last_activity_at else None
        }
        
        if include_sensitive:
            data.update({
                'phone': self.phone,
                'notifications': {
                    'email': self.email_notifications,
                    'push': self.push_notifications,
                    'sms': self.sms_notifications,
                    'whatsapp': self.whatsapp_notifications
                },
                'security': {
                    'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
                    'login_count': self.login_count,
                    'failed_attempts': self.failed_login_attempts,
                    'account_locked': bool(self.account_locked_until and self.account_locked_until > datetime.utcnow())
                }
            })
        
        return data
    
    def to_public_dict(self):
        """Convertit en dictionnaire public (sans infos sensibles)"""
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.get_full_name(),
            'bio': self.bio,
            'profile_photo_url': self.profile_photo_url,
            'city': self.city,
            'country': self.country,
            'trust_score': self.trust_score,
            'total_exchanges': self.total_exchanges,
            'success_rate': (self.successful_exchanges / self.total_exchanges * 100) if self.total_exchanges > 0 else 0,
            'is_verified': self.is_verified,
            'is_premium': self.is_premium,
            'member_since': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username} ({self.email})>'

    @staticmethod
    def find_nearby_users(latitude, longitude, max_distance_km=50, limit=20):
        """Trouve les utilisateurs à proximité d'une position"""
        # Requête simplifiée - en production, utiliser une requête géospatiale optimisée
        users = User.query.filter(
            User.latitude.isnot(None),
            User.longitude.isnot(None),
            User.is_active == True
        ).limit(limit * 3).all()  # Récupérer plus pour filtrer ensuite
        
        nearby_users = []
        for user in users:
            if user.latitude and user.longitude:
                # Calcul de distance simplifié
                import math
                lat1, lon1 = math.radians(latitude), math.radians(longitude)
                lat2, lon2 = math.radians(user.latitude), math.radians(user.longitude)
                
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                
                a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
                c = 2 * math.asin(math.sqrt(a))
                distance_km = 6371 * c
                
                if distance_km <= max_distance_km:
                    user.distance = round(distance_km, 2)
                    nearby_users.append(user)
        
        # Trier par distance et limiter
        nearby_users.sort(key=lambda u: u.distance)
        return nearby_users[:limit]

