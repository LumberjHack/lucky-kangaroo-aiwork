#!/usr/bin/env python3
"""
Test final d'intégration Lucky Kangaroo
"""

import os
import sys
import requests
import json
from datetime import datetime

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Forcer l'utilisation de SQLite
os.environ['DATABASE_URL'] = 'sqlite:///lucky_kangaroo.db'
os.environ['FLASK_ENV'] = 'development'

def test_app_directly():
    """Test direct de l'application"""
    print("🔄 Test direct de l'application...")
    
    try:
        from app import create_app
        app = create_app()
        
        with app.test_client() as client:
            # Test route racine
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Route racine: OK")
            else:
                print(f"❌ Route racine: {response.status_code}")
                return False
            
            # Test route categories
            response = client.get('/api/listings/categories')
            if response.status_code == 200:
                print("✅ Route categories: OK")
                data = response.get_json()
                print(f"   Nombre de catégories: {len(data.get('categories', []))}")
            else:
                print(f"❌ Route categories: {response.status_code}")
                return False
            
            # Test inscription utilisateur
            test_user = {
                "email": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
                "password": "TestPassword123!",
                "first_name": "Test",
                "last_name": "User",
                "country": "CH",
                "accept_terms": True
            }
            
            response = client.post('/api/auth/register', 
                                 json=test_user,
                                 content_type='application/json')
            
            if response.status_code == 201:
                print("✅ Inscription utilisateur: OK")
                data = response.get_json()
                access_token = data.get('access_token')
                user_id = data.get('user', {}).get('id')
                
                if access_token and user_id:
                    print("✅ Token JWT généré: OK")
                    
                    # Test création d'annonce
                    test_listing = {
                        "title": "Test iPhone 13 Pro Max",
                        "description": "iPhone 13 Pro Max 256GB en excellent état, utilisé pendant 6 mois.",
                        "category_id": "550e8400-e29b-41d4-a716-446655440000",  # UUID valide
                        "listing_type": "good",  # "good" ou "service"
                        "condition": "excellent",
                        "brand": "Apple",
                        "model": "iPhone 13 Pro Max",
                        "year": 2022,
                        "estimated_value": 800,
                        "currency": "CHF",
                        "city": "Genève",
                        "postal_code": "1200",
                        "country": "CH",
                        "exchange_type": "both",
                        "desired_items": ["MacBook", "iPad"],
                        "excluded_items": ["vêtements"],
                        "tags": ["urgent", "neuf"]
                    }
                    
                    headers = {'Authorization': f'Bearer {access_token}'}
                    response = client.post('/api/listings/',
                                         json=test_listing,
                                         headers=headers,
                                         content_type='application/json')
                    
                    if response.status_code == 201:
                        print("✅ Création d'annonce: OK")
                        data = response.get_json()
                        listing_id = data.get('listing', {}).get('id')
                        
                        if listing_id:
                            print("✅ ID d'annonce généré: OK")
                            
                            # Test récupération d'annonce
                            response = client.get(f'/api/listings/{listing_id}')
                            if response.status_code == 200:
                                print("✅ Récupération d'annonce: OK")
                                return True
                            else:
                                print(f"❌ Récupération d'annonce: {response.status_code}")
                                return False
                        else:
                            print("❌ ID d'annonce non généré")
                            return False
                    else:
                        print(f"❌ Création d'annonce: {response.status_code}")
                        print(f"   Erreur: {response.get_json()}")
                        return False
                else:
                    print("❌ Token JWT non généré")
                    return False
            else:
                print(f"❌ Inscription utilisateur: {response.status_code}")
                print(f"   Erreur: {response.get_json()}")
                return False
                
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    print("🚀 Test d'intégration final Lucky Kangaroo")
    print("=" * 50)
    
    success = test_app_directly()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS !")
        print("🚀 Lucky Kangaroo est prêt à être utilisé !")
        print("\n📱 Frontend: http://localhost:3001")
        print("🔧 Backend API: http://127.0.0.1:5000")
        print("📚 Documentation: http://127.0.0.1:5000/api/")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Vérifiez les erreurs ci-dessus.")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
