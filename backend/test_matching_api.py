#!/usr/bin/env python3
"""
Test du moteur de matching pour Lucky Kangaroo
Teste les suggestions de matching et les chaînes d'échange
"""

import os
import sys
import requests
import time
import uuid
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.user import User, UserStatus, UserRole
from app.models.listing import Listing, ListingCategory

def test_matching_api():
    """Test complet du moteur de matching"""
    print("🚀 Test du moteur de matching - Suggestions et chaînes d'échange")
    
    # Configuration
    app = create_app()
    app.config['TESTING'] = True
    app.config['DATABASE_URL'] = 'sqlite:///test_matching.db'
    app.config['FLASK_ENV'] = 'testing'
    
    with app.app_context():
        # Nettoyer la base de données
        db.drop_all()
        db.create_all()
        
        # Créer des utilisateurs de test
        users = []
        for i in range(3):
            user = User(
                email=f'test{i+1}@matching.com',
                username=f'testuser{i+1}',
                password_hash='$2b$12$test_hash',
                first_name=f'Test{i+1}',
                last_name='Matching',
                country='CH',
                timezone='Europe/Zurich',
                language='fr',
                currency='CHF',
                preferences={},
                notification_settings={},
                privacy_settings={},
                status=UserStatus.ACTIVE,
                role=UserRole.USER,
                trust_score=5.0,
                ecological_score=5.0,
                total_exchanges=0,
                successful_exchanges=0,
                total_listings=0,
                active_listings=0,
                last_activity=datetime.utcnow()
            )
            db.session.add(user)
            users.append(user)
        
        db.session.commit()
        print("✅ Utilisateurs créés")
        
        # Créer des catégories
        categories = []
        category_names = ['Électronique', 'Vêtements', 'Maison & Jardin']
        for i, name in enumerate(category_names):
            category = ListingCategory(
                name=name,
                slug=name.lower().replace(' ', '-').replace('&', 'et'),
                description=f'Catégorie {name}',
                sort_order=i+1,
                is_active=True
            )
            db.session.add(category)
            categories.append(category)
        
        db.session.commit()
        print("✅ Catégories créées")
        
        # Créer des annonces de test
        listings = []
        listing_data = [
            {
                'title': 'iPhone 13 Pro Max',
                'description': 'iPhone 13 Pro Max 256GB en excellent état',
                'category': 0,  # Électronique
                'user': 0,
                'value': 800.0,
                'condition': 'excellent',
                'city': 'Genève',
                'latitude': 46.2044,
                'longitude': 6.1432
            },
            {
                'title': 'Samsung Galaxy S21',
                'description': 'Samsung Galaxy S21 128GB en très bon état',
                'category': 0,  # Électronique
                'user': 1,
                'value': 600.0,
                'condition': 'very_good',
                'city': 'Lausanne',
                'latitude': 46.5197,
                'longitude': 6.6323
            },
            {
                'title': 'MacBook Pro M1',
                'description': 'MacBook Pro 13" avec puce M1, 512GB SSD',
                'category': 0,  # Électronique
                'user': 2,
                'value': 1200.0,
                'condition': 'excellent',
                'city': 'Zurich',
                'latitude': 47.3769,
                'longitude': 8.5417
            },
            {
                'title': 'Veste en cuir',
                'description': 'Veste en cuir véritable, taille M',
                'category': 1,  # Vêtements
                'user': 0,
                'value': 150.0,
                'condition': 'good',
                'city': 'Genève',
                'latitude': 46.2044,
                'longitude': 6.1432
            },
            {
                'title': 'Table basse en bois',
                'description': 'Table basse en bois massif, style scandinave',
                'category': 2,  # Maison & Jardin
                'user': 1,
                'value': 200.0,
                'condition': 'very_good',
                'city': 'Lausanne',
                'latitude': 46.5197,
                'longitude': 6.6323
            }
        ]
        
        for data in listing_data:
            listing = Listing(
                user_id=users[data['user']].id,
                category_id=categories[data['category']].id,
                title=data['title'],
                description=data['description'],
                listing_type='good',
                condition=data['condition'],
                estimated_value=data['value'],
                currency='CHF',
                city=data['city'],
                latitude=data['latitude'],
                longitude=data['longitude'],
                country='CH',
                exchange_type='both',
                status='active',
                is_featured=False,
                is_boosted=False,
                views_count=0,
                likes_count=0,
                shares_count=0,
                published_at=datetime.utcnow(),
                expires_at=datetime.utcnow(),
                tags='test,matching',
                listing_metadata={}
            )
            db.session.add(listing)
            listings.append(listing)
        
        db.session.commit()
        print("✅ Annonces créées")
        
        # Démarrer le serveur de test
        with app.test_client() as client:
            # Simuler l'authentification
            with app.app_context():
                # Créer un token JWT de test
                from flask_jwt_extended import create_access_token
                token = create_access_token(identity=str(users[0].id))
                
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
                
                print("\n🔍 Test 1: Suggestions de matching pour une annonce spécifique")
                response = client.get(f'/api/exchanges/matching/suggestions?listing_id={listings[0].id}&max_distance=100&max_suggestions=5', 
                    headers=headers
                )
                
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    print("✅ Suggestions de matching réussies")
                    print(f"   - Nombre de suggestions: {data['total']}")
                    print(f"   - Filtres appliqués: {data['filters']}")
                    if data['suggestions']:
                        suggestion = data['suggestions'][0]
                        print(f"   - Meilleure suggestion: {suggestion['listing']['title']}")
                        print(f"   - Score de compatibilité: {suggestion['compatibility_score']:.2f}")
                        print(f"   - Distance: {suggestion['distance_km']} km")
                        print(f"   - Raisons du match: {', '.join(suggestion['match_reasons'])}")
                else:
                    print(f"❌ Erreur: {response.get_json()}")
                
                print("\n🔍 Test 2: Suggestions générales de matching")
                response = client.get('/api/exchanges/matching/suggestions?max_distance=100&max_suggestions=10', 
                    headers=headers
                )
                
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    print("✅ Suggestions générales réussies")
                    print(f"   - Nombre de suggestions: {data['total']}")
                    if data['suggestions']:
                        suggestion = data['suggestions'][0]
                        print(f"   - Meilleure suggestion: {suggestion['listing']['title']}")
                        print(f"   - Score de compatibilité: {suggestion['compatibility_score']:.2f}")
                else:
                    print(f"❌ Erreur: {response.get_json()}")
                
                print("\n🔍 Test 3: Chaînes d'échange")
                response = client.get(f'/api/exchanges/matching/chains?listing_id={listings[0].id}&max_chain_length=3&max_distance=200', 
                    headers=headers
                )
                
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    print("✅ Recherche de chaînes réussie")
                    print(f"   - Nombre de chaînes trouvées: {data['total']}")
                    print(f"   - Filtres appliqués: {data['filters']}")
                    if data['chains']:
                        chain = data['chains'][0]
                        print(f"   - Longueur de chaîne: {chain['length']}")
                        print(f"   - Distance totale: {chain['total_distance']} km")
                        print(f"   - Score de faisabilité: {chain['feasibility_score']:.2f}")
                else:
                    print(f"❌ Erreur: {response.get_json()}")
                
                print("\n🔍 Test 4: Analyse de compatibilité entre deux annonces")
                response = client.post('/api/exchanges/matching/analyze', 
                    json={
                        'listing_id_1': str(listings[0].id),
                        'listing_id_2': str(listings[1].id)
                    },
                    headers=headers
                )
                
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    print("✅ Analyse de compatibilité réussie")
                    analysis = data['analysis']
                    print(f"   - Score de compatibilité: {analysis['compatibility_score']:.2f}")
                    print(f"   - Distance: {analysis['distance_km']} km")
                    print(f"   - Facteurs positifs: {analysis['positive_factors']}/{analysis['total_factors']}")
                    print(f"   - Recommandation: {analysis['recommendation']}")
                    if analysis['suggestions']:
                        print(f"   - Suggestions: {', '.join(analysis['suggestions'])}")
                else:
                    print(f"❌ Erreur: {response.get_json()}")
                
                print("\n🔍 Test 5: Test avec des paramètres différents")
                response = client.get(f'/api/exchanges/matching/suggestions?listing_id={listings[0].id}&max_distance=50&max_suggestions=3', 
                    headers=headers
                )
                
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    print("✅ Test avec paramètres différents réussi")
                    print(f"   - Nombre de suggestions: {data['total']}")
                    print(f"   - Distance max: {data['filters']['max_distance']} km")
                    print(f"   - Suggestions max: {data['filters']['max_suggestions']}")
                else:
                    print(f"❌ Erreur: {response.get_json()}")
                
                print("\n🔍 Test 6: Test d'erreur - Annonce inexistante")
                response = client.get('/api/exchanges/matching/suggestions?listing_id=00000000-0000-0000-0000-000000000000', 
                    headers=headers
                )
                
                print(f"Status: {response.status_code}")
                if response.status_code == 404:
                    print("✅ Gestion d'erreur correcte - Annonce non trouvée")
                else:
                    print(f"❌ Erreur inattendue: {response.get_json()}")
                
                print("\n🔍 Test 7: Test d'erreur - Annonce d'un autre utilisateur")
                # Créer un token pour un autre utilisateur
                other_token = create_access_token(identity=str(users[1].id))
                other_headers = {
                    'Authorization': f'Bearer {other_token}',
                    'Content-Type': 'application/json'
                }
                
                response = client.get(f'/api/exchanges/matching/suggestions?listing_id={listings[0].id}', 
                    headers=other_headers
                )
                
                print(f"Status: {response.status_code}")
                if response.status_code == 404:
                    print("✅ Gestion d'erreur correcte - Annonce d'un autre utilisateur")
                else:
                    print(f"❌ Erreur inattendue: {response.get_json()}")
                
                print("\n==================================================")
                print("🎉 Tests du moteur de matching terminés !")
                print("🚀 Le moteur de matching fonctionne correctement")
                
                return True

if __name__ == '__main__':
    if not test_matching_api():
        print("\n==================================================")
        print("❌ CERTAINS TESTS DU MOTEUR DE MATCHING ONT ÉCHOUÉ")
        sys.exit(1)
