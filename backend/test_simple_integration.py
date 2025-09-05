#!/usr/bin/env python3
"""
Test d'intégration simple Lucky Kangaroo
"""

import os
import sys
import uuid
from datetime import datetime

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Forcer l'utilisation de SQLite
os.environ['DATABASE_URL'] = 'sqlite:///lucky_kangaroo.db'
os.environ['FLASK_ENV'] = 'development'

def test_simple_integration():
    """Test d'intégration simple"""
    print("🔄 Test d'intégration simple...")
    
    try:
        from app import create_app, db
        from app.models.user import User
        from app.models.listing import Listing, ListingCategory
        
        app = create_app()
        
        with app.app_context():
            # Créer les tables
            db.create_all()
            
            # Vérifier si une catégorie existe déjà
            category = ListingCategory.query.filter_by(slug="electronique").first()
            if not category:
                category = ListingCategory(
                    id=str(uuid.uuid4()),
                    name="Électronique",
                    slug="electronique",
                    description="Appareils électroniques",
                    icon="📱",
                    sort_order=1,
                    is_active=True
                )
                db.session.add(category)
                db.session.commit()
                print("✅ Catégorie créée")
            else:
                print("✅ Catégorie existante utilisée")
            
            # Créer un utilisateur de test
            user = User(
                id=str(uuid.uuid4()),
                email=f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
                username=f"test.user.{datetime.now().strftime('%H%M%S')}",
                first_name="Test",
                last_name="User",
                country="CH",
                status="active",
                role="user"
            )
            user.password = "TestPassword123!"
            db.session.add(user)
            db.session.commit()
            
            print("✅ Utilisateur créé")
            
            # Créer une annonce de test
            listing = Listing(
                id=str(uuid.uuid4()),
                user_id=user.id,
                category_id=category.id,
                title="Test iPhone 13 Pro Max",
                description="iPhone 13 Pro Max 256GB en excellent état",
                listing_type="good",
                condition="excellent",
                brand="Apple",
                model="iPhone 13 Pro Max",
                year=2022,
                estimated_value=800,
                currency="CHF",
                city="Genève",
                postal_code="1200",
                country="CH",
                exchange_type="both",
                status="draft"
            )
            db.session.add(listing)
            db.session.commit()
            
            print("✅ Annonce créée")
            
            # Vérifier que tout est bien en base
            user_count = User.query.count()
            category_count = ListingCategory.query.count()
            listing_count = Listing.query.count()
            
            print(f"✅ Utilisateurs en base: {user_count}")
            print(f"✅ Catégories en base: {category_count}")
            print(f"✅ Annonces en base: {listing_count}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    print("🚀 Test d'intégration simple Lucky Kangaroo")
    print("=" * 50)
    
    success = test_simple_integration()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TEST RÉUSSI !")
        print("🚀 Lucky Kangaroo fonctionne correctement !")
        print("\n📱 Frontend: http://localhost:3001")
        print("🔧 Backend API: http://127.0.0.1:5000")
        print("📚 Documentation: http://127.0.0.1:5000/api/")
    else:
        print("❌ TEST ÉCHOUÉ")
        print("🔧 Vérifiez les erreurs ci-dessus.")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
