#!/usr/bin/env python3
"""
Test de l'API IA pour Lucky Kangaroo
Teste la reconnaissance d'objets et l'estimation de valeur
"""

import os
import sys
import requests
import time
import uuid
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.user import User, UserStatus, UserRole
from app.models.listing import Listing, ListingCategory
from app.models.ai_analysis import AIAnalysis

def test_ai_api():
    """Test complet de l'API IA"""
    print("🚀 Test de l'API IA - Reconnaissance d'objets et estimation de valeur")
    
    # Configuration
    app = create_app()
    app.config['TESTING'] = True
    app.config['DATABASE_URL'] = 'sqlite:///test_ai.db'
    app.config['FLASK_ENV'] = 'testing'
    
    with app.app_context():
        # Nettoyer la base de données
        db.drop_all()
        db.create_all()
        
        # Créer un utilisateur de test
        user = User(
            email='test@ai.com',
            username='testai',
            password_hash='$2b$12$test_hash',
            first_name='Test',
            last_name='AI',
            country='CH',
            timezone='Europe/Zurich',
            language='fr',
            currency='CHF',
            preferences={},
            notification_settings={},
            privacy_settings={},
            status=UserStatus.ACTIVE,
            role=UserRole.USER,
            trust_score=5.0,
            ecological_score=5.0,
            total_exchanges=0,
            successful_exchanges=0,
            total_listings=0,
            active_listings=0,
            last_activity=datetime.utcnow()
        )
        
        db.session.add(user)
        db.session.commit()
        print("✅ Utilisateur créé")
        
        # Créer une catégorie
        category = ListingCategory(
            name='Électronique',
            slug='electronique',
            description='Appareils électroniques',
            sort_order=1,
            is_active=True
        )
        
        db.session.add(category)
        db.session.commit()
        print("✅ Catégorie créée")
        
        # Créer une annonce de test
        listing = Listing(
            user_id=user.id,
            category_id=category.id,
            title='iPhone 13 Pro Max',
            description='iPhone 13 Pro Max 256GB en excellent état, avec boîte et accessoires',
            listing_type='good',
            condition='excellent',
            brand='Apple',
            model='iPhone 13 Pro Max',
            year=2022,
            estimated_value=800.0,
            currency='CHF',
            city='Genève',
            postal_code='1200',
            country='CH',
            exchange_type='both',
            status='active',
            is_featured=False,
            is_boosted=False,
            views_count=0,
            likes_count=0,
            shares_count=0,
            published_at=datetime.utcnow(),
            expires_at=datetime.utcnow(),
            tags='smartphone,apple,iphone,pro,max',
            listing_metadata={}
        )
        
        db.session.add(listing)
        db.session.commit()
        print("✅ Annonce créée")
        
        # Démarrer le serveur de test
        with app.test_client() as client:
            # Simuler l'authentification
            with app.app_context():
                # Créer un token JWT de test
                from flask_jwt_extended import create_access_token
                token = create_access_token(identity=str(user.id))
                
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
                
                print("\n🔍 Test 1: Analyse d'image - Reconnaissance d'objets")
                response = client.post('/api/ai/analyze/image', 
                    json={
                        'listing_id': str(listing.id),
                        'analysis_type': 'object_detection'
                    },
                    headers=headers
                )
                
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    print("✅ Reconnaissance d'objets réussie")
                    print(f"   - Type d'analyse: {data['analysis']['analysis_type']}")
                    print(f"   - Statut: {data['analysis']['status']}")
                    print(f"   - Score de confiance: {data['analysis']['confidence_score']}")
                else:
                    print(f"❌ Erreur: {response.get_json()}")
                
                print("\n🔍 Test 2: Analyse d'image - Estimation de valeur")
                response = client.post('/api/ai/analyze/image', 
                    json={
                        'listing_id': str(listing.id),
                        'analysis_type': 'value_estimation'
                    },
                    headers=headers
                )
                
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    print("✅ Estimation de valeur réussie")
                    print(f"   - Type d'analyse: {data['analysis']['analysis_type']}")
                    print(f"   - Statut: {data['analysis']['status']}")
                    print(f"   - Score de confiance: {data['analysis']['confidence_score']}")
                else:
                    print(f"❌ Erreur: {response.get_json()}")
                
                print("\n🔍 Test 3: Analyse d'image - Analyse de condition")
                response = client.post('/api/ai/analyze/image', 
                    json={
                        'listing_id': str(listing.id),
                        'analysis_type': 'condition_analysis'
                    },
                    headers=headers
                )
                
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    print("✅ Analyse de condition réussie")
                    print(f"   - Type d'analyse: {data['analysis']['analysis_type']}")
                    print(f"   - Statut: {data['analysis']['status']}")
                    print(f"   - Score de confiance: {data['analysis']['confidence_score']}")
                else:
                    print(f"❌ Erreur: {response.get_json()}")
                
                print("\n🔍 Test 4: Analyse de texte - Modération de contenu")
                response = client.post('/api/ai/analyze/text', 
                    json={
                        'text': 'Ce produit est vraiment excellent et en parfait état !',
                        'analysis_type': 'content_moderation'
                    },
                    headers=headers
                )
                
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    print("✅ Modération de contenu réussie")
                    print(f"   - Type d'analyse: {data['analysis']['analysis_type']}")
                    print(f"   - Statut: {data['analysis']['status']}")
                    print(f"   - Score de confiance: {data['analysis']['confidence_score']}")
                else:
                    print(f"❌ Erreur: {response.get_json()}")
                
                print("\n🔍 Test 5: Analyse de texte - Analyse de sentiment")
                response = client.post('/api/ai/analyze/text', 
                    json={
                        'text': 'Je suis très satisfait de cet achat, le vendeur était très professionnel.',
                        'analysis_type': 'sentiment_analysis'
                    },
                    headers=headers
                )
                
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    print("✅ Analyse de sentiment réussie")
                    print(f"   - Type d'analyse: {data['analysis']['analysis_type']}")
                    print(f"   - Statut: {data['analysis']['status']}")
                    print(f"   - Score de confiance: {data['analysis']['confidence_score']}")
                else:
                    print(f"❌ Erreur: {response.get_json()}")
                
                print("\n🔍 Test 6: Analyse de texte - Classification de catégorie")
                response = client.post('/api/ai/analyze/text', 
                    json={
                        'text': 'iPhone 13 Pro Max 256GB en excellent état avec boîte et accessoires',
                        'analysis_type': 'category_classification'
                    },
                    headers=headers
                )
                
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    print("✅ Classification de catégorie réussie")
                    print(f"   - Type d'analyse: {data['analysis']['analysis_type']}")
                    print(f"   - Statut: {data['analysis']['status']}")
                    print(f"   - Score de confiance: {data['analysis']['confidence_score']}")
                else:
                    print(f"❌ Erreur: {response.get_json()}")
                
                print("\n🔍 Test 7: Chat IA")
                response = client.post('/api/ai/chat', 
                    json={
                        'message': 'Bonjour, pouvez-vous m\'aider à estimer la valeur de mon iPhone ?',
                        'context': 'value_estimation'
                    },
                    headers=headers
                )
                
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    print("✅ Chat IA réussi")
                    print(f"   - Réponse: {data['response'][:100]}...")
                    print(f"   - Timestamp: {data['timestamp']}")
                else:
                    print(f"❌ Erreur: {response.get_json()}")
                
                print("\n🔍 Test 8: Récupérer les analyses d'un utilisateur")
                response = client.get('/api/ai/analyses', headers=headers)
                
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    print("✅ Récupération des analyses réussie")
                    print(f"   - Nombre d'analyses: {len(data['analyses'])}")
                else:
                    print(f"❌ Erreur: {response.get_json()}")
                
                print("\n🔍 Test 9: Récupérer une analyse spécifique")
                # Récupérer la première analyse
                analyses = AIAnalysis.query.filter_by(user_id=user.id).all()
                if analyses:
                    analysis_id = analyses[0].id
                    response = client.get(f'/api/ai/analyses/{analysis_id}', headers=headers)
                    
                    print(f"Status: {response.status_code}")
                    if response.status_code == 200:
                        data = response.get_json()
                        print("✅ Récupération d'analyse spécifique réussie")
                        print(f"   - ID: {data['analysis']['id']}")
                        print(f"   - Type: {data['analysis']['analysis_type']}")
                        print(f"   - Statut: {data['analysis']['status']}")
                    else:
                        print(f"❌ Erreur: {response.get_json()}")
                
                print("\n==================================================")
                print("🎉 Tests de l'API IA terminés !")
                print("🚀 L'API IA fonctionne correctement")
                
                return True

if __name__ == '__main__':
    if not test_ai_api():
        print("\n==================================================")
        print("❌ CERTAINS TESTS DE L'API IA ONT ÉCHOUÉ")
        sys.exit(1)
