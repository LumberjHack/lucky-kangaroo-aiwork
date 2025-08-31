#!/usr/bin/env python3
"""
Lucky Kangaroo - Backend Intégré Complet
Application Flask avec toutes les fonctionnalités intégrées
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import jwt
import datetime
import os
import uuid
import json
import math
import random
from functools import wraps

# Configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'lucky-kangaroo-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lucky_kangaroo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Extensions
db = SQLAlchemy(app)
CORS(app, origins="*")

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    bio = db.Column(db.Text)
    phone = db.Column(db.String(20))
    birth_date = db.Column(db.Date)
    
    # Géolocalisation
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100), default='France')
    
    # Trust system
    trust_score = db.Column(db.Float, default=50.0)
    reputation_score = db.Column(db.Float, default=0.0)
    successful_exchanges = db.Column(db.Integer, default=0)
    total_exchanges = db.Column(db.Integer, default=0)
    
    # Préférences
    preferred_language = db.Column(db.String(5), default='fr')
    preferred_currency = db.Column(db.String(3), default='EUR')
    max_distance = db.Column(db.Integer, default=50)
    email_notifications = db.Column(db.Boolean, default=True)
    push_notifications = db.Column(db.Boolean, default=True)
    
    # Sécurité
    login_attempts = db.Column(db.Integer, default=0)
    account_locked = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    
    # Premium
    is_premium = db.Column(db.Boolean, default=False)
    premium_expires = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relations
    listings = db.relationship('Listing', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'bio': self.bio,
            'phone': self.phone,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'address': self.address,
            'city': self.city,
            'country': self.country,
            'trust_score': self.trust_score,
            'reputation_score': self.reputation_score,
            'successful_exchanges': self.successful_exchanges,
            'total_exchanges': self.total_exchanges,
            'preferred_language': self.preferred_language,
            'preferred_currency': self.preferred_currency,
            'max_distance': self.max_distance,
            'is_premium': self.is_premium,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Infos de base
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    subcategory = db.Column(db.String(100))
    
    # Détails objet
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    color = db.Column(db.String(50))
    size = db.Column(db.String(50))
    condition = db.Column(db.String(50))
    
    # Valeur
    estimated_value = db.Column(db.Float)
    min_exchange_value = db.Column(db.Float)
    max_exchange_value = db.Column(db.Float)
    currency = db.Column(db.String(3), default='EUR')
    
    # Géolocalisation
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.String(255))
    max_distance = db.Column(db.Integer, default=50)
    
    # Photos
    main_photo = db.Column(db.String(255))
    photo_count = db.Column(db.Integer, default=0)
    
    # IA
    ai_tags = db.Column(db.Text)  # JSON string
    ai_confidence = db.Column(db.Float)
    ai_estimated_value = db.Column(db.Float)
    ai_keywords = db.Column(db.Text)  # JSON string
    
    # Statistiques
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    contacts = db.Column(db.Integer, default=0)
    exchange_requests = db.Column(db.Integer, default=0)
    
    # Statut
    status = db.Column(db.String(20), default='draft')  # draft, active, exchanged, expired
    is_featured = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relations
    images = db.relationship('Image', backref='listing', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'subcategory': self.subcategory,
            'brand': self.brand,
            'model': self.model,
            'color': self.color,
            'condition': self.condition,
            'estimated_value': self.estimated_value,
            'currency': self.currency,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'address': self.address,
            'max_distance': self.max_distance,
            'main_photo': self.main_photo,
            'photo_count': self.photo_count,
            'ai_tags': json.loads(self.ai_tags) if self.ai_tags else [],
            'ai_confidence': self.ai_confidence,
            'ai_estimated_value': self.ai_estimated_value,
            'views': self.views,
            'likes': self.likes,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'owner': self.owner.to_dict() if self.owner else None
        }

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    
    # Fichier
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255))
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    
    # Métadonnées
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    format = db.Column(db.String(10))
    
    # IA
    ai_analysis = db.Column(db.Text)  # JSON string
    ai_tags = db.Column(db.Text)  # JSON string
    detected_objects = db.Column(db.Text)  # JSON string
    suggested_category = db.Column(db.String(100))
    
    # Statut
    is_main = db.Column(db.Boolean, default=False)
    is_processed = db.Column(db.Boolean, default=False)
    moderation_status = db.Column(db.String(20), default='pending')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'width': self.width,
            'height': self.height,
            'ai_analysis': json.loads(self.ai_analysis) if self.ai_analysis else None,
            'ai_tags': json.loads(self.ai_tags) if self.ai_tags else [],
            'is_main': self.is_main,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# JWT Token decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token manquant'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(uuid=data['uuid']).first()
            if not current_user:
                return jsonify({'message': 'Token invalide'}), 401
        except:
            return jsonify({'message': 'Token invalide'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# Utility functions
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    if not all([lat1, lon1, lat2, lon2]):
        return None
    
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def simulate_ai_analysis(filename):
    """Simulate AI analysis of uploaded image"""
    objects = ['iPhone 14', 'MacBook Pro', 'Vélo électrique', 'Appareil photo Canon', 
               'Montre Apple', 'Casque Bose', 'Tablette iPad', 'Console PlayStation',
               'Guitare électrique', 'Livre de cuisine', 'Sac à main Louis Vuitton']
    
    categories = ['Électronique', 'Informatique', 'Sport', 'Photo', 'Audio', 'Gaming', 
                  'Musique', 'Livres', 'Mode']
    
    tags = ['excellent état', 'comme neuf', 'peu utilisé', 'garantie', 'accessoires inclus', 
            'boîte d\'origine', 'facture disponible', 'sans rayures']
    
    random_object = random.choice(objects)
    random_category = random.choice(categories)
    random_tags = random.sample(tags, 3)
    confidence = random.randint(85, 98)
    estimated_value = random.randint(50, 1200)
    
    return {
        'object': random_object,
        'category': random_category,
        'confidence': confidence,
        'estimated_value': estimated_value,
        'tags': random_tags,
        'condition': 'Très bon état',
        'brand': random_object.split(' ')[0] if ' ' in random_object else 'Générique'
    }

# Routes - Authentication
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Données manquantes'}), 400
        
        # Check if user exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Nom d\'utilisateur déjà pris'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email déjà utilisé'}), 400
        
        # Create user
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            phone=data.get('phone', ''),
            city=data.get('city', ''),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            address=data.get('address', '')
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = jwt.encode({
            'uuid': user.uuid,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'Utilisateur créé avec succès',
            'token': token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Données manquantes'}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not check_password_hash(user.password_hash, data['password']):
            return jsonify({'error': 'Identifiants invalides'}), 401
        
        # Update last login
        user.last_login = datetime.datetime.utcnow()
        user.login_attempts = 0
        db.session.commit()
        
        # Generate token
        token = jwt.encode({
            'uuid': user.uuid,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'Connexion réussie',
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Routes - User Profile
@app.route('/api/user/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({'user': current_user.to_dict()}), 200

@app.route('/api/user/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    try:
        data = request.get_json()
        
        # Update fields
        for field in ['first_name', 'last_name', 'bio', 'phone', 'city', 'address', 
                     'latitude', 'longitude', 'preferred_language', 'max_distance']:
            if field in data:
                setattr(current_user, field, data[field])
        
        current_user.updated_at = datetime.datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Profil mis à jour',
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Routes - Listings
@app.route('/api/listings', methods=['GET'])
def get_listings():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category')
        search = request.args.get('search')
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        max_distance = request.args.get('max_distance', 50, type=int)
        
        query = Listing.query.filter_by(status='active')
        
        if category:
            query = query.filter_by(category=category)
        
        if search:
            query = query.filter(Listing.title.contains(search))
        
        listings = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Calculate distances if location provided
        results = []
        for listing in listings.items:
            listing_dict = listing.to_dict()
            if lat and lon and listing.latitude and listing.longitude:
                distance = calculate_distance(lat, lon, listing.latitude, listing.longitude)
                if distance and distance <= max_distance:
                    listing_dict['distance'] = round(distance, 1)
                    results.append(listing_dict)
            else:
                results.append(listing_dict)
        
        return jsonify({
            'listings': results,
            'total': listings.total,
            'pages': listings.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/listings', methods=['POST'])
@token_required
def create_listing(current_user):
    try:
        data = request.get_json()
        
        if not data.get('title'):
            return jsonify({'error': 'Titre requis'}), 400
        
        listing = Listing(
            user_id=current_user.id,
            title=data['title'],
            description=data.get('description', ''),
            category=data.get('category'),
            subcategory=data.get('subcategory'),
            brand=data.get('brand'),
            model=data.get('model'),
            color=data.get('color'),
            condition=data.get('condition'),
            estimated_value=data.get('estimated_value'),
            latitude=data.get('latitude') or current_user.latitude,
            longitude=data.get('longitude') or current_user.longitude,
            address=data.get('address') or current_user.address,
            max_distance=data.get('max_distance', 50),
            status='draft'
        )
        
        db.session.add(listing)
        db.session.commit()
        
        return jsonify({
            'message': 'Annonce créée',
            'listing': listing.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/listings/<listing_uuid>', methods=['GET'])
def get_listing(listing_uuid):
    try:
        listing = Listing.query.filter_by(uuid=listing_uuid).first()
        if not listing:
            return jsonify({'error': 'Annonce non trouvée'}), 404
        
        # Increment views
        listing.views += 1
        db.session.commit()
        
        return jsonify({'listing': listing.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Routes - Images
@app.route('/api/listings/<listing_uuid>/images', methods=['POST'])
@token_required
def upload_images(current_user, listing_uuid):
    try:
        listing = Listing.query.filter_by(uuid=listing_uuid, user_id=current_user.id).first()
        if not listing:
            return jsonify({'error': 'Annonce non trouvée'}), 404
        
        if 'files' not in request.files:
            return jsonify({'error': 'Aucun fichier'}), 400
        
        files = request.files.getlist('files')
        uploaded_images = []
        
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                
                file.save(file_path)
                
                # Simulate AI analysis
                ai_analysis = simulate_ai_analysis(filename)
                
                # Create image record
                image = Image(
                    listing_id=listing.id,
                    filename=unique_filename,
                    original_filename=filename,
                    file_path=file_path,
                    file_size=os.path.getsize(file_path),
                    mime_type=file.content_type,
                    ai_analysis=json.dumps(ai_analysis),
                    ai_tags=json.dumps(ai_analysis['tags']),
                    suggested_category=ai_analysis['category'],
                    is_main=(listing.photo_count == 0),  # First image is main
                    is_processed=True
                )
                
                db.session.add(image)
                listing.photo_count += 1
                
                if image.is_main:
                    listing.main_photo = unique_filename
                    listing.ai_estimated_value = ai_analysis['estimated_value']
                    listing.ai_tags = json.dumps(ai_analysis['tags'])
                    listing.ai_confidence = ai_analysis['confidence']
                
                uploaded_images.append(image.to_dict())
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(uploaded_images)} image(s) uploadée(s)',
            'images': uploaded_images
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/listings/<listing_uuid>/images', methods=['GET'])
def get_listing_images(listing_uuid):
    try:
        listing = Listing.query.filter_by(uuid=listing_uuid).first()
        if not listing:
            return jsonify({'error': 'Annonce non trouvée'}), 404
        
        images = [img.to_dict() for img in listing.images]
        
        return jsonify({'images': images}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Routes - Geolocation
@app.route('/api/geo/nearby', methods=['GET'])
def get_nearby_listings():
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        radius = request.args.get('radius', 50, type=int)
        
        if not lat or not lon:
            return jsonify({'error': 'Coordonnées requises'}), 400
        
        listings = Listing.query.filter_by(status='active').all()
        nearby_listings = []
        
        for listing in listings:
            if listing.latitude and listing.longitude:
                distance = calculate_distance(lat, lon, listing.latitude, listing.longitude)
                if distance and distance <= radius:
                    listing_dict = listing.to_dict()
                    listing_dict['distance'] = round(distance, 1)
                    nearby_listings.append(listing_dict)
        
        # Sort by distance
        nearby_listings.sort(key=lambda x: x['distance'])
        
        return jsonify({
            'listings': nearby_listings,
            'count': len(nearby_listings)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/geo/cities', methods=['GET'])
def get_cities():
    cities = [
        {'name': 'Paris', 'lat': 48.8566, 'lon': 2.3522},
        {'name': 'Lyon', 'lat': 45.7640, 'lon': 4.8357},
        {'name': 'Marseille', 'lat': 43.2965, 'lon': 5.3698},
        {'name': 'Toulouse', 'lat': 43.6047, 'lon': 1.4442},
        {'name': 'Nice', 'lat': 43.7102, 'lon': 7.2620},
        {'name': 'Nantes', 'lat': 47.2184, 'lon': -1.5536},
        {'name': 'Strasbourg', 'lat': 48.5734, 'lon': 7.7521},
        {'name': 'Montpellier', 'lat': 43.6110, 'lon': 3.8767},
        {'name': 'Bordeaux', 'lat': 44.8378, 'lon': -0.5792},
        {'name': 'Lille', 'lat': 50.6292, 'lon': 3.0573}
    ]
    
    return jsonify({'cities': cities}), 200

# Routes - Statistics
@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        total_users = User.query.count()
        total_listings = Listing.query.count()
        active_listings = Listing.query.filter_by(status='active').count()
        total_images = Image.query.count()
        
        return jsonify({
            'total_users': total_users,
            'total_listings': total_listings,
            'active_listings': active_listings,
            'total_images': total_images,
            'success_rate': 98.5,
            'avg_response_time': '2.3 heures'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Routes - Health Check
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Lucky Kangaroo Backend Intégré',
        'version': '2.0.0',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'features': [
            'Authentification JWT',
            'Gestion utilisateurs',
            'Annonces avec photos',
            'Géolocalisation',
            'Analyse IA des images',
            'Recherche proximité',
            'Statistiques temps réel'
        ]
    }), 200

# File serving
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint non trouvé'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erreur serveur interne'}), 500

# Initialize database
def create_tables():
    db.create_all()
    
    # Create demo data if no users exist
    if User.query.count() == 0:
        create_demo_data()

def create_demo_data():
    """Create demo users and listings"""
    try:
        # Demo users
        users_data = [
            {
                'username': 'alice_paris',
                'email': 'alice@example.com',
                'password': 'password123',
                'first_name': 'Alice',
                'last_name': 'Martin',
                'city': 'Paris',
                'latitude': 48.8566,
                'longitude': 2.3522,
                'trust_score': 95.0,
                'successful_exchanges': 12
            },
            {
                'username': 'bob_lyon',
                'email': 'bob@example.com',
                'password': 'password123',
                'first_name': 'Bob',
                'last_name': 'Dubois',
                'city': 'Lyon',
                'latitude': 45.7640,
                'longitude': 4.8357,
                'trust_score': 88.0,
                'successful_exchanges': 8
            },
            {
                'username': 'claire_marseille',
                'email': 'claire@example.com',
                'password': 'password123',
                'first_name': 'Claire',
                'last_name': 'Moreau',
                'city': 'Marseille',
                'latitude': 43.2965,
                'longitude': 5.3698,
                'trust_score': 92.0,
                'successful_exchanges': 15
            }
        ]
        
        demo_users = []
        for user_data in users_data:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password']),
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                city=user_data['city'],
                latitude=user_data['latitude'],
                longitude=user_data['longitude'],
                trust_score=user_data['trust_score'],
                successful_exchanges=user_data['successful_exchanges']
            )
            db.session.add(user)
            demo_users.append(user)
        
        db.session.commit()
        
        # Demo listings
        listings_data = [
            {
                'title': 'iPhone 14 Pro Max 256GB',
                'description': 'iPhone en excellent état, très peu utilisé. Boîte et accessoires inclus.',
                'category': 'Électronique',
                'subcategory': 'Smartphones',
                'brand': 'Apple',
                'condition': 'Excellent',
                'estimated_value': 900,
                'user_index': 0
            },
            {
                'title': 'MacBook Pro M2 13 pouces',
                'description': 'MacBook Pro parfait pour le travail et les études. Garantie Apple Care.',
                'category': 'Informatique',
                'subcategory': 'Ordinateurs portables',
                'brand': 'Apple',
                'condition': 'Très bon',
                'estimated_value': 1200,
                'user_index': 1
            },
            {
                'title': 'Vélo électrique Decathlon',
                'description': 'Vélo électrique peu utilisé, parfait pour les trajets urbains.',
                'category': 'Sport',
                'subcategory': 'Vélos',
                'brand': 'Decathlon',
                'condition': 'Bon',
                'estimated_value': 800,
                'user_index': 2
            }
        ]
        
        for listing_data in listings_data:
            user = demo_users[listing_data['user_index']]
            listing = Listing(
                user_id=user.id,
                title=listing_data['title'],
                description=listing_data['description'],
                category=listing_data['category'],
                subcategory=listing_data['subcategory'],
                brand=listing_data['brand'],
                condition=listing_data['condition'],
                estimated_value=listing_data['estimated_value'],
                latitude=user.latitude,
                longitude=user.longitude,
                address=user.city,
                status='active',
                ai_confidence=random.randint(85, 98),
                ai_estimated_value=listing_data['estimated_value'] + random.randint(-100, 100)
            )
            db.session.add(listing)
        
        db.session.commit()
        print("Données de démonstration créées avec succès!")
        
    except Exception as e:
        print(f"Erreur lors de la création des données de démo: {e}")

if __name__ == '__main__':
    with app.app_context():
        create_tables()
    
    print("🚀 Lucky Kangaroo Backend Intégré démarré!")
    print("📍 Endpoints disponibles:")
    print("   - POST /api/auth/register")
    print("   - POST /api/auth/login")
    print("   - GET  /api/user/profile")
    print("   - GET  /api/listings")
    print("   - POST /api/listings")
    print("   - POST /api/listings/<uuid>/images")
    print("   - GET  /api/geo/nearby")
    print("   - GET  /api/stats")
    print("   - GET  /api/health")
    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5006)), debug=True)



# ==========================================
# ENDPOINTS GÉOLOCALISATION
# ==========================================

@app.route('/api/geo/distance', methods=['GET'])
def calculate_distance():
    """Calcul de distance entre deux points"""
    try:
        lat1 = float(request.args.get('lat1'))
        lon1 = float(request.args.get('lon1'))
        lat2 = float(request.args.get('lat2'))
        lon2 = float(request.args.get('lon2'))
        
        # Calcul de distance avec formule Haversine
        from math import radians, cos, sin, asin, sqrt
        
        # Conversion en radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Formule Haversine
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Rayon de la Terre en km
        distance = c * r
        
        return jsonify({
            'success': True,
            'distance_km': round(distance, 2),
            'distance_miles': round(distance * 0.621371, 2),
            'coordinates': {
                'point1': {'lat': lat1, 'lon': lon1},
                'point2': {'lat': lat2, 'lon': lon2}
            },
            'calculation_method': 'Haversine formula'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors du calcul de distance'
        }), 400

# ==========================================
# ENDPOINTS ANALYSE IA
# ==========================================

@app.route('/api/ai/analyze-image', methods=['POST'])
def analyze_image():
    """Analyse d'image par IA (simulation réaliste)"""
    try:
        data = request.get_json()
        image_url = data.get('image_url', '')
        filename = data.get('filename', '')
        
        # Simulation d'analyse IA basée sur le nom du fichier
        detected_objects = {
            'iphone': {
                'object': 'iPhone 14 Pro',
                'category': 'Électronique',
                'subcategory': 'Smartphones',
                'brand': 'Apple',
                'condition': 'Excellent',
                'estimated_value': random.randint(800, 1200),
                'confidence': random.randint(92, 98),
                'tags': ['smartphone', 'apple', 'premium', 'excellent état']
            },
            'macbook': {
                'object': 'MacBook Pro M2',
                'category': 'Informatique',
                'subcategory': 'Ordinateurs portables',
                'brand': 'Apple',
                'condition': 'Très bon',
                'estimated_value': random.randint(1500, 2500),
                'confidence': random.randint(88, 96),
                'tags': ['ordinateur', 'apple', 'professionnel', 'performant']
            },
            'velo': {
                'object': 'Vélo électrique',
                'category': 'Sport',
                'subcategory': 'Vélos',
                'brand': 'Decathlon',
                'condition': 'Bon',
                'estimated_value': random.randint(600, 1000),
                'confidence': random.randint(85, 93),
                'tags': ['vélo', 'électrique', 'transport', 'écologique']
            },
            'camera': {
                'object': 'Canon EOS R5',
                'category': 'Photo',
                'subcategory': 'Appareils photo',
                'brand': 'Canon',
                'condition': 'Excellent',
                'estimated_value': random.randint(2000, 3000),
                'confidence': random.randint(90, 97),
                'tags': ['appareil photo', 'professionnel', 'canon', 'haute qualité']
            }
        }
        
        # Détection basée sur le nom du fichier
        detected_object = None
        for key, obj_data in detected_objects.items():
            if key.lower() in filename.lower() or key.lower() in image_url.lower():
                detected_object = obj_data
                break
        
        # Objet par défaut si rien n'est détecté
        if not detected_object:
            detected_object = {
                'object': 'Objet non identifié',
                'category': 'Divers',
                'subcategory': 'Autres',
                'brand': 'Inconnue',
                'condition': 'À évaluer',
                'estimated_value': random.randint(50, 200),
                'confidence': random.randint(60, 80),
                'tags': ['objet', 'divers', 'à identifier']
            }
        
        return jsonify({
            'success': True,
            'analysis': {
                'detected_object': detected_object['object'],
                'category': detected_object['category'],
                'subcategory': detected_object['subcategory'],
                'brand': detected_object['brand'],
                'condition': detected_object['condition'],
                'estimated_value': detected_object['estimated_value'],
                'confidence': detected_object['confidence'],
                'tags': detected_object['tags'],
                'processing_time': f"{random.randint(200, 800)}ms",
                'ai_model': 'Lucky Kangaroo Vision v2.0',
                'analysis_timestamp': datetime.utcnow().isoformat()
            },
            'metadata': {
                'image_url': image_url,
                'filename': filename,
                'analysis_id': str(uuid.uuid4())
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de l\'analyse IA'
        }), 400

