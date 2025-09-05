"""
Lucky Kangaroo - Tests d'API
Tests d'intégration pour toutes les routes API
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

class TestAuthAPI:
    """Tests pour l'API d'authentification"""
    
    def test_register_user_success(self, client, db_session):
        """Test l'inscription réussie d'un utilisateur"""
        user_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User',
            'preferred_language': 'fr',
            'preferred_currency': 'CHF'
        }
        
        response = client.post('/api/v1/auth/register', 
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Utilisateur créé avec succès'
        assert 'user' in data
        assert data['user']['username'] == 'newuser'
        assert data['user']['email'] == 'new@example.com'
        assert 'password' not in data['user']  # Mot de passe non exposé
    
    def test_register_user_duplicate_username(self, client, db_session, sample_user):
        """Test l'inscription avec un nom d'utilisateur déjà existant"""
        user_data = {
            'username': 'testuser',  # Déjà existant
            'email': 'different@example.com',
            'password': 'SecurePass123!',
            'first_name': 'Different',
            'last_name': 'User'
        }
        
        response = client.post('/api/v1/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'username' in data['message'].lower()
    
    def test_register_user_duplicate_email(self, client, db_session, sample_user):
        """Test l'inscription avec un email déjà existant"""
        user_data = {
            'username': 'differentuser',
            'email': 'test@example.com',  # Déjà existant
            'password': 'SecurePass123!',
            'first_name': 'Different',
            'last_name': 'User'
        }
        
        response = client.post('/api/v1/auth/register',
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'email' in data['message'].lower()
    
    def test_register_user_invalid_data(self, client, db_session):
        """Test l'inscription avec des données invalides"""
        invalid_data = {
            'username': 'ab',  # Trop court
            'email': 'invalid-email',  # Format invalide
            'password': 'weak',  # Trop faible
            'first_name': '',  # Vide
            'last_name': 'User'
        }
        
        response = client.post('/api/v1/auth/register',
                             data=json.dumps(invalid_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'validation' in data['type']
    
    def test_login_user_success(self, client, db_session, sample_user):
        """Test la connexion réussie d'un utilisateur"""
        # Mock du hachage de mot de passe
        with patch('backend.models.user.check_password_hash', return_value=True):
            login_data = {
                'username': 'testuser',
                'password': 'SecurePass123!'
            }
            
            response = client.post('/api/v1/auth/login',
                                 data=json.dumps(login_data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'access_token' in data
            assert 'refresh_token' in data
            assert 'user' in data
            assert data['user']['username'] == 'testuser'
    
    def test_login_user_invalid_credentials(self, client, db_session, sample_user):
        """Test la connexion avec des identifiants invalides"""
        login_data = {
            'username': 'testuser',
            'password': 'WrongPassword123!'
        }
        
        response = client.post('/api/v1/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert 'credentials' in data['message'].lower()
    
    def test_login_user_nonexistent(self, client, db_session):
        """Test la connexion avec un utilisateur inexistant"""
        login_data = {
            'username': 'nonexistent',
            'password': 'SecurePass123!'
        }
        
        response = client.post('/api/v1/auth/login',
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data

class TestUserAPI:
    """Tests pour l'API utilisateur"""
    
    def test_get_user_profile(self, client, db_session, sample_user, auth_headers):
        """Test la récupération du profil utilisateur"""
        with patch('backend.api.v1.user_routes.get_jwt_identity', return_value=sample_user.id):
            response = client.get('/api/v1/users/profile',
                                headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['username'] == 'testuser'
            assert data['email'] == 'test@example.com'
            assert data['first_name'] == 'Test'
            assert data['last_name'] == 'User'
    
    def test_update_user_profile(self, client, db_session, sample_user, auth_headers):
        """Test la mise à jour du profil utilisateur"""
        with patch('backend.api.v1.user_routes.get_jwt_identity', return_value=sample_user.id):
            update_data = {
                'first_name': 'Updated',
                'bio': 'New bio for the user',
                'preferred_language': 'en'
            }
            
            response = client.put('/api/v1/users/profile',
                                data=json.dumps(update_data),
                                content_type='application/json',
                                headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['first_name'] == 'Updated'
            assert data['bio'] == 'New bio for the user'
            assert data['preferred_language'] == 'en'
    
    def test_update_user_profile_invalid_data(self, client, db_session, sample_user, auth_headers):
        """Test la mise à jour du profil avec des données invalides"""
        with patch('backend.api.v1.user_routes.get_jwt_identity', return_value=sample_user.id):
            invalid_data = {
                'first_name': 'A' * 100,  # Trop long
                'preferred_language': 'invalid_lang'  # Langue non supportée
            }
            
            response = client.put('/api/v1/users/profile',
                                data=json.dumps(invalid_data),
                                content_type='application/json',
                                headers=auth_headers)
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert 'validation' in data['type']
    
    def test_change_password(self, client, db_session, sample_user, auth_headers):
        """Test le changement de mot de passe"""
        with patch('backend.api.v1.user_routes.get_jwt_identity', return_value=sample_user.id), \
             patch('backend.models.user.check_password_hash', return_value=True):
            
            password_data = {
                'current_password': 'OldPass123!',
                'new_password': 'NewPass123!',
                'confirm_password': 'NewPass123!'
            }
            
            response = client.post('/api/v1/users/change-password',
                                 data=json.dumps(password_data),
                                 content_type='application/json',
                                 headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data
            assert 'mot de passe' in data['message'].lower()
    
    def test_change_password_mismatch(self, client, db_session, sample_user, auth_headers):
        """Test le changement de mot de passe avec confirmation incorrecte"""
        with patch('backend.api.v1.user_routes.get_jwt_identity', return_value=sample_user.id):
            password_data = {
                'current_password': 'OldPass123!',
                'new_password': 'NewPass123!',
                'confirm_password': 'DifferentPass123!'  # Ne correspond pas
            }
            
            response = client.post('/api/v1/users/change-password',
                                 data=json.dumps(password_data),
                                 content_type='application/json',
                                 headers=auth_headers)
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert 'correspondent' in data['message'].lower()

class TestListingAPI:
    """Tests pour l'API des annonces"""
    
    def test_create_listing_success(self, client, db_session, sample_user, auth_headers):
        """Test la création réussie d'une annonce"""
        with patch('backend.api.v1.listing_routes.get_jwt_identity', return_value=sample_user.id):
            listing_data = {
                'title': 'New Test Listing',
                'description': 'This is a new test listing with enough characters to be valid',
                'category': 'livres',
                'condition': 'excellent',
                'estimated_value': 50.0,
                'currency': 'CHF',
                'exchange_type': 'direct',
                'max_distance_km': 25
            }
            
            response = client.post('/api/v1/listings',
                                 data=json.dumps(listing_data),
                                 content_type='application/json',
                                 headers=auth_headers)
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert 'message' in data
            assert 'listing' in data
            assert data['listing']['title'] == 'New Test Listing'
            assert data['listing']['category'] == 'livres'
            assert data['listing']['user_id'] == sample_user.id
    
    def test_create_listing_invalid_data(self, client, db_session, sample_user, auth_headers):
        """Test la création d'annonce avec des données invalides"""
        with patch('backend.api.v1.listing_routes.get_jwt_identity', return_value=sample_user.id):
            invalid_data = {
                'title': 'Hi',  # Trop court
                'description': 'Short',  # Trop court
                'category': 'invalid_category',  # Catégorie inexistante
                'condition': 'invalid_condition',  # État invalide
                'estimated_value': -10,  # Valeur négative
                'currency': 'INVALID'  # Devise invalide
            }
            
            response = client.post('/api/v1/listings',
                                 data=json.dumps(invalid_data),
                                 content_type='application/json',
                                 headers=auth_headers)
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert 'validation' in data['type']
    
    def test_get_listing(self, client, db_session, sample_listing):
        """Test la récupération d'une annonce"""
        response = client.get(f'/api/v1/listings/{sample_listing.id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == sample_listing.id
        assert data['title'] == 'Test Listing'
        assert data['category'] == 'electronique'
        assert data['user_id'] == sample_listing.user_id
    
    def test_get_listing_nonexistent(self, client, db_session):
        """Test la récupération d'une annonce inexistante"""
        response = client.get('/api/v1/listings/99999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert 'not found' in data['message'].lower()
    
    def test_update_listing_success(self, client, db_session, sample_listing, sample_user, auth_headers):
        """Test la mise à jour réussie d'une annonce"""
        with patch('backend.api.v1.listing_routes.get_jwt_identity', return_value=sample_user.id):
            update_data = {
                'title': 'Updated Title',
                'description': 'Updated description with enough characters to be valid',
                'status': 'paused'
            }
            
            response = client.put(f'/api/v1/listings/{sample_listing.id}',
                                 data=json.dumps(update_data),
                                 content_type='application/json',
                                 headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['title'] == 'Updated Title'
            assert data['description'] == 'Updated description with enough characters to be valid'
            assert data['status'] == 'paused'
    
    def test_update_listing_unauthorized(self, client, db_session, sample_listing, sample_user2, auth_headers):
        """Test la mise à jour d'une annonce par un utilisateur non autorisé"""
        with patch('backend.api.v1.listing_routes.get_jwt_identity', return_value=sample_user2.id):
            update_data = {
                'title': 'Unauthorized Update'
            }
            
            response = client.put(f'/api/v1/listings/{sample_listing.id}',
                                 data=json.dumps(update_data),
                                 content_type='application/json',
                                 headers=auth_headers)
            
            assert response.status_code == 403
            data = json.loads(response.data)
            assert 'error' in data
            assert 'unauthorized' in data['message'].lower()
    
    def test_delete_listing_success(self, client, db_session, sample_listing, sample_user, auth_headers):
        """Test la suppression réussie d'une annonce"""
        with patch('backend.api.v1.listing_routes.get_jwt_identity', return_value=sample_user.id):
            response = client.delete(f'/api/v1/listings/{sample_listing.id}',
                                   headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data
            assert 'deleted' in data['message'].lower()
    
    def test_search_listings(self, client, db_session, sample_listing):
        """Test la recherche d'annonces"""
        response = client.get('/api/v1/listings/search?q=test&category=electronique')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'results' in data
        assert 'total' in data
        assert 'page' in data
        assert 'per_page' in data

class TestExchangeAPI:
    """Tests pour l'API des échanges"""
    
    def test_create_exchange_success(self, client, db_session, sample_user, sample_listing, sample_listing2, auth_headers):
        """Test la création réussie d'un échange"""
        with patch('backend.api.v1.exchange_routes.get_jwt_identity', return_value=sample_user.id):
            exchange_data = {
                'requested_listing_id': sample_listing2.id,
                'offered_listing_id': sample_listing.id,
                'message': 'I would like to exchange these items',
                'exchange_type': 'direct'
            }
            
            response = client.post('/api/v1/exchanges',
                                 data=json.dumps(exchange_data),
                                 content_type='application/json',
                                 headers=auth_headers)
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert 'message' in data
            assert 'exchange' in data
            assert data['exchange']['requester_id'] == sample_user.id
            assert data['exchange']['status'] == 'requested'
    
    def test_create_exchange_invalid_data(self, client, db_session, sample_user, auth_headers):
        """Test la création d'échange avec des données invalides"""
        with patch('backend.api.v1.exchange_routes.get_jwt_identity', return_value=sample_user.id):
            invalid_data = {
                'requested_listing_id': 99999,  # Annonce inexistante
                'offered_listing_id': 99998,  # Annonce inexistante
                'message': 'URGENT!!! GRATUIT!!! $$$',  # Contient du spam
                'exchange_type': 'invalid_type'  # Type invalide
            }
            
            response = client.post('/api/v1/exchanges',
                                 data=json.dumps(invalid_data),
                                 content_type='application/json',
                                 headers=auth_headers)
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
    
    def test_get_exchange(self, client, db_session, sample_exchange):
        """Test la récupération d'un échange"""
        response = client.get(f'/api/v1/exchanges/{sample_exchange.id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == sample_exchange.id
        assert data['status'] == 'requested'
        assert data['exchange_type'] == 'direct'
    
    def test_update_exchange_status(self, client, db_session, sample_exchange, sample_user2, auth_headers):
        """Test la mise à jour du statut d'un échange"""
        with patch('backend.api.v1.exchange_routes.get_jwt_identity', return_value=sample_user2.id):
            update_data = {
                'status': 'accepted',
                'message': 'I accept this exchange'
            }
            
            response = client.put(f'/api/v1/exchanges/{sample_exchange.id}',
                                 data=json.dumps(update_data),
                                 content_type='application/json',
                                 headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'accepted'
    
    def test_respond_to_exchange(self, client, db_session, sample_exchange, sample_user2, auth_headers):
        """Test la réponse à un échange"""
        with patch('backend.api.v1.exchange_routes.get_jwt_identity', return_value=sample_user2.id):
            response_data = {
                'action': 'accept',
                'message': 'I accept this exchange'
            }
            
            response = client.post(f'/api/v1/exchanges/{sample_exchange.id}/respond',
                                 data=json.dumps(response_data),
                                 content_type='application/json',
                                 headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data

class TestChatAPI:
    """Tests pour l'API du chat"""
    
    def test_create_chat_room(self, client, db_session, sample_user, sample_user2, auth_headers):
        """Test la création d'une salle de chat"""
        with patch('backend.api.v1.chat_routes.get_jwt_identity', return_value=sample_user.id):
            chat_data = {
                'user2_id': sample_user2.id
            }
            
            response = client.post('/api/v1/chat/rooms',
                                 data=json.dumps(chat_data),
                                 content_type='application/json',
                                 headers=auth_headers)
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert 'chat_room' in data
            assert data['chat_room']['user1_id'] == sample_user.id
            assert data['chat_room']['user2_id'] == sample_user2.id
    
    def test_send_message(self, client, db_session, sample_chat_room, sample_user, auth_headers):
        """Test l'envoi d'un message"""
        with patch('backend.api.v1.chat_routes.get_jwt_identity', return_value=sample_user.id):
            message_data = {
                'content': 'Hello, this is a test message',
                'message_type': 'text'
            }
            
            response = client.post(f'/api/v1/chat/rooms/{sample_chat_room.id}/messages',
                                 data=json.dumps(message_data),
                                 content_type='application/json',
                                 headers=auth_headers)
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert 'message' in data
            assert data['message']['content'] == 'Hello, this is a test message'
            assert data['message']['sender_id'] == sample_user.id
    
    def test_get_chat_messages(self, client, db_session, sample_chat_room, sample_user, auth_headers):
        """Test la récupération des messages d'une salle de chat"""
        with patch('backend.api.v1.chat_routes.get_jwt_identity', return_value=sample_user.id):
            response = client.get(f'/api/v1/chat/rooms/{sample_chat_room.id}/messages',
                                headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'messages' in data
            assert isinstance(data['messages'], list)
    
    def test_search_chat_messages(self, client, db_session, sample_chat_room, sample_user, auth_headers):
        """Test la recherche dans les messages de chat"""
        with patch('backend.api.v1.chat_routes.get_jwt_identity', return_value=sample_user.id):
            response = client.get(f'/api/v1/chat/rooms/{sample_chat_room.id}/search?q=test',
                                headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'results' in data

class TestPaymentAPI:
    """Tests pour l'API des paiements"""
    
    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent(self, mock_stripe, client, db_session, sample_user, auth_headers):
        """Test la création d'une intention de paiement"""
        with patch('backend.api.v1.payments.get_jwt_identity', return_value=sample_user.id):
            # Mock Stripe
            mock_stripe.return_value = MagicMock(id='pi_test123', status='requires_payment_method')
            
            payment_data = {
                'amount': 9999,  # 99.99 CHF
                'currency': 'CHF',
                'description': 'Test payment'
            }
            
            response = client.post('/api/v1/payments/create-intent',
                                 data=json.dumps(payment_data),
                                 content_type='application/json',
                                 headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'client_secret' in data
            assert 'payment_intent_id' in data
    
    def test_create_payment_intent_invalid_amount(self, client, db_session, sample_user, auth_headers):
        """Test la création d'une intention de paiement avec un montant invalide"""
        with patch('backend.api.v1.payments.get_jwt_identity', return_value=sample_user.id):
            invalid_data = {
                'amount': 15000,  # Trop élevé
                'currency': 'CHF'
            }
            
            response = client.post('/api/v1/payments/create-intent',
                                 data=json.dumps(invalid_data),
                                 content_type='application/json',
                                 headers=auth_headers)
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
    
    @patch('stripe.PaymentMethod.create')
    def test_create_payment_method(self, mock_stripe, client, db_session, sample_user, auth_headers):
        """Test la création d'une méthode de paiement"""
        with patch('backend.api.v1.payments.get_jwt_identity', return_value=sample_user.id):
            # Mock Stripe
            mock_stripe.return_value = MagicMock(id='pm_test123')
            
            payment_method_data = {
                'type': 'card',
                'token': 'tok_test123',
                'is_default': True
            }
            
            response = client.post('/api/v1/payments/methods',
                                 data=json.dumps(payment_method_data),
                                 content_type='application/json',
                                 headers=auth_headers)
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert 'payment_method' in data
            assert data['payment_method']['type'] == 'card'

class TestSearchAPI:
    """Tests pour l'API de recherche"""
    
    def test_search_listings(self, client, db_session, sample_listing):
        """Test la recherche d'annonces"""
        response = client.get('/api/v1/search?q=test&category=electronique&max_price=200')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'results' in data
        assert 'total' in data
        assert 'page' in data
        assert 'per_page' in data
    
    def test_search_listings_invalid_filters(self, client, db_session):
        """Test la recherche avec des filtres invalides"""
        response = client.get('/api/v1/search?max_price=invalid&min_price=-10')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_search_suggestions(self, client, db_session):
        """Test les suggestions de recherche"""
        response = client.get('/api/v1/search/suggestions?q=elec')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'suggestions' in data
        assert isinstance(data['suggestions'], list)

class TestAIAPI:
    """Tests pour l'API d'IA"""
    
    @patch('backend.services.ai_service.AIService.analyze_image')
    def test_analyze_image(self, mock_ai, client, db_session, sample_user, auth_headers):
        """Test l'analyse d'image par l'IA"""
        with patch('backend.api.v1.ai_routes.get_jwt_identity', return_value=sample_user.id):
            # Mock du service IA
            mock_ai.return_value = {
                'category': 'electronique',
                'confidence': 0.95,
                'tags': ['smartphone', 'mobile'],
                'estimated_value': 500.0
            }
            
            # Simuler un fichier d'image
            image_data = b'fake_image_data'
            
            response = client.post('/api/v1/ai/analyze-image',
                                 data={'image': (image_data, 'test.jpg')},
                                 headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'analysis' in data
            assert data['analysis']['category'] == 'electronique'
            assert data['analysis']['confidence'] == 0.95
    
    @patch('backend.services.ai_service.AIService.generate_description')
    def test_generate_description(self, mock_ai, client, db_session, sample_user, auth_headers):
        """Test la génération de description par l'IA"""
        with patch('backend.api.v1.ai_routes.get_jwt_identity', return_value=sample_user.id):
            # Mock du service IA
            mock_ai.return_value = "Description générée par l'IA pour cet objet"
            
            description_data = {
                'category': 'livres',
                'condition': 'excellent',
                'brand': 'Test Brand',
                'model': 'Test Model'
            }
            
            response = client.post('/api/v1/ai/generate-description',
                                 data=json.dumps(description_data),
                                 content_type='application/json',
                                 headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'description' in data
            assert 'générée par l\'IA' in data['description']
    
    @patch('backend.services.ai_service.AIService.moderate_content')
    def test_moderate_content(self, mock_ai, client, db_session, sample_user, auth_headers):
        """Test la modération de contenu par l'IA"""
        with patch('backend.api.v1.ai_routes.get_jwt_identity', return_value=sample_user.id):
            # Mock du service IA
            mock_ai.return_value = {
                'is_appropriate': True,
                'confidence': 0.98,
                'flags': []
            }
            
            content_data = {
                'text': 'This is appropriate content for testing',
                'content_type': 'listing_description'
            }
            
            response = client.post('/api/v1/ai/moderate',
                                 data=json.dumps(content_data),
                                 content_type='application/json',
                                 headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'moderation' in data
            assert data['moderation']['is_appropriate'] is True

class TestGeolocationAPI:
    """Tests pour l'API de géolocalisation"""
    
    @patch('backend.services.geolocation_service.GeolocationService.get_coordinates_from_address')
    def test_get_coordinates_from_address(self, mock_geo, client, db_session):
        """Test la récupération de coordonnées depuis une adresse"""
        # Mock du service de géolocalisation
        mock_geo.return_value = {
            'latitude': 46.9481,
            'longitude': 7.4474
        }
        
        response = client.get('/api/v1/geolocation/coordinates?address=Bern, Switzerland')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'coordinates' in data
        assert data['coordinates']['latitude'] == 46.9481
        assert data['coordinates']['longitude'] == 7.4474
    
    @patch('backend.services.geolocation_service.GeolocationService.calculate_distance')
    def test_calculate_distance(self, mock_geo, client, db_session):
        """Test le calcul de distance entre deux points"""
        # Mock du service de géolocalisation
        mock_geo.return_value = 5.2  # km
        
        response = client.get('/api/v1/geolocation/distance?lat1=46.9481&lon1=7.4474&lat2=46.9516&lon2=7.4386')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'distance' in data
        assert data['distance'] == 5.2
    
    @patch('backend.services.geolocation_service.GeolocationService.get_nearby_cities')
    def test_get_nearby_cities(self, mock_geo, client, db_session):
        """Test la récupération des villes à proximité"""
        # Mock du service de géolocalisation
        mock_geo.return_value = [
            {'name': 'Bern', 'distance': 5.2},
            {'name': 'Thun', 'distance': 15.8}
        ]
        
        response = client.get('/api/v1/geolocation/nearby-cities?lat=46.9481&lon=7.4474&radius=20')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'cities' in data
        assert len(data['cities']) == 2
        assert data['cities'][0]['name'] == 'Bern'
        assert data['cities'][1]['name'] == 'Thun'

class TestAdminAPI:
    """Tests pour l'API d'administration"""
    
    def test_admin_access_required(self, client, db_session, sample_user, auth_headers):
        """Test que l'accès admin est requis pour les routes protégées"""
        with patch('backend.api.v1.admin_routes.get_jwt_identity', return_value=sample_user.id):
            # L'utilisateur n'est pas admin
            response = client.get('/api/v1/admin/users',
                                headers=auth_headers)
            
            assert response.status_code == 403
            data = json.loads(response.data)
            assert 'error' in data
            assert 'admin' in data['message'].lower()
    
    def test_admin_get_users(self, client, db_session, sample_user, auth_headers):
        """Test la récupération des utilisateurs par un admin"""
        # Mock l'utilisateur comme admin
        sample_user.is_admin = True
        
        with patch('backend.api.v1.admin_routes.get_jwt_identity', return_value=sample_user.id):
            response = client.get('/api/v1/admin/users',
                                headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'users' in data
            assert isinstance(data['users'], list)
    
    def test_admin_get_statistics(self, client, db_session, sample_user, auth_headers):
        """Test la récupération des statistiques par un admin"""
        # Mock l'utilisateur comme admin
        sample_user.is_admin = True
        
        with patch('backend.api.v1.admin_routes.get_jwt_identity', return_value=sample_user.id):
            response = client.get('/api/v1/admin/statistics',
                                headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'statistics' in data
            assert 'total_users' in data['statistics']
            assert 'total_listings' in data['statistics']
            assert 'total_exchanges' in data['statistics']

class TestErrorHandling:
    """Tests pour la gestion d'erreurs"""
    
    def test_404_not_found(self, client):
        """Test la gestion des routes non trouvées"""
        response = client.get('/api/v1/nonexistent')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert 'not found' in data['message'].lower()
        assert 'available_endpoints' in data
    
    def test_405_method_not_allowed(self, client):
        """Test la gestion des méthodes HTTP non autorisées"""
        response = client.post('/api/v1/listings')  # POST sur une route qui n'existe pas
        
        assert response.status_code == 405
        data = json.loads(response.data)
        assert 'error' in data
        assert 'method not allowed' in data['message'].lower()
    
    def test_validation_error_handling(self, client, db_session):
        """Test la gestion des erreurs de validation"""
        invalid_data = {
            'username': '',  # Vide
            'email': 'invalid-email',  # Format invalide
            'password': '123'  # Trop court
        }
        
        response = client.post('/api/v1/auth/register',
                             data=json.dumps(invalid_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'validation' in data['type']
        assert 'details' in data
    
    def test_database_error_handling(self, client, db_session, sample_user, auth_headers):
        """Test la gestion des erreurs de base de données"""
        with patch('backend.api.v1.user_routes.get_jwt_identity', return_value=sample_user.id), \
             patch('backend.models.user.User.query') as mock_query:
            
            # Simuler une erreur de base de données
            mock_query.filter_by.side_effect = Exception("Database connection error")
            
            response = client.get('/api/v1/users/profile',
                                headers=auth_headers)
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert 'database' in data['type']
