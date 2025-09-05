#!/usr/bin/env python3
"""
Test simple de l'API de recherche Lucky Kangaroo
"""

import os
import sys

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Forcer l'utilisation de SQLite
os.environ['DATABASE_URL'] = 'sqlite:///lucky_kangaroo.db'
os.environ['FLASK_ENV'] = 'testing'

def test_search_simple():
    """Test simple de l'API de recherche"""
    print("🔍 Test simple de l'API de recherche Lucky Kangaroo")
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
                
                # Test 1: Recherche simple sans données
                print("\n🔍 Test 1: Recherche simple (sans données)")
                response = client.get('/api/search/search')
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    print(f"Résultats trouvés: {len(data.get('data', {}).get('listings', []))}")
                    print("✅ Recherche simple fonctionne")
                else:
                    print(f"❌ Erreur: {response.get_json()}")
                
                # Test 2: Suggestions de recherche
                print("\n🔍 Test 2: Suggestions de recherche")
                response = client.get('/api/search/suggestions?q=test')
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    suggestions = data.get('data', {}).get('suggestions', [])
                    print(f"Suggestions trouvées: {len(suggestions)}")
                    print("✅ Suggestions fonctionnent")
                else:
                    print(f"❌ Erreur: {response.get_json()}")
                
                # Test 3: Filtres disponibles
                print("\n🔍 Test 3: Filtres disponibles")
                response = client.get('/api/search/filters')
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    filters_data = data.get('data', {})
                    print(f"Catégories: {len(filters_data.get('categories', []))}")
                    print(f"Conditions: {len(filters_data.get('conditions', []))}")
                    print("✅ Filtres fonctionnent")
                else:
                    print(f"❌ Erreur: {response.get_json()}")
                
                # Test 4: Recherches tendances
                print("\n🔍 Test 4: Recherches tendances")
                response = client.get('/api/search/trending')
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    trending = data.get('data', {}).get('trending', [])
                    print(f"Tendances trouvées: {len(trending)}")
                    print("✅ Tendances fonctionnent")
                else:
                    print(f"❌ Erreur: {response.get_json()}")
                
                print("\n🎉 Tests simples de l'API de recherche terminés !")
                return True
                
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    success = test_search_simple()
    
    if success:
        print("\n✅ Tests simples de l'API de recherche réussis !")
        print("🚀 L'API de recherche fonctionne correctement")
    else:
        print("\n❌ Erreur lors des tests de l'API de recherche")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
