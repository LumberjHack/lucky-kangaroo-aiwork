"""
Lucky Kangaroo - Tests des schémas de validation
Tests unitaires pour les schémas Marshmallow
"""

import pytest
from datetime import date, datetime, timedelta
from marshmallow import ValidationError

from backend.schemas.user import (
    UserSchema, CreateUserSchema, UpdateUserSchema, ChangePasswordSchema
)
from backend.schemas.listing import (
    ListingSchema, CreateListingSchema, UpdateListingSchema
)
from backend.schemas.exchange import (
    ExchangeSchema, CreateExchangeSchema, UpdateExchangeSchema, ExchangeResponseSchema
)
from backend.schemas.chat import (
    ChatMessageSchema, CreateChatMessageSchema, UpdateChatMessageSchema,
    ChatRoomSchema, CreateChatRoomSchema, ChatReactionSchema, ChatSearchSchema
)
from backend.schemas.payment import (
    PaymentSchema, CreatePaymentSchema, SubscriptionPlanSchema,
    CreateSubscriptionSchema, UpdateSubscriptionSchema, PaymentMethodSchema,
    CreatePaymentMethodSchema, UpdatePaymentMethodSchema, RefundSchema,
    InvoiceSchema, CreateInvoiceSchema
)

class TestUserSchemas:
    """Tests pour les schémas d'utilisateur"""
    
    def test_user_schema_serialization(self):
        """Test la sérialisation du schéma utilisateur"""
        user_data = {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'trust_score': 85.5,
            'reputation_score': 92.0,
            'is_active': True,
            'created_at': datetime.utcnow()
        }
        
        schema = UserSchema()
        result = schema.dump(user_data)
        
        assert result['username'] == 'testuser'
        assert result['email'] == 'test@example.com'
        assert result['trust_score'] == 85.5
        assert 'password_hash' not in result  # Champ protégé
    
    def test_create_user_schema_valid_data(self):
        """Test la validation de données valides pour la création d'utilisateur"""
        valid_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User',
            'phone': '+33123456789',
            'date_of_birth': '1990-01-01',
            'preferred_language': 'fr',
            'preferred_currency': 'EUR'
        }
        
        schema = CreateUserSchema()
        result = schema.load(valid_data)
        
        assert result['username'] == 'newuser'
        assert result['email'] == 'new@example.com'
        assert result['password'] == 'SecurePass123!'
        assert result['preferred_language'] == 'fr'
        assert result['preferred_currency'] == 'EUR'
    
    def test_create_user_schema_invalid_username(self):
        """Test la validation d'un nom d'utilisateur invalide"""
        invalid_data = {
            'username': 'admin',  # Nom réservé
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        schema = CreateUserSchema()
        with pytest.raises(ValidationError, match="Ce nom d'utilisateur n'est pas autorisé"):
            schema.load(invalid_data)
    
    def test_create_user_schema_weak_password(self):
        """Test la validation d'un mot de passe faible"""
        invalid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'weak',  # Mot de passe trop court
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        schema = CreateUserSchema()
        with pytest.raises(ValidationError, match="Le mot de passe doit contenir au moins 8 caractères"):
            schema.load(invalid_data)
    
    def test_create_user_schema_invalid_date_of_birth(self):
        """Test la validation d'une date de naissance invalide"""
        invalid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'date_of_birth': '2015-01-01'  # Trop jeune
        }
        
        schema = CreateUserSchema()
        with pytest.raises(ValidationError, match="L'utilisateur doit avoir au moins 13 ans"):
            schema.load(invalid_data)
    
    def test_update_user_schema_partial_update(self):
        """Test la mise à jour partielle d'un utilisateur"""
        update_data = {
            'first_name': 'Updated',
            'bio': 'New bio for the user',
            'preferred_language': 'en'
        }
        
        schema = UpdateUserSchema()
        result = schema.load(update_data)
        
        assert result['first_name'] == 'Updated'
        assert result['bio'] == 'New bio for the user'
        assert result['preferred_language'] == 'en'
    
    def test_change_password_schema_mismatch(self):
        """Test la validation de la confirmation de mot de passe"""
        invalid_data = {
            'current_password': 'OldPass123!',
            'new_password': 'NewPass123!',
            'confirm_password': 'DifferentPass123!'  # Ne correspond pas
        }
        
        schema = ChangePasswordSchema()
        with pytest.raises(ValidationError, match="Les mots de passe ne correspondent pas"):
            schema.load(invalid_data)

class TestListingSchemas:
    """Tests pour les schémas d'annonce"""
    
    def test_listing_schema_serialization(self):
        """Test la sérialisation du schéma d'annonce"""
        listing_data = {
            'id': 1,
            'title': 'Test Listing',
            'description': 'Test description',
            'category': 'electronique',
            'estimated_value': 100.0,
            'currency': 'CHF',
            'status': 'active',
            'created_at': datetime.utcnow()
        }
        
        schema = ListingSchema()
        result = schema.dump(listing_data)
        
        assert result['title'] == 'Test Listing'
        assert result['category'] == 'electronique'
        assert result['estimated_value'] == 100.0
        assert result['currency'] == 'CHF'
    
    def test_create_listing_schema_valid_data(self):
        """Test la validation de données valides pour la création d'annonce"""
        valid_data = {
            'title': 'New Listing',
            'description': 'This is a new listing with enough characters to be valid',
            'category': 'livres',
            'condition': 'excellent',
            'estimated_value': 50.0,
            'currency': 'EUR',
            'exchange_type': 'direct',
            'max_distance_km': 25
        }
        
        schema = CreateListingSchema()
        result = schema.load(valid_data)
        
        assert result['title'] == 'New Listing'
        assert result['category'] == 'livres'
        assert result['estimated_value'] == 50.0
        assert result['currency'] == 'EUR'
    
    def test_create_listing_schema_title_too_short(self):
        """Test la validation d'un titre trop court"""
        invalid_data = {
            'title': 'Hi',  # Trop court
            'description': 'Valid description with enough characters',
            'category': 'livres',
            'condition': 'good',
            'estimated_value': 50.0,
            'currency': 'CHF'
        }
        
        schema = CreateListingSchema()
        with pytest.raises(ValidationError, match="Le titre doit contenir entre 5 et 200 caractères"):
            schema.load(invalid_data)
    
    def test_create_listing_schema_invalid_category(self):
        """Test la validation d'une catégorie invalide"""
        invalid_data = {
            'title': 'Valid Title',
            'description': 'Valid description with enough characters',
            'category': 'invalid_category',  # Catégorie inexistante
            'condition': 'good',
            'estimated_value': 50.0,
            'currency': 'CHF'
        }
        
        schema = CreateListingSchema()
        with pytest.raises(ValidationError, match="Catégorie invalide"):
            schema.load(invalid_data)
    
    def test_create_listing_schema_spam_title(self):
        """Test la validation d'un titre contenant du spam"""
        invalid_data = {
            'title': 'URGENT!!! GRATUIT!!!',  # Contient des indicateurs de spam
            'description': 'Valid description with enough characters',
            'category': 'livres',
            'condition': 'good',
            'estimated_value': 50.0,
            'currency': 'CHF'
        }
        
        schema = CreateListingSchema()
        with pytest.raises(ValidationError, match="Le titre contient des mots interdits"):
            schema.load(invalid_data)
    
    def test_update_listing_schema_partial_update(self):
        """Test la mise à jour partielle d'une annonce"""
        update_data = {
            'title': 'Updated Title',
            'description': 'Updated description with enough characters',
            'status': 'paused'
        }
        
        schema = UpdateListingSchema()
        result = schema.load(update_data)
        
        assert result['title'] == 'Updated Title'
        assert result['description'] == 'Updated description with enough characters'
        assert result['status'] == 'paused'

class TestExchangeSchemas:
    """Tests pour les schémas d'échange"""
    
    def test_exchange_schema_serialization(self):
        """Test la sérialisation du schéma d'échange"""
        exchange_data = {
            'id': 1,
            'requester_id': 1,
            'owner_id': 2,
            'offered_listing_id': 1,
            'requested_listing_id': 2,
            'exchange_type': 'direct',
            'status': 'requested',
            'created_at': datetime.utcnow()
        }
        
        schema = ExchangeSchema()
        result = schema.dump(exchange_data)
        
        assert result['requester_id'] == 1
        assert result['owner_id'] == 2
        assert result['exchange_type'] == 'direct'
        assert result['status'] == 'requested'
    
    def test_create_exchange_schema_valid_data(self):
        """Test la validation de données valides pour la création d'échange"""
        valid_data = {
            'requested_listing_id': 1,
            'offered_listing_id': 2,
            'message': 'I would like to exchange these items',
            'exchange_type': 'direct'
        }
        
        schema = CreateExchangeSchema()
        result = schema.load(valid_data)
        
        assert result['requested_listing_id'] == 1
        assert result['offered_listing_id'] == 2
        assert result['message'] == 'I would like to exchange these items'
        assert result['exchange_type'] == 'direct'
    
    def test_create_exchange_schema_spam_message(self):
        """Test la validation d'un message contenant du spam"""
        invalid_data = {
            'requested_listing_id': 1,
            'offered_listing_id': 2,
            'message': 'URGENT!!! GRATUIT!!! $$$',  # Contient du spam
            'exchange_type': 'direct'
        }
        
        schema = CreateExchangeSchema()
        with pytest.raises(ValidationError, match="Le message contient des indicateurs de spam"):
            schema.load(invalid_data)
    
    def test_update_exchange_schema_meeting_datetime_past(self):
        """Test la validation d'une date de rendez-vous dans le passé"""
        past_date = datetime.utcnow() - timedelta(days=1)
        invalid_data = {
            'meeting_datetime': past_date.isoformat(),
            'meeting_location': 'Test Location'
        }
        
        schema = UpdateExchangeSchema()
        with pytest.raises(ValidationError, match="La date du rendez-vous ne peut pas être dans le passé"):
            schema.load(invalid_data)
    
    def test_exchange_response_schema_valid_data(self):
        """Test la validation de données valides pour la réponse d'échange"""
        valid_data = {
            'action': 'accept',
            'message': 'I accept this exchange'
        }
        
        schema = ExchangeResponseSchema()
        result = schema.load(valid_data)
        
        assert result['action'] == 'accept'
        assert result['message'] == 'I accept this exchange'
    
    def test_exchange_response_schema_counter_offer_missing_listing(self):
        """Test la validation d'une contre-proposition sans annonce"""
        invalid_data = {
            'action': 'counter_offer',
            'message': 'Here is my counter offer'
            # Manque counter_offered_listing_id
        }
        
        schema = ExchangeResponseSchema()
        with pytest.raises(ValidationError, match="L'ID de l'annonce de contre-proposition est requis"):
            schema.load(invalid_data)

class TestChatSchemas:
    """Tests pour les schémas de chat"""
    
    def test_chat_message_schema_serialization(self):
        """Test la sérialisation du schéma de message de chat"""
        message_data = {
            'id': 1,
            'chat_room_id': 1,
            'sender_id': 1,
            'content': 'Hello world',
            'message_type': 'text',
            'status': 'sent',
            'created_at': datetime.utcnow()
        }
        
        schema = ChatMessageSchema()
        result = schema.dump(message_data)
        
        assert result['content'] == 'Hello world'
        assert result['message_type'] == 'text'
        assert result['status'] == 'sent'
    
    def test_create_chat_message_schema_valid_data(self):
        """Test la validation de données valides pour la création de message"""
        valid_data = {
            'content': 'Hello, this is a test message',
            'message_type': 'text'
        }
        
        schema = CreateChatMessageSchema()
        result = schema.load(valid_data)
        
        assert result['content'] == 'Hello, this is a test message'
        assert result['message_type'] == 'text'
    
    def test_create_chat_message_schema_spam_content(self):
        """Test la validation d'un contenu contenant du spam"""
        invalid_data = {
            'content': 'URGENT!!! GRATUIT!!! $$$',  # Contient du spam
            'message_type': 'text'
        }
        
        schema = CreateChatMessageSchema()
        with pytest.raises(ValidationError, match="Le contenu contient des indicateurs de spam"):
            schema.load(invalid_data)
    
    def test_create_chat_message_schema_external_link(self):
        """Test la validation d'un lien externe non autorisé"""
        invalid_data = {
            'content': 'Check this out: http://suspicious-site.com',
            'message_type': 'text'
        }
        
        schema = CreateChatMessageSchema()
        with pytest.raises(ValidationError, match="Les liens externes ne sont pas autorisés"):
            schema.load(invalid_data)
    
    def test_chat_reaction_schema_valid_data(self):
        """Test la validation de données valides pour les réactions"""
        valid_data = {
            'reaction_type': 'like'
        }
        
        schema = ChatReactionSchema()
        result = schema.load(valid_data)
        
        assert result['reaction_type'] == 'like'
    
    def test_chat_search_schema_date_range_validation(self):
        """Test la validation de la plage de dates pour la recherche"""
        now = datetime.utcnow()
        past_date = now - timedelta(days=1)
        future_date = now + timedelta(days=1)
        
        invalid_data = {
            'date_from': future_date.isoformat(),
            'date_to': past_date.isoformat()  # Date de fin avant date de début
        }
        
        schema = ChatSearchSchema()
        with pytest.raises(ValidationError, match="La date de fin doit être postérieure à la date de début"):
            schema.load(invalid_data)

class TestPaymentSchemas:
    """Tests pour les schémas de paiement"""
    
    def test_payment_schema_serialization(self):
        """Test la sérialisation du schéma de paiement"""
        payment_data = {
            'id': 'pi_test123',
            'user_id': 1,
            'amount': 99.99,
            'currency': 'CHF',
            'status': 'succeeded',
            'created_at': datetime.utcnow()
        }
        
        schema = PaymentSchema()
        result = schema.dump(payment_data)
        
        assert result['id'] == 'pi_test123'
        assert result['amount'] == 99.99
        assert result['currency'] == 'CHF'
        assert result['status'] == 'succeeded'
    
    def test_create_payment_schema_valid_data(self):
        """Test la validation de données valides pour la création de paiement"""
        valid_data = {
            'amount': 99.99,
            'currency': 'CHF',
            'description': 'Test payment'
        }
        
        schema = CreatePaymentSchema()
        result = schema.load(valid_data)
        
        assert result['amount'] == 99.99
        assert result['currency'] == 'CHF'
        assert result['description'] == 'Test payment'
    
    def test_create_payment_schema_amount_too_high(self):
        """Test la validation d'un montant trop élevé"""
        invalid_data = {
            'amount': 15000.0,  # Au-dessus de la limite
            'currency': 'CHF'
        }
        
        schema = CreatePaymentSchema()
        with pytest.raises(ValidationError, match="Le montant doit être compris entre 0.01 et 10 000"):
            schema.load(invalid_data)
    
    def test_create_payment_schema_invalid_currency(self):
        """Test la validation d'une devise invalide"""
        invalid_data = {
            'amount': 99.99,
            'currency': 'INVALID'  # Devise non supportée
        }
        
        schema = CreatePaymentSchema()
        with pytest.raises(ValidationError, match="Devise non supportée"):
            schema.load(invalid_data)
    
    def test_refund_schema_valid_data(self):
        """Test la validation de données valides pour le remboursement"""
        valid_data = {
            'payment_id': 'pi_test123',
            'reason': 'requested_by_customer',
            'description': 'Customer requested refund'
        }
        
        schema = RefundSchema()
        result = schema.load(valid_data)
        
        assert result['payment_id'] == 'pi_test123'
        assert result['reason'] == 'requested_by_customer'
        assert result['description'] == 'Customer requested refund'
    
    def test_refund_schema_invalid_reason(self):
        """Test la validation d'une raison de remboursement invalide"""
        invalid_data = {
            'payment_id': 'pi_test123',
            'reason': 'invalid_reason'  # Raison non supportée
        }
        
        schema = RefundSchema()
        with pytest.raises(ValidationError, match="Raison de remboursement invalide"):
            schema.load(invalid_data)
    
    def test_create_invoice_schema_date_validation(self):
        """Test la validation des dates pour la création de facture"""
        now = datetime.utcnow()
        past_date = now - timedelta(days=1)
        
        invalid_data = {
            'user_id': 1,
            'amount': 99.99,
            'currency': 'CHF',
            'due_date': past_date.isoformat()  # Date d'échéance dans le passé
        }
        
        schema = CreateInvoiceSchema()
        with pytest.raises(ValidationError, match="La date d'échéance ne peut pas être dans le passé"):
            schema.load(invalid_data)

class TestSchemaIntegration:
    """Tests d'intégration des schémas"""
    
    def test_user_listing_exchange_flow(self):
        """Test le flux complet utilisateur -> annonce -> échange"""
        # Créer un utilisateur
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        user_schema = CreateUserSchema()
        user = user_schema.load(user_data)
        
        # Créer une annonce
        listing_data = {
            'title': 'Test Item',
            'description': 'This is a test item with enough characters to be valid',
            'category': 'electronique',
            'condition': 'good',
            'estimated_value': 100.0,
            'currency': 'CHF'
        }
        listing_schema = CreateListingSchema()
        listing = listing_schema.load(listing_data)
        
        # Créer un échange
        exchange_data = {
            'requested_listing_id': 1,
            'offered_listing_id': 2,
            'message': 'I would like to exchange these items'
        }
        exchange_schema = CreateExchangeSchema()
        exchange = exchange_schema.load(exchange_data)
        
        # Vérifier que tout est valide
        assert user['username'] == 'testuser'
        assert listing['title'] == 'Test Item'
        assert exchange['message'] == 'I would like to exchange these items'
    
    def test_schema_error_messages_french(self):
        """Test que les messages d'erreur sont en français"""
        # Test utilisateur sans nom d'utilisateur
        invalid_user_data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        user_schema = CreateUserSchema()
        with pytest.raises(ValidationError) as exc_info:
            user_schema.load(invalid_user_data)
        
        assert "Le nom d'utilisateur est requis" in str(exc_info.value)
        
        # Test annonce sans titre
        invalid_listing_data = {
            'description': 'Valid description with enough characters',
            'category': 'livres',
            'condition': 'good',
            'estimated_value': 50.0,
            'currency': 'CHF'
        }
        
        listing_schema = CreateListingSchema()
        with pytest.raises(ValidationError) as exc_info:
            listing_schema.load(invalid_listing_data)
        
        assert "Le titre est requis" in str(exc_info.value)
