#!/usr/bin/env python3
"""
Script pour créer les tables dans Postgres
"""

import os
import sys
from flask import Flask
from flask_migrate import upgrade

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import *  # Importer tous les modèles

def migrate_database():
    """Créer toutes les tables dans la base de données"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Création des tables dans la base de données...")
            
            # Créer toutes les tables
            db.create_all()
            
            print("✅ Tables créées avec succès!")
            
            # Vérifier les tables créées
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"📊 {len(tables)} tables créées:")
            for table in sorted(tables):
                print(f"  - {table}")
                
        except Exception as e:
            print(f"❌ Erreur lors de la création des tables: {e}")
            sys.exit(1)

if __name__ == '__main__':
    migrate_database()
