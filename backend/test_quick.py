#!/usr/bin/env python3
"""
Test rapide pour vérifier l'application
"""

import os
import sys

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Forcer l'utilisation de SQLite
os.environ['DATABASE_URL'] = 'sqlite:///lucky_kangaroo.db'
os.environ['FLASK_ENV'] = 'development'

def test_app():
    """Test rapide de l'application"""
    try:
        from app import create_app
        app = create_app()
        
        print("✅ Application créée avec succès")
        
        # Tester les routes
        with app.test_client() as client:
            # Test route racine
            response = client.get('/')
            print(f"Route racine: {response.status_code}")
            
            # Test route health
            response = client.get('/health')
            print(f"Route health: {response.status_code}")
            
            # Test route API
            response = client.get('/api/listings/categories')
            print(f"Route categories: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ API fonctionne correctement")
                return True
            else:
                print(f"❌ Erreur API: {response.get_json()}")
                return False
                
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_app()
