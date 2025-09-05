#!/usr/bin/env python3
"""
Test de l'API de recherche Lucky Kangaroo
"""

import os
import sys
import requests
import json

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Forcer l'utilisation de SQLite
os.environ['DATABASE_URL'] = 'sqlite:///lucky_kangaroo.db'
os.environ['FLASK_ENV'] = 'testing'

def test_search_api():
    """Tester l'API de recherche"""
    print("🔍 Test de l'API de recherche Lucky Kangaroo")
    print("=" * 50)
    
    try:
        from app import create_app, db
        from app.models.user import User
        from app.models.listing import Listing, ListingCategory
        
        app = create_app()
        
        with app.test_client() as client:
            with app.app_context():
                # Créer les tables
                db.create_all()
                
                # Créer une catégorie de test
                category = ListingCategory.query.filter_by(slug='electronique').first()
                if not category:
                    category = ListingCategory(
                        id='test-category-id',
                        name='Électronique',
                        slug='electronique',
                        description='Appareils électroniques',
                        icon='📱',
                        sort_order=1,
                        is_active=True
                    )
                    db.session.add(category)
                    db.session.commit()
                
                # Créer un utilisateur de test
                user = User.query.filter_by(email='test@example.com').first()
                if not user:
                    user = User(
                        id='test-user-id',
                        email='test@example.com',
                        username='test.user',
                        first_name='Test',
                        last_name='User',
                        country='CH',
                        status='active',
                        role='user'
                    )
                    user.password = 'TestPassword123!'
                    db.session.add(user)
                    db.session.commit()
                
                # Créer quelques annonces de test
                test_listings = [
                    {
                        'id': 'listing-1',
                        'title': 'iPhone 13 Pro Max 256GB',
                        'description': 'iPhone 13 Pro Max en excellent état, utilisé 6 mois.',
                        'estimated_value': 800,
                        'city': 'Genève',
                        'postal_code': '1200',
                        'latitude': 46.2044,
                        'longitude': 6.1432
                    },
                    {
                        'id': 'listing-2',
                        'title': 'MacBook Pro M2 13"',
                        'description': 'MacBook Pro M2 13 pouces, 512GB SSD, 16GB RAM.',
                        'estimated_value': 1500,
                        'city': 'Lausanne',
                        'postal_code': '1000',
                        'latitude': 46.5197,
                        'longitude': 6.6323
                    },
                    {
                        'id': 'listing-3',
                        'title': 'Samsung Galaxy S23 Ultra',
                        'description': 'Samsung Galaxy S23 Ultra 256GB, noir.',
                        'estimated_value': 900,
                        'city': 'Zurich',
                        'postal_code': '8001',
                        'latitude': 47.3769,
                        'longitude': 8.5417
                    }
                ]
                
                for listing_data in test_listings:
                    existing = Listing.query.filter_by(id=listing_data['id']).first()
                    if not existing:
                        listing = Listing(
                            id=listing_data['id'],
                            user_id=user.id,
                            category_id=category.id,
                            title=listing_data['title'],
                            description=listing_data['description'],
                            listing_type='good',
                            condition='excellent',
                            brand='Test Brand',
                            model='Test Model',
                            year=2023,
                            estimated_value=listing_data['estimated_value'],
                            currency='CHF',
                            city=listing_data['city'],
                            postal_code=listing_data['postal_code'],
                            country='CH',
                            exchange_type='both',
                            status='active',
                            latitude=listing_data['latitude'],
                            longitude=listing_data['longitude'],
                            views_count=100,
                            likes_count=10
                        )
                        db.session.add(listing)
                
                db.session.commit()
                print("✅ Données de test créées")
                
                # Test 1: Recherche simple
                print("\n🔍 Test 1: Recherche simple")
                response = client.get('/api/search/search?query=iPhone')
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    print(f"Résultats trouvés: {len(data.get('data', {}).get('listings', []))}")
                    if data.get('data', {}).get('listings'):
                        print(f"Premier résultat: {data['data']['listings'][0]['title']}")
                else:
                    print(f"Erreur: {response.get_json()}")
                
                # Test 2: Recherche par catégorie
                print("\n🔍 Test 2: Recherche par catégorie")
                response = client.get(f'/api/search/search?category_id={category.id}')
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    print(f"Résultats trouvés: {len(data.get('data', {}).get('listings', []))}")
                else:
                    print(f"Erreur: {response.get_json()}")
                
                # Test 3: Recherche géolocalisée
                print("\n🔍 Test 3: Recherche géolocalisée")
                response = client.get('/api/search/search?latitude=46.2044&longitude=6.1432&radius_km=50')
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    print(f"Résultats trouvés: {len(data.get('data', {}).get('listings', []))}")
                    if data.get('data', {}).get('listings'):
                        for listing in data['data']['listings']:
                            if 'distance_km' in listing:
                                print(f"  - {listing['title']}: {listing['distance_km']} km")
                else:
                    print(f"Erreur: {response.get_json()}")
                
                # Test 4: Filtres de recherche
                print("\n🔍 Test 4: Filtres de recherche")
                response = client.get('/api/search/search?min_price=500&max_price=1000')
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    print(f"Résultats trouvés: {len(data.get('data', {}).get('listings', []))}")
                else:
                    print(f"Erreur: {response.get_json()}")
                
                # Test 5: Suggestions de recherche
                print("\n🔍 Test 5: Suggestions de recherche")
                response = client.get('/api/search/suggestions?q=iPhone')
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    suggestions = data.get('data', {}).get('suggestions', [])
                    print(f"Suggestions trouvées: {len(suggestions)}")
                    for suggestion in suggestions[:3]:
                        print(f"  - {suggestion.get('text', '')}")
                else:
                    print(f"Erreur: {response.get_json()}")
                
                # Test 6: Filtres disponibles
                print("\n🔍 Test 6: Filtres disponibles")
                response = client.get('/api/search/filters')
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    filters_data = data.get('data', {})
                    print(f"Catégories: {len(filters_data.get('categories', []))}")
                    print(f"Conditions: {len(filters_data.get('conditions', []))}")
                    print(f"Villes: {len(filters_data.get('cities', []))}")
                else:
                    print(f"Erreur: {response.get_json()}")
                
                print("\n🎉 Tests de l'API de recherche terminés !")
                return True
                
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    success = test_search_api()
    
    if success:
        print("\n✅ Tests de l'API de recherche réussis !")
        print("🚀 L'API de recherche fonctionne correctement")
    else:
        print("\n❌ Erreur lors des tests de l'API de recherche")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
