#!/usr/bin/env python3
"""
Script de test pour créer la base de données Lucky Kangaroo
"""

import os
import sys

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Définir l'environnement de développement
os.environ['FLASK_ENV'] = 'development'
os.environ['DATABASE_URL'] = 'sqlite:///lucky_kangaroo.db'

from app import create_app, db
from app.models import User, Listing, Exchange, ChatMessage, Notification, Badge, Review, Payment, Location, AIAnalysis

def create_database():
    """Créer la base de données et les tables"""
    try:
        print("🔄 Création de l'application Flask...")
        app = create_app('development')
        
        print("🔄 Création du contexte d'application...")
        with app.app_context():
            print("🔄 Création des tables de base de données...")
            db.create_all()
            
            print("✅ Base de données créée avec succès !")
            print(f"📁 Base de données : {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # Vérifier que les tables ont été créées
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📊 Tables créées : {', '.join(tables)}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la création de la base de données : {str(e)}")
        return False

if __name__ == '__main__':
    success = create_database()
    if success:
        print("\n🎉 Base de données Lucky Kangaroo prête !")
    else:
        print("\n💥 Échec de la création de la base de données")
        sys.exit(1)
