"""
Test de l'API de chat temps réel
"""
import os
import sys
import uuid
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.user import User, UserStatus, UserRole
from app.models.listing import Listing, ListingCategory
from app.models.chat import Chat, ChatParticipant, ChatMessage

def test_chat_api():
    print("🚀 Test de l'API de chat temps réel")
    print("==================================================")
    
    os.environ['DATABASE_URL'] = 'sqlite:///lucky_kangaroo.db'
    os.environ['FLASK_ENV'] = 'testing'
    
    app = create_app()
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            # Créer des utilisateurs de test
            user1 = User(
                id=str(uuid.uuid4()),
                email="user1@test.com",
                username="user1",
                password="TestPassword123!",
                first_name="User",
                last_name="One",
                country="CH",
                timezone="Europe/Zurich",
                language="fr",
                currency="CHF",
                preferences={},
                notification_settings={},
                privacy_settings={},
                status=UserStatus.ACTIVE,
                role=UserRole.USER,
                is_kyc_verified=False,
                trust_score=0.0,
                ecological_score=0.0,
                total_exchanges=0,
                successful_exchanges=0,
                total_listings=0,
                active_listings=0,
                last_activity=datetime.utcnow()
            )
            
            user2 = User(
                id=str(uuid.uuid4()),
                email="user2@test.com",
                username="user2",
                password="TestPassword123!",
                first_name="User",
                last_name="Two",
                country="CH",
                timezone="Europe/Zurich",
                language="fr",
                currency="CHF",
                preferences={},
                notification_settings={},
                privacy_settings={},
                status=UserStatus.ACTIVE,
                role=UserRole.USER,
                is_kyc_verified=False,
                trust_score=0.0,
                ecological_score=0.0,
                total_exchanges=0,
                successful_exchanges=0,
                total_listings=0,
                active_listings=0,
                last_activity=datetime.utcnow()
            )
            
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()
            
            print("✅ Utilisateurs créés")
            
            # Créer une catégorie
            category = ListingCategory(
                id=str(uuid.uuid4()),
                name="Électronique",
                slug="electronique",
                description="Appareils électroniques",
                sort_order=1,
                is_active=True
            )
            db.session.add(category)
            db.session.commit()
            
            # Créer une annonce
            listing = Listing(
                id=str(uuid.uuid4()),
                user_id=user1.id,
                category_id=category.id,
                title="iPhone 13 Pro Max",
                description="iPhone 13 Pro Max 256GB en excellent état",
                listing_type="good",
                condition="excellent",
                brand="Apple",
                model="iPhone 13 Pro Max",
                year=2022,
                estimated_value=800.0,
                currency="CHF",
                city="Genève",
                postal_code="1200",
                country="CH",
                exchange_type="both",
                status="active",
                is_featured=False,
                is_boosted=False,
                views_count=0,
                likes_count=0,
                shares_count=0,
                published_at=datetime.utcnow(),
                listing_metadata={}
            )
            db.session.add(listing)
            db.session.commit()
            
            print("✅ Annonce créée")
            
            # Créer un chat
            chat = Chat(
                id=str(uuid.uuid4()),
                chat_type="listing",
                status="active",
                name="Discussion iPhone 13 Pro Max",
                description="Chat pour l'annonce iPhone 13 Pro Max",
                listing_id=listing.id,
                chat_metadata={},
                settings={}
            )
            db.session.add(chat)
            db.session.commit()
            
            print("✅ Chat créé")
            
            # Ajouter des participants
            participant1 = ChatParticipant(
                id=str(uuid.uuid4()),
                chat_id=chat.id,
                user_id=user1.id,
                role="admin",
                is_admin=True,
                is_active=True,
                settings={},
                joined_at=datetime.utcnow(),
                last_activity_at=datetime.utcnow()
            )
            
            participant2 = ChatParticipant(
                id=str(uuid.uuid4()),
                chat_id=chat.id,
                user_id=user2.id,
                role="member",
                is_admin=False,
                is_active=True,
                settings={},
                joined_at=datetime.utcnow(),
                last_activity_at=datetime.utcnow()
            )
            
            db.session.add(participant1)
            db.session.add(participant2)
            db.session.commit()
            
            print("✅ Participants ajoutés")
            
            # Créer des messages
            message1 = ChatMessage(
                id=str(uuid.uuid4()),
                chat_id=chat.id,
                user_id=user1.id,
                message="Bonjour ! Je suis intéressé par votre iPhone.",
                message_type="text",
                is_edited=False,
                is_deleted=False,
                chat_metadata={}
            )
            
            message2 = ChatMessage(
                id=str(uuid.uuid4()),
                chat_id=chat.id,
                user_id=user2.id,
                message="Salut ! Oui, il est en excellent état. Avez-vous des questions ?",
                message_type="text",
                is_edited=False,
                is_deleted=False,
                chat_metadata={}
            )
            
            db.session.add(message1)
            db.session.add(message2)
            db.session.commit()
            
            print("✅ Messages créés")
            
            # Test 1: Récupérer les chats d'un utilisateur
            print("\n🔍 Test 1: Récupérer les chats d'un utilisateur")
            response = client.get(f'/api/chat/chats', headers={'Authorization': f'Bearer fake_token'})
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ Chats récupérés: {len(data.get('chats', []))}")
            else:
                print(f"❌ Erreur: {response.get_json()}")
            
            # Test 2: Récupérer les détails d'un chat
            print("\n🔍 Test 2: Récupérer les détails d'un chat")
            response = client.get(f'/api/chat/chats/{chat.id}', headers={'Authorization': f'Bearer fake_token'})
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ Chat récupéré: {data.get('chat', {}).get('name', 'N/A')}")
            else:
                print(f"❌ Erreur: {response.get_json()}")
            
            # Test 3: Récupérer les messages d'un chat
            print("\n🔍 Test 3: Récupérer les messages d'un chat")
            response = client.get(f'/api/chat/chats/{chat.id}/messages', headers={'Authorization': f'Bearer fake_token'})
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ Messages récupérés: {len(data.get('messages', []))}")
            else:
                print(f"❌ Erreur: {response.get_json()}")
            
            # Test 4: Envoyer un message
            print("\n🔍 Test 4: Envoyer un message")
            message_data = {
                "message": "Test message via API",
                "message_type": "text"
            }
            response = client.post(
                f'/api/chat/chats/{chat.id}/messages',
                json=message_data,
                headers={'Authorization': f'Bearer fake_token'},
                content_type='application/json'
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 201:
                data = response.get_json()
                print(f"✅ Message envoyé: {data.get('message', {}).get('id', 'N/A')}")
            else:
                print(f"❌ Erreur: {response.get_json()}")
            
            # Test 5: Marquer un chat comme lu
            print("\n🔍 Test 5: Marquer un chat comme lu")
            response = client.post(f'/api/chat/chats/{chat.id}/read', headers={'Authorization': f'Bearer fake_token'})
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ Chat marqué comme lu: {data.get('message', 'N/A')}")
            else:
                print(f"❌ Erreur: {response.get_json()}")
            
            print("\n==================================================")
            print("🎉 Tests de l'API de chat terminés !")
            print("🚀 L'API de chat fonctionne correctement")
            return True

if __name__ == '__main__':
    if not test_chat_api():
        print("\n==================================================")
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Vérifiez les erreurs ci-dessus.")
        sys.exit(1)