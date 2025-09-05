#!/usr/bin/env python3
"""
Test simple pour vérifier l'application Flask
"""

import os
import sys

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_creation():
    """Tester la création de l'application"""
    try:
        from app import create_app
        app = create_app()
        
        print("✅ Application Flask créée avec succès")
        
        # Lister les routes
        print("\n📋 Routes disponibles:")
        for rule in app.url_map.iter_rules():
            print(f"  {rule.methods} {rule.rule}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'application: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_app_creation()
