#!/usr/bin/env python3
"""
Test de l'application Flask Lucky Kangaroo
"""

import os
import sys

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Définir l'environnement de développement
os.environ['FLASK_ENV'] = 'development'
os.environ['DATABASE_URL'] = 'sqlite:///lucky_kangaroo.db'

def test_app_creation():
    """Tester la création de l'application Flask"""
    try:
        print("🔄 Test de création de l'application Flask...")
        
        # Importer et créer l'application
        from app import create_app, db
        app = create_app()
        
        print("✅ Application Flask créée avec succès")
        
        # Tester le contexte d'application
        with app.app_context():
            print("🔄 Test du contexte d'application...")
            
            # Tester la connexion à la base de données
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            print("✅ Connexion à la base de données réussie")
            
            # Tester les routes de base
            with app.test_client() as client:
                print("🔄 Test des routes de base...")
                
                # Test de la route racine
                response = client.get('/')
                if response.status_code == 200:
                    print("✅ Route racine fonctionnelle")
                else:
                    print(f"❌ Route racine échouée: {response.status_code}")
                
                # Test de la route de santé
                response = client.get('/health')
                if response.status_code == 200:
                    print("✅ Route de santé fonctionnelle")
                else:
                    print(f"❌ Route de santé échouée: {response.status_code}")
        
        print("🎉 Tous les tests sont passés avec succès !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_app_creation()
    sys.exit(0 if success else 1)
