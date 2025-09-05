"""
Lucky Kangaroo - Configuration des tests
Configuration pytest et fixtures communes
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Ajouter le répertoire parent au PYTHONPATH
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend import create_app
from backend.extensions import db
from backend.models.user import User
from backend.models.listing import Listing
from backend.models.exchange import Exchange
from backend.models.chat import ChatRoom, ChatMessage
from backend.models.payment import Payment
from backend.models.gamification import UserAchievement, UserBadge

@pytest.fixture(scope='session')
def app():
    """Crée une instance de l'application Flask pour les tests"""
    # Configuration temporaire pour les tests
    test_config = {
        'TESTING': True,
        'DEBUG': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key',
        'JWT_SECRET_KEY': 'test-jwt-secret-key',
        'WTF_CSRF_ENABLED': False,
        'CELERY_ALWAYS_EAGER': True,
        'UPLOAD_FOLDER': tempfile.mkdtemp(),
        'LOG_LEVEL': 'ERROR'
    }
    
    app = create_app(test_config)
    
    # Créer le contexte de l'application
    with app.app_context():
        # Créer toutes les tables
        db.create_all()
        yield app
        # Nettoyer
        db.drop_all()
    
    # Nettoyer le dossier temporaire
    import shutil
    shutil.rmtree(test_config['UPLOAD_FOLDER'])

@pytest.fixture(scope='function')
def client(app):
    """Crée un client de test Flask"""
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    """Crée une session de base de données pour les tests"""
    with app.app_context():
        # Commencer une transaction
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Créer une session avec la transaction
        session = db.create_scoped_session()
        session.configure(bind=connection)
        
        yield session
        
        # Rollback de la transaction
        transaction.rollback()
        connection.close()
        session.remove()

@pytest.fixture
def sample_user(db_session):
    """Crée un utilisateur de test"""
    user = User(
        username='testuser',
        email='test@example.com',
        first_name='Test',
        last_name='User',
        password_hash='hashed_password',
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def sample_user2(db_session):
    """Crée un second utilisateur de test"""
    user = User(
        username='testuser2',
        email='test2@example.com',
        first_name='Test2',
        last_name='User2',
        password_hash='hashed_password2',
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def sample_listing(db_session, sample_user):
    """Crée une annonce de test"""
    listing = Listing(
        user_id=sample_user.id,
        title='Test Listing',
        description='This is a test listing',
        category='electronique',
        condition='good',
        estimated_value=100.0,
        currency='CHF',
        exchange_type='direct',
        status='active'
    )
    db_session.add(listing)
    db_session.commit()
    return listing

@pytest.fixture
def sample_listing2(db_session, sample_user2):
    """Crée une seconde annonce de test"""
    listing = Listing(
        user_id=sample_user2.id,
        title='Test Listing 2',
        description='This is another test listing',
        category='livres',
        condition='excellent',
        estimated_value=50.0,
        currency='CHF',
        exchange_type='direct',
        status='active'
    )
    db_session.add(listing)
    db_session.commit()
    return listing

@pytest.fixture
def sample_exchange(db_session, sample_user, sample_user2, sample_listing, sample_listing2):
    """Crée un échange de test"""
    exchange = Exchange(
        requester_id=sample_user.id,
        owner_id=sample_user2.id,
        offered_listing_id=sample_listing.id,
        requested_listing_id=sample_listing2.id,
        exchange_type='direct',
        status='requested',
        message='I would like to exchange these items'
    )
    db_session.add(exchange)
    db_session.commit()
    return exchange

@pytest.fixture
def sample_chat_room(db_session, sample_user, sample_user2):
    """Crée une salle de chat de test"""
    chat_room = ChatRoom(
        user1_id=sample_user.id,
        user2_id=sample_user2.id,
        is_active=True
    )
    db_session.add(chat_room)
    db_session.commit()
    return chat_room

@pytest.fixture
def sample_chat_message(db_session, sample_chat_room, sample_user):
    """Crée un message de chat de test"""
    message = ChatMessage(
        chat_room_id=sample_chat_room.id,
        sender_id=sample_user.id,
        content='Hello, this is a test message',
        message_type='text',
        status='sent'
    )
    db_session.add(message)
    db_session.commit()
    return message

@pytest.fixture
def sample_payment(db_session, sample_user):
    """Crée un paiement de test"""
    payment = Payment(
        user_id=sample_user.id,
        amount=99.99,
        currency='CHF',
        status='pending',
        description='Test payment'
    )
    db_session.add(payment)
    db_session.commit()
    return payment

@pytest.fixture
def sample_achievement(db_session, sample_user):
    """Crée un achievement de test"""
    achievement = UserAchievement(
        user_id=sample_user.id,
        achievement_type='first_exchange',
        title='First Exchange',
        description='Completed your first exchange',
        points=100
    )
    db_session.add(achievement)
    db_session.commit()
    return achievement

@pytest.fixture
def sample_badge(db_session, sample_user):
    """Crée un badge de test"""
    badge = UserBadge(
        user_id=sample_user.id,
        badge_type='trusted_user',
        title='Trusted User',
        description='Earned trust through successful exchanges',
        icon_url='badge_trusted.png'
    )
    db_session.add(badge)
    db_session.commit()
    return badge

@pytest.fixture
def auth_headers(sample_user):
    """Crée des en-têtes d'authentification pour les tests"""
    # Mock JWT token
    return {'Authorization': 'Bearer test-jwt-token'}

@pytest.fixture
def mock_redis():
    """Mock Redis pour les tests"""
    with patch('backend.extensions.redis_connection') as mock:
        mock_redis = Mock()
        mock.return_value = mock_redis
        yield mock_redis

@pytest.fixture
def mock_celery():
    """Mock Celery pour les tests"""
    with patch('backend.extensions.celery') as mock:
        yield mock

@pytest.fixture
def mock_openai():
    """Mock OpenAI pour les tests"""
    with patch('openai.OpenAI') as mock:
        mock_client = Mock()
        mock.return_value = mock_client
        yield mock_client

@pytest.fixture
def mock_stripe():
    """Mock Stripe pour les tests"""
    with patch('stripe.PaymentIntent') as mock_payment_intent, \
         patch('stripe.Customer') as mock_customer, \
         patch('stripe.PaymentMethod') as mock_payment_method:
        
        # Mock PaymentIntent
        mock_payment_intent.create.return_value = Mock(id='pi_test123', status='requires_payment_method')
        mock_payment_intent.retrieve.return_value = Mock(id='pi_test123', status='succeeded')
        
        # Mock Customer
        mock_customer.create.return_value = Mock(id='cus_test123')
        mock_customer.retrieve.return_value = Mock(id='cus_test123')
        
        # Mock PaymentMethod
        mock_payment_method.create.return_value = Mock(id='pm_test123')
        mock_payment_method.retrieve.return_value = Mock(id='pm_test123')
        
        yield {
            'PaymentIntent': mock_payment_intent,
            'Customer': mock_customer,
            'PaymentMethod': mock_payment_method
        }

@pytest.fixture
def mock_geolocation():
    """Mock du service de géolocalisation pour les tests"""
    with patch('backend.services.geolocation_service.GeolocationService') as mock:
        mock_service = Mock()
        mock.return_value = mock_service
        
        # Mock des méthodes de géolocalisation
        mock_service.get_coordinates_from_address.return_value = {
            'latitude': 46.9481,
            'longitude': 7.4474
        }
        mock_service.calculate_distance.return_value = 5.2  # km
        mock_service.get_nearby_cities.return_value = [
            {'name': 'Bern', 'distance': 5.2},
            {'name': 'Thun', 'distance': 15.8}
        ]
        
        yield mock_service

@pytest.fixture
def mock_search():
    """Mock du service de recherche pour les tests"""
    with patch('backend.services.search_service.SearchService') as mock:
        mock_service = Mock()
        mock.return_value = mock_service
        
        # Mock des méthodes de recherche
        mock_service.search_listings.return_value = {
            'results': [],
            'total': 0,
            'page': 1,
            'per_page': 20
        }
        mock_service.index_listing.return_value = True
        mock_service.delete_listing.return_value = True
        
        yield mock_service

@pytest.fixture
def mock_ai():
    """Mock du service d'IA pour les tests"""
    with patch('backend.services.ai_service.AIService') as mock:
        mock_service = Mock()
        mock.return_value = mock_service
        
        # Mock des méthodes d'IA
        mock_service.analyze_image.return_value = {
            'category': 'electronique',
            'confidence': 0.95,
            'tags': ['smartphone', 'mobile', 'technology'],
            'estimated_value': 500.0
        }
        mock_service.generate_description.return_value = "Description générée par l'IA"
        mock_service.moderate_content.return_value = {
            'is_appropriate': True,
            'confidence': 0.98,
            'flags': []
        }
        
        yield mock_service

@pytest.fixture
def mock_notification():
    """Mock du service de notification pour les tests"""
    with patch('backend.services.notification_service.NotificationService') as mock:
        mock_service = Mock()
        mock.return_value = mock_service
        
        # Mock des méthodes de notification
        mock_service.send_notification.return_value = True
        mock_service.send_email.return_value = True
        mock_service.send_push_notification.return_value = True
        
        yield mock_service

# Configuration des marqueurs pytest
def pytest_configure(config):
    """Configure les marqueurs pytest personnalisés"""
    config.addinivalue_line(
        "markers", "unit: marque les tests unitaires"
    )
    config.addinivalue_line(
        "markers", "integration: marque les tests d'intégration"
    )
    config.addinivalue_line(
        "markers", "slow: marque les tests lents"
    )
    config.addinivalue_line(
        "markers", "auth: marque les tests d'authentification"
    )
    config.addinivalue_line(
        "markers", "api: marque les tests d'API"
    )
    config.addinivalue_line(
        "markers", "database: marque les tests de base de données"
    )
    config.addinivalue_line(
        "markers", "external: marque les tests qui utilisent des services externes"
    )

# Configuration des options de ligne de commande
def pytest_addoption(parser):
    """Ajoute des options de ligne de commande personnalisées"""
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )
    parser.addoption(
        "--runexternal", action="store_true", default=False, help="run external service tests"
    )

def pytest_collection_modifyitems(config, items):
    """Modifie la collection des tests selon les options"""
    if not config.getoption("--runslow"):
        skip_slow = pytest.mark.skip(reason="need --runslow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
    
    if not config.getoption("--runexternal"):
        skip_external = pytest.mark.skip(reason="need --runexternal option to run")
        for item in items:
            if "external" in item.keywords:
                item.add_marker(skip_external)
