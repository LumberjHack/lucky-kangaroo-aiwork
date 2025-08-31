"""
Lucky Kangaroo - Service de Géolocalisation Complet
Service pour la gestion de la géolocalisation et calculs de distance
"""

import math
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Location:
    """Classe pour représenter une localisation"""
    latitude: float
    longitude: float
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    
    def to_dict(self):
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'address': self.address,
            'city': self.city,
            'postal_code': self.postal_code,
            'country': self.country
        }

@dataclass
class DistanceResult:
    """Résultat de calcul de distance"""
    distance_km: float
    distance_miles: float
    bearing: float
    travel_time_minutes: Optional[int] = None
    
    def to_dict(self):
        return {
            'distance_km': round(self.distance_km, 2),
            'distance_miles': round(self.distance_miles, 2),
            'bearing': round(self.bearing, 2),
            'travel_time_minutes': self.travel_time_minutes
        }

class GeolocationService:
    """Service de géolocalisation avancé"""
    
    def __init__(self):
        self.earth_radius_km = 6371.0
        self.earth_radius_miles = 3959.0
        
        # Coordonnées des principales villes françaises pour les tests
        self.major_cities = {
            'paris': {'lat': 48.8566, 'lng': 2.3522, 'name': 'Paris'},
            'lyon': {'lat': 45.7640, 'lng': 4.8357, 'name': 'Lyon'},
            'marseille': {'lat': 43.2965, 'lng': 5.3698, 'name': 'Marseille'},
            'toulouse': {'lat': 43.6047, 'lng': 1.4442, 'name': 'Toulouse'},
            'nice': {'lat': 43.7102, 'lng': 7.2620, 'name': 'Nice'},
            'nantes': {'lat': 47.2184, 'lng': -1.5536, 'name': 'Nantes'},
            'strasbourg': {'lat': 48.5734, 'lng': 7.7521, 'name': 'Strasbourg'},
            'montpellier': {'lat': 43.6110, 'lng': 3.8767, 'name': 'Montpellier'},
            'bordeaux': {'lat': 44.8378, 'lng': -0.5792, 'name': 'Bordeaux'},
            'lille': {'lat': 50.6292, 'lng': 3.0573, 'name': 'Lille'}
        }
    
    def calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> DistanceResult:
        """
        Calcule la distance entre deux points géographiques en utilisant la formule Haversine
        """
        # Conversion en radians
        lat1_rad = math.radians(lat1)
        lng1_rad = math.radians(lng1)
        lat2_rad = math.radians(lat2)
        lng2_rad = math.radians(lng2)
        
        # Différences
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        
        # Formule Haversine
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        
        # Distance en kilomètres et miles
        distance_km = self.earth_radius_km * c
        distance_miles = self.earth_radius_miles * c
        
        # Calcul du bearing (direction)
        bearing = self.calculate_bearing(lat1, lng1, lat2, lng2)
        
        # Estimation du temps de trajet (vitesse moyenne 50 km/h)
        travel_time_minutes = int((distance_km / 50) * 60) if distance_km > 0 else 0
        
        return DistanceResult(
            distance_km=distance_km,
            distance_miles=distance_miles,
            bearing=bearing,
            travel_time_minutes=travel_time_minutes
        )
    
    def calculate_bearing(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calcule la direction (bearing) entre deux points
        """
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlng_rad = math.radians(lng2 - lng1)
        
        y = math.sin(dlng_rad) * math.cos(lat2_rad)
        x = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlng_rad))
        
        bearing_rad = math.atan2(y, x)
        bearing_deg = math.degrees(bearing_rad)
        
        # Normaliser entre 0 et 360 degrés
        return (bearing_deg + 360) % 360
    
    def get_direction_name(self, bearing: float) -> str:
        """
        Convertit un bearing en nom de direction
        """
        directions = [
            "Nord", "Nord-Nord-Est", "Nord-Est", "Est-Nord-Est",
            "Est", "Est-Sud-Est", "Sud-Est", "Sud-Sud-Est",
            "Sud", "Sud-Sud-Ouest", "Sud-Ouest", "Ouest-Sud-Ouest",
            "Ouest", "Ouest-Nord-Ouest", "Nord-Ouest", "Nord-Nord-Ouest"
        ]
        
        index = int((bearing + 11.25) / 22.5) % 16
        return directions[index]
    
    def find_nearby_points(self, center_lat: float, center_lng: float, 
                          points: List[Dict], max_distance_km: float = 50) -> List[Dict]:
        """
        Trouve les points à proximité d'un centre dans un rayon donné
        """
        nearby_points = []
        
        for point in points:
            if 'latitude' in point and 'longitude' in point:
                distance_result = self.calculate_distance(
                    center_lat, center_lng,
                    point['latitude'], point['longitude']
                )
                
                if distance_result.distance_km <= max_distance_km:
                    point_with_distance = point.copy()
                    point_with_distance['distance'] = distance_result.to_dict()
                    point_with_distance['direction'] = self.get_direction_name(distance_result.bearing)
                    nearby_points.append(point_with_distance)
        
        # Trier par distance
        nearby_points.sort(key=lambda p: p['distance']['distance_km'])
        
        return nearby_points
    
    def geocode_address(self, address: str) -> Optional[Location]:
        """
        Géocode une adresse en coordonnées (simulation avec villes principales)
        En production, utiliser une vraie API comme Google Maps, OpenStreetMap Nominatim, etc.
        """
        address_lower = address.lower().strip()
        
        # Recherche dans les villes principales
        for city_key, city_data in self.major_cities.items():
            if city_key in address_lower or city_data['name'].lower() in address_lower:
                return Location(
                    latitude=city_data['lat'],
                    longitude=city_data['lng'],
                    city=city_data['name'],
                    country='France',
                    address=address
                )
        
        # Simulation pour d'autres adresses (coordonnées aléatoires autour de Paris)
        import random
        base_lat = 48.8566
        base_lng = 2.3522
        
        # Variation aléatoire dans un rayon de ~100km autour de Paris
        lat_variation = random.uniform(-0.9, 0.9)  # ~100km
        lng_variation = random.uniform(-1.2, 1.2)  # ~100km
        
        return Location(
            latitude=base_lat + lat_variation,
            longitude=base_lng + lng_variation,
            address=address,
            city="Ville simulée",
            country='France'
        )
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Location]:
        """
        Géocode inverse : coordonnées vers adresse (simulation)
        """
        # Trouver la ville la plus proche
        closest_city = None
        min_distance = float('inf')
        
        for city_data in self.major_cities.values():
            distance_result = self.calculate_distance(
                latitude, longitude,
                city_data['lat'], city_data['lng']
            )
            
            if distance_result.distance_km < min_distance:
                min_distance = distance_result.distance_km
                closest_city = city_data
        
        if closest_city and min_distance < 50:  # Dans un rayon de 50km
            return Location(
                latitude=latitude,
                longitude=longitude,
                city=closest_city['name'],
                country='France',
                address=f"Près de {closest_city['name']}"
            )
        
        # Adresse générique si pas de ville proche
        return Location(
            latitude=latitude,
            longitude=longitude,
            address=f"Latitude: {latitude:.4f}, Longitude: {longitude:.4f}",
            country='France'
        )
    
    def get_bounding_box(self, center_lat: float, center_lng: float, 
                        radius_km: float) -> Dict[str, float]:
        """
        Calcule une bounding box autour d'un point
        """
        # Approximation : 1 degré de latitude ≈ 111 km
        # 1 degré de longitude ≈ 111 km * cos(latitude)
        
        lat_delta = radius_km / 111.0
        lng_delta = radius_km / (111.0 * math.cos(math.radians(center_lat)))
        
        return {
            'north': center_lat + lat_delta,
            'south': center_lat - lat_delta,
            'east': center_lng + lng_delta,
            'west': center_lng - lng_delta
        }
    
    def is_point_in_bounding_box(self, lat: float, lng: float, 
                                bounding_box: Dict[str, float]) -> bool:
        """
        Vérifie si un point est dans une bounding box
        """
        return (bounding_box['south'] <= lat <= bounding_box['north'] and
                bounding_box['west'] <= lng <= bounding_box['east'])
    
    def get_area_statistics(self, points: List[Dict], center_lat: float, 
                           center_lng: float, radius_km: float) -> Dict:
        """
        Calcule des statistiques pour une zone géographique
        """
        nearby_points = self.find_nearby_points(center_lat, center_lng, points, radius_km)
        
        if not nearby_points:
            return {
                'total_points': 0,
                'average_distance_km': 0,
                'closest_distance_km': 0,
                'farthest_distance_km': 0,
                'density_per_km2': 0
            }
        
        distances = [p['distance']['distance_km'] for p in nearby_points]
        area_km2 = math.pi * (radius_km ** 2)
        
        return {
            'total_points': len(nearby_points),
            'average_distance_km': round(sum(distances) / len(distances), 2),
            'closest_distance_km': round(min(distances), 2),
            'farthest_distance_km': round(max(distances), 2),
            'density_per_km2': round(len(nearby_points) / area_km2, 2),
            'area_km2': round(area_km2, 2)
        }
    
    def suggest_meeting_points(self, lat1: float, lng1: float, 
                              lat2: float, lng2: float) -> List[Dict]:
        """
        Suggère des points de rencontre entre deux positions
        """
        # Point milieu
        mid_lat = (lat1 + lat2) / 2
        mid_lng = (lng1 + lng2) / 2
        
        # Distance totale
        total_distance = self.calculate_distance(lat1, lng1, lat2, lng2)
        
        meeting_points = []
        
        # Point milieu exact
        meeting_points.append({
            'name': 'Point milieu',
            'latitude': mid_lat,
            'longitude': mid_lng,
            'description': 'Point équidistant entre les deux positions',
            'distance_from_1': round(total_distance.distance_km / 2, 2),
            'distance_from_2': round(total_distance.distance_km / 2, 2)
        })
        
        # Points à 1/3 et 2/3 du trajet
        for ratio, name in [(0.33, 'Plus proche du premier'), (0.67, 'Plus proche du second')]:
            point_lat = lat1 + (lat2 - lat1) * ratio
            point_lng = lng1 + (lng2 - lng1) * ratio
            
            dist_from_1 = self.calculate_distance(lat1, lng1, point_lat, point_lng)
            dist_from_2 = self.calculate_distance(lat2, lng2, point_lat, point_lng)
            
            meeting_points.append({
                'name': name,
                'latitude': point_lat,
                'longitude': point_lng,
                'description': f'Point à {int(ratio*100)}% du trajet',
                'distance_from_1': round(dist_from_1.distance_km, 2),
                'distance_from_2': round(dist_from_2.distance_km, 2)
            })
        
        return meeting_points
    
    def get_travel_zones(self, center_lat: float, center_lng: float) -> List[Dict]:
        """
        Définit des zones de déplacement avec temps de trajet estimés
        """
        zones = [
            {'name': 'Très proche', 'radius_km': 5, 'color': '#22c55e', 'travel_time': '< 15 min'},
            {'name': 'Proche', 'radius_km': 15, 'color': '#84cc16', 'travel_time': '15-30 min'},
            {'name': 'Modéré', 'radius_km': 30, 'color': '#eab308', 'travel_time': '30-60 min'},
            {'name': 'Éloigné', 'radius_km': 50, 'color': '#f97316', 'travel_time': '1-2h'},
            {'name': 'Très éloigné', 'radius_km': 100, 'color': '#ef4444', 'travel_time': '> 2h'}
        ]
        
        for zone in zones:
            zone['center'] = {'latitude': center_lat, 'longitude': center_lng}
            zone['bounding_box'] = self.get_bounding_box(center_lat, center_lng, zone['radius_km'])
        
        return zones
    
    def validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """
        Valide des coordonnées géographiques
        """
        return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)
    
    def format_coordinates(self, latitude: float, longitude: float, 
                          format_type: str = 'decimal') -> str:
        """
        Formate des coordonnées selon différents formats
        """
        if not self.validate_coordinates(latitude, longitude):
            return "Coordonnées invalides"
        
        if format_type == 'decimal':
            return f"{latitude:.6f}, {longitude:.6f}"
        
        elif format_type == 'dms':  # Degrees, Minutes, Seconds
            def to_dms(coord, is_latitude=True):
                abs_coord = abs(coord)
                degrees = int(abs_coord)
                minutes = int((abs_coord - degrees) * 60)
                seconds = ((abs_coord - degrees) * 60 - minutes) * 60
                
                if is_latitude:
                    direction = 'N' if coord >= 0 else 'S'
                else:
                    direction = 'E' if coord >= 0 else 'W'
                
                return f"{degrees}°{minutes}'{seconds:.2f}\"{direction}"
            
            lat_dms = to_dms(latitude, True)
            lng_dms = to_dms(longitude, False)
            return f"{lat_dms}, {lng_dms}"
        
        elif format_type == 'utm':
            # Simulation UTM (en production, utiliser une vraie conversion)
            return f"UTM: Zone 31N, {int(longitude * 100000)}, {int(latitude * 100000)}"
        
        return f"{latitude}, {longitude}"
    
    def get_location_info(self, latitude: float, longitude: float) -> Dict:
        """
        Retourne des informations complètes sur une localisation
        """
        if not self.validate_coordinates(latitude, longitude):
            return {'error': 'Coordonnées invalides'}
        
        location = self.reverse_geocode(latitude, longitude)
        travel_zones = self.get_travel_zones(latitude, longitude)
        
        return {
            'coordinates': {
                'latitude': latitude,
                'longitude': longitude,
                'decimal': self.format_coordinates(latitude, longitude, 'decimal'),
                'dms': self.format_coordinates(latitude, longitude, 'dms'),
                'utm': self.format_coordinates(latitude, longitude, 'utm')
            },
            'location': location.to_dict() if location else None,
            'travel_zones': travel_zones,
            'bounding_boxes': {
                f'{zone["name"].lower().replace(" ", "_")}': zone['bounding_box'] 
                for zone in travel_zones
            },
            'timestamp': datetime.utcnow().isoformat()
        }

# Instance globale du service
geolocation_service = GeolocationService()

# Fonctions utilitaires pour l'API
def calculate_distance_api(lat1: float, lng1: float, lat2: float, lng2: float) -> Dict:
    """API wrapper pour le calcul de distance"""
    try:
        result = geolocation_service.calculate_distance(lat1, lng1, lat2, lng2)
        return {
            'success': True,
            'data': result.to_dict()
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def find_nearby_api(center_lat: float, center_lng: float, 
                   points: List[Dict], max_distance_km: float = 50) -> Dict:
    """API wrapper pour la recherche de proximité"""
    try:
        nearby_points = geolocation_service.find_nearby_points(
            center_lat, center_lng, points, max_distance_km
        )
        
        statistics = geolocation_service.get_area_statistics(
            points, center_lat, center_lng, max_distance_km
        )
        
        return {
            'success': True,
            'data': {
                'nearby_points': nearby_points,
                'statistics': statistics,
                'search_params': {
                    'center_latitude': center_lat,
                    'center_longitude': center_lng,
                    'max_distance_km': max_distance_km
                }
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def geocode_api(address: str) -> Dict:
    """API wrapper pour le géocodage"""
    try:
        location = geolocation_service.geocode_address(address)
        return {
            'success': True,
            'data': location.to_dict() if location else None
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def reverse_geocode_api(latitude: float, longitude: float) -> Dict:
    """API wrapper pour le géocodage inverse"""
    try:
        location = geolocation_service.reverse_geocode(latitude, longitude)
        return {
            'success': True,
            'data': location.to_dict() if location else None
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def suggest_meeting_points_api(lat1: float, lng1: float, lat2: float, lng2: float) -> Dict:
    """API wrapper pour la suggestion de points de rencontre"""
    try:
        meeting_points = geolocation_service.suggest_meeting_points(lat1, lng1, lat2, lng2)
        return {
            'success': True,
            'data': meeting_points
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

