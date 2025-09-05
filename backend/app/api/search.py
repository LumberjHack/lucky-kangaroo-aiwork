"""
Blueprint de recherche pour Lucky Kangaroo
Recherche avancée avec filtres, géolocalisation et IA
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from marshmallow import Schema, fields, validate, ValidationError
from sqlalchemy import and_, or_, func, text
from sqlalchemy.orm import joinedload
import math
import re

from app import db
from app.models.user import User
from app.models.listing import Listing
from app.models.listing import ListingCategory, ListingImage

# Créer le blueprint
search_bp = Blueprint('search', __name__)

# Limiter de taux
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per hour"]
)

# Schémas de validation
class SearchSchema(Schema):
    query = fields.Str(validate=validate.Length(max=200))
    category_id = fields.UUID()
    listing_type = fields.Str(validate=validate.OneOf(['good', 'service', 'both']))
    condition = fields.List(fields.Str(validate=validate.OneOf(['excellent', 'very_good', 'good', 'fair', 'poor', 'new'])))
    min_price = fields.Float(validate=validate.Range(min=0))
    max_price = fields.Float(validate=validate.Range(min=0))
    currency = fields.Str(validate=validate.OneOf(['CHF', 'EUR', 'USD']))
    city = fields.Str(validate=validate.Length(max=100))
    postal_code = fields.Str(validate=validate.Length(max=20))
    country = fields.Str(validate=validate.Length(max=100))
    latitude = fields.Float(validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(validate=validate.Range(min=-180, max=180))
    radius_km = fields.Float(validate=validate.Range(min=0.1, max=1000))
    exchange_type = fields.Str(validate=validate.OneOf(['direct', 'chain', 'both']))
    brand = fields.Str(validate=validate.Length(max=100))
    model = fields.Str(validate=validate.Length(max=100))
    year_min = fields.Int(validate=validate.Range(min=1900, max=2030))
    year_max = fields.Int(validate=validate.Range(min=1900, max=2030))
    sort_by = fields.Str(validate=validate.OneOf(['relevance', 'date', 'price_asc', 'price_desc', 'distance']))
    page = fields.Int(validate=validate.Range(min=1, max=100))
    per_page = fields.Int(validate=validate.Range(min=1, max=50))

class SearchFiltersSchema(Schema):
    """Schéma pour les filtres de recherche"""
    categories = fields.List(fields.Dict())
    conditions = fields.List(fields.Str())
    price_ranges = fields.List(fields.Dict())
    locations = fields.List(fields.Dict())
    brands = fields.List(fields.Str())
    years = fields.List(fields.Int())

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculer la distance entre deux points en kilomètres (formule de Haversine)"""
    if not all([lat1, lon1, lat2, lon2]):
        return None
    
    # Rayon de la Terre en kilomètres
    R = 6371.0
    
    # Convertir en radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Différences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Formule de Haversine
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def build_search_query(filters):
    """Construire la requête de recherche avec filtres"""
    query = db.session.query(Listing).options(
        joinedload(Listing.category),
        joinedload(Listing.user),
        joinedload(Listing.images)
    )
    
    # Filtrer uniquement les annonces actives
    query = query.filter(Listing.status == 'active')
    
    # Recherche textuelle
    if filters.get('query'):
        search_term = filters['query'].strip()
        if search_term:
            # Recherche dans le titre, description et tags
            search_filter = or_(
                Listing.title.ilike(f'%{search_term}%'),
                Listing.description.ilike(f'%{search_term}%'),
                Listing.brand.ilike(f'%{search_term}%'),
                Listing.model.ilike(f'%{search_term}%'),
                func.json_extract(Listing.tags, '$').ilike(f'%{search_term}%')
            )
            query = query.filter(search_filter)
    
    # Filtre par catégorie
    if filters.get('category_id'):
        query = query.filter(Listing.category_id == filters['category_id'])
    
    # Filtre par type d'annonce
    if filters.get('listing_type') and filters['listing_type'] != 'both':
        query = query.filter(Listing.listing_type == filters['listing_type'])
    
    # Filtre par condition
    if filters.get('condition'):
        query = query.filter(Listing.condition.in_(filters['condition']))
    
    # Filtre par prix
    if filters.get('min_price') is not None:
        query = query.filter(Listing.estimated_value >= filters['min_price'])
    if filters.get('max_price') is not None:
        query = query.filter(Listing.estimated_value <= filters['max_price'])
    
    # Filtre par devise
    if filters.get('currency'):
        query = query.filter(Listing.currency == filters['currency'])
    
    # Filtre par localisation
    if filters.get('city'):
        query = query.filter(Listing.city.ilike(f'%{filters["city"]}%'))
    if filters.get('postal_code'):
        query = query.filter(Listing.postal_code == filters['postal_code'])
    if filters.get('country'):
        query = query.filter(Listing.country == filters['country'])
    
    # Filtre géolocalisé avec rayon
    if all([filters.get('latitude'), filters.get('longitude'), filters.get('radius_km')]):
        lat, lon, radius = filters['latitude'], filters['longitude'], filters['radius_km']
        
        # Calculer les bornes approximatives pour optimiser la requête
        lat_delta = radius / 111.0  # 1 degré ≈ 111 km
        lon_delta = radius / (111.0 * math.cos(math.radians(lat)))
        
        query = query.filter(
            and_(
                Listing.latitude.isnot(None),
                Listing.longitude.isnot(None),
                Listing.latitude.between(lat - lat_delta, lat + lat_delta),
                Listing.longitude.between(lon - lon_delta, lon + lon_delta)
            )
        )
    
    # Filtre par type d'échange
    if filters.get('exchange_type'):
        if filters['exchange_type'] == 'both':
            query = query.filter(Listing.exchange_type.in_(['direct', 'chain', 'both']))
        else:
            query = query.filter(
                or_(
                    Listing.exchange_type == filters['exchange_type'],
                    Listing.exchange_type == 'both'
                )
            )
    
    # Filtre par marque
    if filters.get('brand'):
        query = query.filter(Listing.brand.ilike(f'%{filters["brand"]}%'))
    
    # Filtre par modèle
    if filters.get('model'):
        query = query.filter(Listing.model.ilike(f'%{filters["model"]}%'))
    
    # Filtre par année
    if filters.get('year_min'):
        query = query.filter(Listing.year >= filters['year_min'])
    if filters.get('year_max'):
        query = query.filter(Listing.year <= filters['year_max'])
    
    return query

def apply_sorting(query, sort_by, user_lat=None, user_lon=None):
    """Appliquer le tri à la requête"""
    if sort_by == 'date':
        query = query.order_by(Listing.created_at.desc())
    elif sort_by == 'price_asc':
        query = query.order_by(Listing.estimated_value.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Listing.estimated_value.desc())
    elif sort_by == 'distance' and user_lat and user_lon:
        # Tri par distance (nécessite un calcul post-requête)
        query = query.order_by(Listing.created_at.desc())  # Tri par défaut
    else:  # relevance par défaut
        query = query.order_by(
            Listing.is_featured.desc(),
            Listing.views_count.desc(),
            Listing.created_at.desc()
        )
    
    return query

@search_bp.route('/search', methods=['GET'])
@limiter.limit("30 per minute")
def search_listings():
    """
    Recherche avancée d'annonces avec filtres multiples
    """
    try:
        # Valider les paramètres
        schema = SearchSchema()
        filters = schema.load(request.args)
        
        # Construire la requête de base
        query = build_search_query(filters)
        
        # Récupérer les coordonnées de l'utilisateur si disponibles
        user_lat = filters.get('latitude')
        user_lon = filters.get('longitude')
        
        # Appliquer le tri
        sort_by = filters.get('sort_by', 'relevance')
        query = apply_sorting(query, sort_by, user_lat, user_lon)
        
        # Pagination
        page = filters.get('page', 1)
        per_page = min(filters.get('per_page', 20), 50)
        
        # Exécuter la requête
        paginated_results = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Traiter les résultats
        listings = []
        for listing in paginated_results.items:
            listing_data = {
                'id': listing.id,
                'title': listing.title,
                'description': listing.description[:200] + '...' if len(listing.description) > 200 else listing.description,
                'category': {
                    'id': listing.category.id,
                    'name': listing.category.name,
                    'slug': listing.category.slug,
                    'icon': listing.category.icon
                } if listing.category else None,
                'user': {
                    'id': listing.user.id,
                    'username': listing.user.username,
                    'trust_score': listing.user.trust_score,
                    'city': listing.user.city
                } if listing.user else None,
                'listing_type': listing.listing_type,
                'condition': listing.condition,
                'brand': listing.brand,
                'model': listing.model,
                'year': listing.year,
                'estimated_value': listing.estimated_value,
                'currency': listing.currency,
                'city': listing.city,
                'postal_code': listing.postal_code,
                'country': listing.country,
                'exchange_type': listing.exchange_type,
                'views_count': listing.views_count,
                'likes_count': listing.likes_count,
                'created_at': listing.created_at.isoformat(),
                'images': [
                    {
                        'id': img.id,
                        'url': img.url,
                        'alt': img.alt_text,
                        'is_primary': img.is_primary
                    } for img in listing.images[:3]  # Limiter à 3 images
                ],
                'tags': listing.tags or []
            }
            
            # Calculer la distance si les coordonnées sont disponibles
            if user_lat and user_lon and listing.latitude and listing.longitude:
                distance = calculate_distance(
                    user_lat, user_lon,
                    listing.latitude, listing.longitude
                )
                if distance is not None:
                    listing_data['distance_km'] = round(distance, 1)
            
            listings.append(listing_data)
        
        # Trier par distance si demandé
        if sort_by == 'distance' and user_lat and user_lon:
            listings.sort(key=lambda x: x.get('distance_km', float('inf')))
        
        # Statistiques de recherche
        total_results = paginated_results.total
        total_pages = paginated_results.pages
        
        return jsonify({
            'success': True,
            'data': {
                'listings': listings,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total_results,
                    'pages': total_pages,
                    'has_next': paginated_results.has_next,
                    'has_prev': paginated_results.has_prev
                },
                'filters_applied': filters,
                'search_stats': {
                    'total_found': total_results,
                    'query_time': '< 100ms'  # Placeholder
                }
            }
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Paramètres de recherche invalides',
            'details': e.messages
        }), 400
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la recherche: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur'
        }), 500

@search_bp.route('/search/suggestions', methods=['GET'])
@limiter.limit("50 per minute")
def search_suggestions():
    """
    Suggestions de recherche basées sur les annonces existantes
    """
    try:
        query = request.args.get('q', '').strip()
        if len(query) < 2:
            return jsonify({
                'success': True,
                'data': {
                    'suggestions': []
                }
            }), 200
        
        # Suggestions basées sur les titres d'annonces
        title_suggestions = db.session.query(Listing.title).filter(
            and_(
                Listing.status == 'active',
                Listing.title.ilike(f'%{query}%')
            )
        ).distinct().limit(5).all()
        
        # Suggestions basées sur les marques
        brand_suggestions = db.session.query(Listing.brand).filter(
            and_(
                Listing.status == 'active',
                Listing.brand.isnot(None),
                Listing.brand.ilike(f'%{query}%')
            )
        ).distinct().limit(3).all()
        
        # Suggestions basées sur les modèles
        model_suggestions = db.session.query(Listing.model).filter(
            and_(
                Listing.status == 'active',
                Listing.model.isnot(None),
                Listing.model.ilike(f'%{query}%')
            )
        ).distinct().limit(3).all()
        
        # Combiner et formater les suggestions
        suggestions = []
        
        for title, in title_suggestions:
            suggestions.append({
                'type': 'title',
                'text': title,
                'category': 'Titres d\'annonces'
            })
        
        for brand, in brand_suggestions:
            suggestions.append({
                'type': 'brand',
                'text': brand,
                'category': 'Marques'
            })
        
        for model, in model_suggestions:
            suggestions.append({
                'type': 'model',
                'text': model,
                'category': 'Modèles'
            })
        
        return jsonify({
            'success': True,
            'data': {
                'suggestions': suggestions[:10]  # Limiter à 10 suggestions
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la génération des suggestions: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur'
        }), 500

@search_bp.route('/search/filters', methods=['GET'])
def get_search_filters():
    """
    Récupérer les filtres disponibles pour la recherche
    """
    try:
        # Catégories actives
        categories = db.session.query(ListingCategory).filter(
            ListingCategory.is_active == True
        ).order_by(ListingCategory.sort_order).all()
        
        # Conditions disponibles
        conditions = [condition.value for condition in Condition]
        
        # Plages de prix populaires
        price_ranges = [
            {'label': 'Moins de 50 CHF', 'min': 0, 'max': 50},
            {'label': '50 - 100 CHF', 'min': 50, 'max': 100},
            {'label': '100 - 200 CHF', 'min': 100, 'max': 200},
            {'label': '200 - 500 CHF', 'min': 200, 'max': 500},
            {'label': '500 - 1000 CHF', 'min': 500, 'max': 1000},
            {'label': 'Plus de 1000 CHF', 'min': 1000, 'max': None}
        ]
        
        # Villes populaires
        cities = db.session.query(Listing.city).filter(
            and_(
                Listing.status == 'active',
                Listing.city.isnot(None)
            )
        ).distinct().limit(20).all()
        
        # Marques populaires
        brands = db.session.query(Listing.brand).filter(
            and_(
                Listing.status == 'active',
                Listing.brand.isnot(None)
            )
        ).distinct().limit(20).all()
        
        return jsonify({
            'success': True,
            'data': {
                'categories': [
                    {
                        'id': cat.id,
                        'name': cat.name,
                        'slug': cat.slug,
                        'icon': cat.icon,
                        'description': cat.description
                    } for cat in categories
                ],
                'conditions': conditions,
                'price_ranges': price_ranges,
                'cities': [city[0] for city in cities if city[0]],
                'brands': [brand[0] for brand in brands if brand[0]],
                'currencies': ['CHF', 'EUR', 'USD'],
                'exchange_types': ['direct', 'chain', 'both']
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des filtres: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur'
        }), 500

@search_bp.route('/search/trending', methods=['GET'])
def get_trending_searches():
    """
    Récupérer les recherches tendances
    """
    try:
        # Pour l'instant, retourner des recherches populaires statiques
        # Dans une version future, cela pourrait être basé sur les logs de recherche
        trending = [
            {'query': 'iPhone', 'count': 45},
            {'query': 'vélo', 'count': 38},
            {'query': 'meubles', 'count': 32},
            {'query': 'voiture', 'count': 28},
            {'query': 'livres', 'count': 25},
            {'query': 'vêtements', 'count': 22},
            {'query': 'électronique', 'count': 20},
            {'query': 'sport', 'count': 18}
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'trending': trending
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des tendances: {e}")
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur'
        }), 500