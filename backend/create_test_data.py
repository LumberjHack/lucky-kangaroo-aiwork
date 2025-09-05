#!/usr/bin/env python3
"""
Script pour créer des données de test pour Lucky Kangaroo
"""

import os
import sys
import uuid
from datetime import datetime, timedelta
import random

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Forcer l'utilisation de SQLite
os.environ['DATABASE_URL'] = 'sqlite:///lucky_kangaroo.db'
os.environ['FLASK_ENV'] = 'development'

def create_test_data():
    """Créer des données de test"""
    print("🔄 Création des données de test...")
    
    try:
        from app import create_app, db
        from app.models.user import User
        from app.models.listing import Listing, ListingCategory, ListingStatus, ListingType, ExchangeType, Condition
        
        app = create_app()
        
        with app.app_context():
            # Créer les tables
            db.create_all()
            
            # Créer des catégories de test
            categories_data = [
                {'name': 'Électronique', 'slug': 'electronique', 'icon': '📱', 'description': 'Appareils électroniques'},
                {'name': 'Véhicules', 'slug': 'vehicules', 'icon': '🚗', 'description': 'Voitures, motos, vélos'},
                {'name': 'Meubles', 'slug': 'meubles', 'icon': '🪑', 'description': 'Meubles et décoration'},
                {'name': 'Vêtements', 'slug': 'vetements', 'icon': '👕', 'description': 'Vêtements et accessoires'},
                {'name': 'Livres', 'slug': 'livres', 'icon': '📚', 'description': 'Livres, BD, magazines'},
                {'name': 'Sport', 'slug': 'sport', 'icon': '⚽', 'description': 'Équipements sportifs'},
                {'name': 'Maison & Jardin', 'slug': 'maison-jardin', 'icon': '🏠', 'description': 'Outils et équipements'},
                {'name': 'Services', 'slug': 'services', 'icon': '🔧', 'description': 'Services divers'}
            ]
            
            categories = {}
            for cat_data in categories_data:
                category = ListingCategory.query.filter_by(slug=cat_data['slug']).first()
                if not category:
                    category = ListingCategory(
                        id=str(uuid.uuid4()),
                        name=cat_data['name'],
                        slug=cat_data['slug'],
                        description=cat_data['description'],
                        icon=cat_data['icon'],
                        sort_order=len(categories) + 1,
                        is_active=True
                    )
                    db.session.add(category)
                    db.session.commit()
                categories[cat_data['slug']] = category
            
            print(f"✅ {len(categories)} catégories créées")
            
            # Créer des utilisateurs de test
            users_data = [
                {'email': 'alice@example.com', 'username': 'alice.martin', 'first_name': 'Alice', 'last_name': 'Martin', 'city': 'Genève'},
                {'email': 'bob@example.com', 'username': 'bob.dupont', 'first_name': 'Bob', 'last_name': 'Dupont', 'city': 'Lausanne'},
                {'email': 'charlie@example.com', 'username': 'charlie.bernard', 'first_name': 'Charlie', 'last_name': 'Bernard', 'city': 'Zurich'},
                {'email': 'diana@example.com', 'username': 'diana.richard', 'first_name': 'Diana', 'last_name': 'Richard', 'city': 'Bâle'},
                {'email': 'eve@example.com', 'username': 'eve.petit', 'first_name': 'Eve', 'last_name': 'Petit', 'city': 'Berne'}
            ]
            
            users = {}
            for user_data in users_data:
                user = User.query.filter_by(email=user_data['email']).first()
                if not user:
                    user = User(
                        id=str(uuid.uuid4()),
                        email=user_data['email'],
                        username=user_data['username'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        city=user_data['city'],
                        country='CH',
                        status='active',
                        role='user'
                    )
                    user.password = 'TestPassword123!'
                    db.session.add(user)
                    db.session.commit()
                users[user_data['username']] = user
            
            print(f"✅ {len(users)} utilisateurs créés")
            
            # Créer des annonces de test
            listings_data = [
                # Électronique
                {'title': 'iPhone 13 Pro Max 256GB', 'description': 'iPhone 13 Pro Max en excellent état, utilisé 6 mois. Boîtier, chargeur et écouteurs inclus.', 'category': 'electronique', 'listing_type': 'good', 'condition': 'excellent', 'brand': 'Apple', 'model': 'iPhone 13 Pro Max', 'year': 2022, 'estimated_value': 800, 'city': 'Genève', 'postal_code': '1200', 'user': 'alice.martin'},
                {'title': 'MacBook Pro M2 13"', 'description': 'MacBook Pro M2 13 pouces, 512GB SSD, 16GB RAM. Parfait état, garantie Apple.', 'category': 'electronique', 'listing_type': 'good', 'condition': 'excellent', 'brand': 'Apple', 'model': 'MacBook Pro M2', 'year': 2023, 'estimated_value': 1500, 'city': 'Lausanne', 'postal_code': '1000', 'user': 'bob.dupont'},
                {'title': 'Samsung Galaxy S23 Ultra', 'description': 'Samsung Galaxy S23 Ultra 256GB, noir. Très bon état, quelques micro-rayures sur l\'écran.', 'category': 'electronique', 'listing_type': 'good', 'condition': 'very_good', 'brand': 'Samsung', 'model': 'Galaxy S23 Ultra', 'year': 2023, 'estimated_value': 900, 'city': 'Zurich', 'postal_code': '8001', 'user': 'charlie.bernard'},
                
                # Véhicules
                {'title': 'Vélo électrique Trek Powerfly 5', 'description': 'Vélo électrique Trek Powerfly 5, moteur Bosch, batterie 500Wh. Parfait pour les trajets urbains.', 'category': 'vehicules', 'listing_type': 'good', 'condition': 'very_good', 'brand': 'Trek', 'model': 'Powerfly 5', 'year': 2022, 'estimated_value': 2500, 'city': 'Bâle', 'postal_code': '4001', 'user': 'diana.richard'},
                {'title': 'Honda Civic Type R 2020', 'description': 'Honda Civic Type R en excellent état, 45\'000 km, entretien récent. Garantie constructeur.', 'category': 'vehicules', 'listing_type': 'good', 'condition': 'excellent', 'brand': 'Honda', 'model': 'Civic Type R', 'year': 2020, 'estimated_value': 35000, 'city': 'Genève', 'postal_code': '1200', 'user': 'alice.martin'},
                
                # Meubles
                {'title': 'Table à manger en chêne massif', 'description': 'Table à manger en chêne massif, 6 places, dimensions 180x90cm. Très bon état.', 'category': 'meubles', 'listing_type': 'good', 'condition': 'good', 'brand': 'IKEA', 'model': 'HENRIKSDAL', 'year': 2021, 'estimated_value': 400, 'city': 'Lausanne', 'postal_code': '1000', 'user': 'bob.dupont'},
                {'title': 'Canapé 3 places gris', 'description': 'Canapé 3 places gris, tissu résistant, très confortable. Quelques taches mineures.', 'category': 'meubles', 'listing_type': 'good', 'condition': 'fair', 'brand': 'Conforama', 'model': 'DIVAN 3P', 'year': 2020, 'estimated_value': 300, 'city': 'Zurich', 'postal_code': '8001', 'user': 'charlie.bernard'},
                
                # Vêtements
                {'title': 'Manteau d\'hiver The North Face', 'description': 'Manteau d\'hiver The North Face, taille M, noir. Parfait pour les sports d\'hiver.', 'category': 'vetements', 'listing_type': 'good', 'condition': 'very_good', 'brand': 'The North Face', 'model': 'NUPTSE', 'year': 2022, 'estimated_value': 200, 'city': 'Bâle', 'postal_code': '4001', 'user': 'diana.richard'},
                {'title': 'Chaussures de course Nike Air Max', 'description': 'Chaussures de course Nike Air Max, taille 42, bleu. Utilisées quelques fois seulement.', 'category': 'vetements', 'listing_type': 'good', 'condition': 'excellent', 'brand': 'Nike', 'model': 'Air Max 270', 'year': 2023, 'estimated_value': 120, 'city': 'Berne', 'postal_code': '3000', 'user': 'eve.petit'},
                
                # Livres
                {'title': 'Collection Harry Potter complète', 'description': 'Collection complète des 7 livres Harry Potter en français, édition Gallimard. Très bon état.', 'category': 'livres', 'listing_type': 'good', 'condition': 'very_good', 'brand': 'Gallimard', 'model': 'Harry Potter', 'year': 2020, 'estimated_value': 80, 'city': 'Genève', 'postal_code': '1200', 'user': 'alice.martin'},
                {'title': 'Manuel de cuisine française', 'description': 'Manuel de cuisine française, 500 recettes traditionnelles. État correct.', 'category': 'livres', 'listing_type': 'good', 'condition': 'good', 'brand': 'Larousse', 'model': 'Cuisine Française', 'year': 2019, 'estimated_value': 25, 'city': 'Lausanne', 'postal_code': '1000', 'user': 'bob.dupont'},
                
                # Sport
                {'title': 'Raquette de tennis Wilson Pro Staff', 'description': 'Raquette de tennis Wilson Pro Staff, modèle 2023. Parfait état, cordage récent.', 'category': 'sport', 'listing_type': 'good', 'condition': 'excellent', 'brand': 'Wilson', 'model': 'Pro Staff', 'year': 2023, 'estimated_value': 180, 'city': 'Zurich', 'postal_code': '8001', 'user': 'charlie.bernard'},
                {'title': 'Vélo de route Cannondale CAAD13', 'description': 'Vélo de route Cannondale CAAD13, taille 56cm, groupe Shimano 105. Excellent état.', 'category': 'sport', 'listing_type': 'good', 'condition': 'excellent', 'brand': 'Cannondale', 'model': 'CAAD13', 'year': 2022, 'estimated_value': 1800, 'city': 'Bâle', 'postal_code': '4001', 'user': 'diana.richard'},
                
                # Services
                {'title': 'Cours de guitare à domicile', 'description': 'Cours de guitare à domicile pour débutants et intermédiaires. 10 ans d\'expérience.', 'category': 'services', 'listing_type': 'service', 'condition': 'excellent', 'brand': 'Musique', 'model': 'Cours', 'year': 2023, 'estimated_value': 50, 'city': 'Berne', 'postal_code': '3000', 'user': 'eve.petit'},
                {'title': 'Nettoyage de maison', 'description': 'Service de nettoyage de maison, appartement ou bureau. Tarif horaire compétitif.', 'category': 'services', 'listing_type': 'service', 'condition': 'excellent', 'brand': 'Ménage', 'model': 'Nettoyage', 'year': 2023, 'estimated_value': 25, 'city': 'Genève', 'postal_code': '1200', 'user': 'alice.martin'}
            ]
            
            created_listings = 0
            for listing_data in listings_data:
                # Vérifier si l'annonce existe déjà
                existing = Listing.query.filter_by(title=listing_data['title']).first()
                if existing:
                    continue
                
                listing = Listing(
                    id=str(uuid.uuid4()),
                    user_id=users[listing_data['user']].id,
                    category_id=categories[listing_data['category']].id,
                    title=listing_data['title'],
                    description=listing_data['description'],
                    listing_type=listing_data['listing_type'],  # Utiliser directement la string
                    condition=listing_data['condition'],  # Utiliser directement la string
                    brand=listing_data['brand'],
                    model=listing_data['model'],
                    year=listing_data['year'],
                    estimated_value=listing_data['estimated_value'],
                    currency='CHF',
                    city=listing_data['city'],
                    postal_code=listing_data['postal_code'],
                    country='CH',
                    exchange_type='both',  # Utiliser directement la string
                    status='active',  # Utiliser directement la string
                    views_count=random.randint(10, 500),
                    likes_count=random.randint(0, 50)
                )
                
                # Ajouter des coordonnées approximatives pour chaque ville
                city_coords = {
                    'Genève': (46.2044, 6.1432),
                    'Lausanne': (46.5197, 6.6323),
                    'Zurich': (47.3769, 8.5417),
                    'Bâle': (47.5596, 7.5886),
                    'Berne': (46.9481, 7.4474)
                }
                
                if listing_data['city'] in city_coords:
                    lat, lon = city_coords[listing_data['city']]
                    # Ajouter une petite variation pour simuler des positions différentes
                    listing.latitude = lat + random.uniform(-0.01, 0.01)
                    listing.longitude = lon + random.uniform(-0.01, 0.01)
                
                db.session.add(listing)
                created_listings += 1
            
            db.session.commit()
            print(f"✅ {created_listings} annonces créées")
            
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
    print("🚀 Création des données de test Lucky Kangaroo")
    print("=" * 50)
    
    success = create_test_data()
    
    if success:
        print("\n✅ Données de test créées avec succès !")
        print("🔍 Vous pouvez maintenant tester la recherche avancée")
    else:
        print("\n❌ Erreur lors de la création des données de test")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
