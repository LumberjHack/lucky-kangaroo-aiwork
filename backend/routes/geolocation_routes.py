"""
Lucky Kangaroo - Routes API Géolocalisation
Routes Flask pour les services de géolocalisation
"""

from flask import Blueprint, request, jsonify
from services.geolocation_service import (
    geolocation_service,
    calculate_distance_api,
    find_nearby_api,
    geocode_api,
    reverse_geocode_api,
    suggest_meeting_points_api
)

# Création du blueprint
geolocation_bp = Blueprint('geolocation', __name__, url_prefix='/api/geolocation')

@geolocation_bp.route('/health', methods=['GET'])
def health_check():
    """Vérification de santé du service de géolocalisation"""
    return jsonify({
        'status': 'healthy',
        'service': 'geolocation',
        'version': '1.0.0',
        'features': [
            'distance_calculation',
            'nearby_search',
            'geocoding',
            'reverse_geocoding',
            'meeting_points_suggestion',
            'travel_zones',
            'area_statistics'
        ]
    })

@geolocation_bp.route('/distance', methods=['POST'])
def calculate_distance():
    """
    Calcule la distance entre deux points
    
    Body JSON:
    {
        "from": {"latitude": 48.8566, "longitude": 2.3522},
        "to": {"latitude": 45.7640, "longitude": 4.8357}
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'from' not in data or 'to' not in data:
            return jsonify({
                'success': False,
                'error': 'Format invalide. Requis: {"from": {"latitude": X, "longitude": Y}, "to": {"latitude": X, "longitude": Y}}'
            }), 400
        
        from_point = data['from']
        to_point = data['to']
        
        # Validation des coordonnées
        required_fields = ['latitude', 'longitude']
        for point_name, point in [('from', from_point), ('to', to_point)]:
            for field in required_fields:
                if field not in point:
                    return jsonify({
                        'success': False,
                        'error': f'Champ manquant: {point_name}.{field}'
                    }), 400
        
        result = calculate_distance_api(
            from_point['latitude'], from_point['longitude'],
            to_point['latitude'], to_point['longitude']
        )
        
        if result['success']:
            # Ajouter des informations contextuelles
            result['data']['from'] = from_point
            result['data']['to'] = to_point
            result['data']['direction'] = geolocation_service.get_direction_name(result['data']['bearing'])
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur interne: {str(e)}'
        }), 500

@geolocation_bp.route('/nearby', methods=['POST'])
def find_nearby():
    """
    Trouve les points à proximité d'un centre
    
    Body JSON:
    {
        "center": {"latitude": 48.8566, "longitude": 2.3522},
        "points": [
            {"id": 1, "latitude": 48.8606, "longitude": 2.3376, "name": "Point 1"},
            {"id": 2, "latitude": 48.8738, "longitude": 2.2950, "name": "Point 2"}
        ],
        "max_distance_km": 10
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'center' not in data or 'points' not in data:
            return jsonify({
                'success': False,
                'error': 'Format invalide. Requis: {"center": {"latitude": X, "longitude": Y}, "points": [...]}'
            }), 400
        
        center = data['center']
        points = data['points']
        max_distance_km = data.get('max_distance_km', 50)
        
        # Validation du centre
        if 'latitude' not in center or 'longitude' not in center:
            return jsonify({
                'success': False,
                'error': 'Centre invalide. Requis: {"latitude": X, "longitude": Y}'
            }), 400
        
        # Validation des points
        if not isinstance(points, list):
            return jsonify({
                'success': False,
                'error': 'Points doit être une liste'
            }), 400
        
        result = find_nearby_api(
            center['latitude'], center['longitude'],
            points, max_distance_km
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur interne: {str(e)}'
        }), 500

@geolocation_bp.route('/geocode', methods=['POST'])
def geocode():
    """
    Géocode une adresse en coordonnées
    
    Body JSON:
    {
        "address": "Paris, France"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'address' not in data:
            return jsonify({
                'success': False,
                'error': 'Format invalide. Requis: {"address": "adresse"}'
            }), 400
        
        address = data['address'].strip()
        
        if not address:
            return jsonify({
                'success': False,
                'error': 'Adresse vide'
            }), 400
        
        result = geocode_api(address)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur interne: {str(e)}'
        }), 500

@geolocation_bp.route('/reverse-geocode', methods=['POST'])
def reverse_geocode():
    """
    Géocode inverse : coordonnées vers adresse
    
    Body JSON:
    {
        "latitude": 48.8566,
        "longitude": 2.3522
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({
                'success': False,
                'error': 'Format invalide. Requis: {"latitude": X, "longitude": Y}'
            }), 400
        
        latitude = data['latitude']
        longitude = data['longitude']
        
        # Validation des coordonnées
        if not geolocation_service.validate_coordinates(latitude, longitude):
            return jsonify({
                'success': False,
                'error': 'Coordonnées invalides'
            }), 400
        
        result = reverse_geocode_api(latitude, longitude)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur interne: {str(e)}'
        }), 500

@geolocation_bp.route('/meeting-points', methods=['POST'])
def suggest_meeting_points():
    """
    Suggère des points de rencontre entre deux positions
    
    Body JSON:
    {
        "person1": {"latitude": 48.8566, "longitude": 2.3522},
        "person2": {"latitude": 45.7640, "longitude": 4.8357}
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'person1' not in data or 'person2' not in data:
            return jsonify({
                'success': False,
                'error': 'Format invalide. Requis: {"person1": {"latitude": X, "longitude": Y}, "person2": {"latitude": X, "longitude": Y}}'
            }), 400
        
        person1 = data['person1']
        person2 = data['person2']
        
        # Validation des coordonnées
        for person_name, person in [('person1', person1), ('person2', person2)]:
            if 'latitude' not in person or 'longitude' not in person:
                return jsonify({
                    'success': False,
                    'error': f'Coordonnées manquantes pour {person_name}'
                }), 400
            
            if not geolocation_service.validate_coordinates(person['latitude'], person['longitude']):
                return jsonify({
                    'success': False,
                    'error': f'Coordonnées invalides pour {person_name}'
                }), 400
        
        result = suggest_meeting_points_api(
            person1['latitude'], person1['longitude'],
            person2['latitude'], person2['longitude']
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur interne: {str(e)}'
        }), 500

@geolocation_bp.route('/location-info', methods=['POST'])
def get_location_info():
    """
    Retourne des informations complètes sur une localisation
    
    Body JSON:
    {
        "latitude": 48.8566,
        "longitude": 2.3522
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({
                'success': False,
                'error': 'Format invalide. Requis: {"latitude": X, "longitude": Y}'
            }), 400
        
        latitude = data['latitude']
        longitude = data['longitude']
        
        # Validation des coordonnées
        if not geolocation_service.validate_coordinates(latitude, longitude):
            return jsonify({
                'success': False,
                'error': 'Coordonnées invalides'
            }), 400
        
        location_info = geolocation_service.get_location_info(latitude, longitude)
        
        return jsonify({
            'success': True,
            'data': location_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur interne: {str(e)}'
        }), 500

@geolocation_bp.route('/travel-zones', methods=['POST'])
def get_travel_zones():
    """
    Retourne les zones de déplacement autour d'un point
    
    Body JSON:
    {
        "center": {"latitude": 48.8566, "longitude": 2.3522}
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'center' not in data:
            return jsonify({
                'success': False,
                'error': 'Format invalide. Requis: {"center": {"latitude": X, "longitude": Y}}'
            }), 400
        
        center = data['center']
        
        if 'latitude' not in center or 'longitude' not in center:
            return jsonify({
                'success': False,
                'error': 'Centre invalide. Requis: {"latitude": X, "longitude": Y}'
            }), 400
        
        latitude = center['latitude']
        longitude = center['longitude']
        
        # Validation des coordonnées
        if not geolocation_service.validate_coordinates(latitude, longitude):
            return jsonify({
                'success': False,
                'error': 'Coordonnées invalides'
            }), 400
        
        travel_zones = geolocation_service.get_travel_zones(latitude, longitude)
        
        return jsonify({
            'success': True,
            'data': {
                'center': center,
                'zones': travel_zones
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur interne: {str(e)}'
        }), 500

@geolocation_bp.route('/validate-coordinates', methods=['POST'])
def validate_coordinates():
    """
    Valide des coordonnées géographiques
    
    Body JSON:
    {
        "latitude": 48.8566,
        "longitude": 2.3522
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({
                'success': False,
                'error': 'Format invalide. Requis: {"latitude": X, "longitude": Y}'
            }), 400
        
        latitude = data['latitude']
        longitude = data['longitude']
        
        is_valid = geolocation_service.validate_coordinates(latitude, longitude)
        
        result = {
            'success': True,
            'data': {
                'latitude': latitude,
                'longitude': longitude,
                'is_valid': is_valid,
                'formatted': {
                    'decimal': geolocation_service.format_coordinates(latitude, longitude, 'decimal'),
                    'dms': geolocation_service.format_coordinates(latitude, longitude, 'dms'),
                    'utm': geolocation_service.format_coordinates(latitude, longitude, 'utm')
                } if is_valid else None
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur interne: {str(e)}'
        }), 500

@geolocation_bp.route('/cities', methods=['GET'])
def get_major_cities():
    """
    Retourne la liste des principales villes disponibles
    """
    try:
        cities = []
        for city_key, city_data in geolocation_service.major_cities.items():
            cities.append({
                'key': city_key,
                'name': city_data['name'],
                'latitude': city_data['lat'],
                'longitude': city_data['lng']
            })
        
        return jsonify({
            'success': True,
            'data': {
                'cities': cities,
                'total': len(cities)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur interne: {str(e)}'
        }), 500

@geolocation_bp.route('/demo', methods=['GET'])
def demo():
    """
    Démonstration des capacités du service de géolocalisation
    """
    try:
        # Points de démonstration
        paris = {'latitude': 48.8566, 'longitude': 2.3522, 'name': 'Paris'}
        lyon = {'latitude': 45.7640, 'longitude': 4.8357, 'name': 'Lyon'}
        marseille = {'latitude': 43.2965, 'longitude': 5.3698, 'name': 'Marseille'}
        
        # Calcul de distances
        paris_lyon_distance = geolocation_service.calculate_distance(
            paris['latitude'], paris['longitude'],
            lyon['latitude'], lyon['longitude']
        )
        
        paris_marseille_distance = geolocation_service.calculate_distance(
            paris['latitude'], paris['longitude'],
            marseille['latitude'], marseille['longitude']
        )
        
        # Points de rencontre
        meeting_points = geolocation_service.suggest_meeting_points(
            paris['latitude'], paris['longitude'],
            lyon['latitude'], lyon['longitude']
        )
        
        # Zones de déplacement autour de Paris
        travel_zones = geolocation_service.get_travel_zones(
            paris['latitude'], paris['longitude']
        )
        
        return jsonify({
            'success': True,
            'data': {
                'demo_points': {
                    'paris': paris,
                    'lyon': lyon,
                    'marseille': marseille
                },
                'distances': {
                    'paris_to_lyon': paris_lyon_distance.to_dict(),
                    'paris_to_marseille': paris_marseille_distance.to_dict()
                },
                'meeting_points_paris_lyon': meeting_points,
                'travel_zones_from_paris': travel_zones,
                'capabilities': [
                    'Distance calculation with Haversine formula',
                    'Nearby points search with radius filtering',
                    'Geocoding and reverse geocoding',
                    'Meeting points suggestion',
                    'Travel zones with time estimates',
                    'Coordinate validation and formatting',
                    'Area statistics calculation'
                ]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur interne: {str(e)}'
        }), 500

# Gestion des erreurs
@geolocation_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint non trouvé',
        'available_endpoints': [
            'GET /api/geolocation/health',
            'POST /api/geolocation/distance',
            'POST /api/geolocation/nearby',
            'POST /api/geolocation/geocode',
            'POST /api/geolocation/reverse-geocode',
            'POST /api/geolocation/meeting-points',
            'POST /api/geolocation/location-info',
            'POST /api/geolocation/travel-zones',
            'POST /api/geolocation/validate-coordinates',
            'GET /api/geolocation/cities',
            'GET /api/geolocation/demo'
        ]
    }), 404

@geolocation_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Méthode HTTP non autorisée'
    }), 405

@geolocation_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Erreur interne du serveur'
    }), 500

