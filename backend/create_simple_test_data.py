#!/usr/bin/env python3
"""
Script simple pour créer des données de test pour Lucky Kangaroo
"""

import os
import sys
import uuid
from datetime import datetime
import random

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Forcer l'utilisation de SQLite
os.environ['DATABASE_URL'] = 'sqlite:///lucky_kangaroo.db'
os.environ['FLASK_ENV'] = 'development'

def create_simple_test_data():
    """Créer des données de test simples"""
    print("🔄 Création des données de test simples...")
    
    try:
        from app import create_app, db
        from app.models.user import User
        from app.models.listing import Listing, ListingCategory
        
        app = create_app()
        
        with app.app_context():
            # Créer les tables
            db.create_all()
            
            # Créer une catégorie de test si elle n'existe pas
            category = ListingCategory.query.filter_by(slug='electronique').first()
            if not category:
                category = ListingCategory(
                    id=str(uuid.uuid4()),
                    name='Électronique',
                    slug='electronique',
                    description='Appareils électroniques',
                    icon='📱',
                    sort_order=1,
                    is_active=True
                )
                db.session.add(category)
                db.session.commit()
                print("✅ Catégorie créée")
            else:
                print("✅ Catégorie existante utilisée")
            
            # Créer un utilisateur de test si il n'existe pas
            user = User.query.filter_by(email='test@example.com').first()
            if not user:
                user = User(
                    id=str(uuid.uuid4()),
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
                print("✅ Utilisateur créé")
            else:
                print("✅ Utilisateur existant utilisé")
            
            # Créer quelques annonces de test
            test_listings = [
                {
                    'title': 'iPhone 13 Pro Max 256GB',
                    'description': 'iPhone 13 Pro Max en excellent état, utilisé 6 mois. Boîtier, chargeur et écouteurs inclus.',
                    'estimated_value': 800,
                    'city': 'Genève',
                    'postal_code': '1200'
                },
                {
                    'title': 'MacBook Pro M2 13"',
                    'description': 'MacBook Pro M2 13 pouces, 512GB SSD, 16GB RAM. Parfait état, garantie Apple.',
                    'estimated_value': 1500,
                    'city': 'Lausanne',
                    'postal_code': '1000'
                },
                {
                    'title': 'Samsung Galaxy S23 Ultra',
                    'description': 'Samsung Galaxy S23 Ultra 256GB, noir. Très bon état, quelques micro-rayures sur l\'écran.',
                    'estimated_value': 900,
                    'city': 'Zurich',
                    'postal_code': '8001'
                },
                {
                    'title': 'Vélo électrique Trek Powerfly 5',
                    'description': 'Vélo électrique Trek Powerfly 5, moteur Bosch, batterie 500Wh. Parfait pour les trajets urbains.',
                    'estimated_value': 2500,
                    'city': 'Bâle',
                    'postal_code': '4001'
                },
                {
                    'title': 'Table à manger en chêne massif',
                    'description': 'Table à manger en chêne massif, 6 places, dimensions 180x90cm. Très bon état.',
                    'estimated_value': 400,
                    'city': 'Berne',
                    'postal_code': '3000'
                }
            ]
            
            created_count = 0
            for listing_data in test_listings:
                # Vérifier si l'annonce existe déjà
                existing = Listing.query.filter_by(title=listing_data['title']).first()
                if existing:
                    continue
                
                listing = Listing(
                    id=str(uuid.uuid4()),
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
                    views_count=random.randint(10, 500),
                    likes_count=random.randint(0, 50)
                )
                
                # Ajouter des coordonnées approximatives
                city_coords = {
                    'Genève': (46.2044, 6.1432),
                    'Lausanne': (46.5197, 6.6323),
                    'Zurich': (47.3769, 8.5417),
                    'Bâle': (47.5596, 7.5886),
                    'Berne': (46.9481, 7.4474)
                }
                
                if listing_data['city'] in city_coords:
                    lat, lon = city_coords[listing_data['city']]
                    listing.latitude = lat + random.uniform(-0.01, 0.01)
                    listing.longitude = lon + random.uniform(-0.01, 0.01)
                
                db.session.add(listing)
                created_count += 1
            
            db.session.commit()
            print(f"✅ {created_count} annonces créées")
            
            # Statistiques finales
            total_users = User.query.count()
            total_categories = ListingCategory.query.count()
            total_listings = Listing.query.count()
            
            print(f"\n🎉 Données de test créées avec succès !")
            print(f"📊 Statistiques:")
            print(f"   - Utilisateurs: {total_users}")
            print(f"   - Catégories: {total_categories}")
            print(f"   - Annonces: {total_listings}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    print("🚀 Création des données de test simples Lucky Kangaroo")
    print("=" * 50)
    
    success = create_simple_test_data()
    
    if success:
        print("\n✅ Données de test créées avec succès !")
        print("🔍 Vous pouvez maintenant tester la recherche avancée")
    else:
        print("\n❌ Erreur lors de la création des données de test")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
