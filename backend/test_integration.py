#!/usr/bin/env python3
"""
Test d'intégration pour Lucky Kangaroo
Vérification que l'API fonctionne correctement
"""

import os
import sys
import requests
import json
from datetime import datetime

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuration
BASE_URL = "http://localhost:5000"
FRONTEND_URL = "http://localhost:3000"

def test_backend_health():
    """Tester la santé du backend"""
    print("🔄 Test de santé du backend...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend en ligne - {data.get('message', 'API fonctionne')}")
            return True
        else:
            print(f"❌ Backend répond avec le code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Impossible de contacter le backend: {e}")
        return False

def test_api_routes():
    """Tester les routes API principales"""
    print("\n🔄 Test des routes API...")
    
    routes_to_test = [
        ("/", "Route racine"),
        ("/api/auth/register", "Inscription"),
        ("/api/listings/categories", "Catégories"),
        ("/api/listings", "Listings")
    ]
    
    results = []
    
    for route, description in routes_to_test:
        try:
            response = requests.get(f"{BASE_URL}{route}", timeout=5)
            if response.status_code in [200, 401, 405]:  # 401/405 sont acceptables pour certaines routes
                print(f"✅ {description}: {response.status_code}")
                results.append(True)
            else:
                print(f"❌ {description}: {response.status_code}")
                results.append(False)
        except requests.exceptions.RequestException as e:
            print(f"❌ {description}: Erreur de connexion - {e}")
            results.append(False)
    
    return all(results)

def test_user_registration():
    """Tester l'inscription d'un utilisateur"""
    print("\n🔄 Test d'inscription utilisateur...")
    
    test_user = {
        "email": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "country": "CH",
        "accept_terms": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Utilisateur créé: {data.get('user', {}).get('email', 'N/A')}")
            return data.get('access_token'), data.get('user', {}).get('id')
        else:
            print(f"❌ Erreur d'inscription: {response.status_code} - {response.text}")
            return None, None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return None, None

def test_listing_creation(access_token, user_id):
    """Tester la création d'une annonce"""
    print("\n🔄 Test de création d'annonce...")
    
    test_listing = {
        "title": "Test iPhone 13 Pro Max",
        "description": "iPhone 13 Pro Max 256GB en excellent état, utilisé pendant 6 mois. Boîte et accessoires inclus.",
        "category_id": "electronics",
        "listing_type": "exchange",
        "condition": "excellent",
        "brand": "Apple",
        "model": "iPhone 13 Pro Max",
        "year": 2022,
        "estimated_value": 800,
        "currency": "CHF",
        "city": "Genève",
        "postal_code": "1200",
        "country": "CH",
        "exchange_type": "both",
        "desired_items": ["MacBook", "iPad"],
        "excluded_items": ["vêtements"],
        "tags": ["urgent", "neuf"]
    }
    
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/listings",
            json=test_listing,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Annonce créée: {data.get('listing', {}).get('title', 'N/A')}")
            return data.get('listing', {}).get('id')
        else:
            print(f"❌ Erreur de création d'annonce: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def test_listing_retrieval(listing_id):
    """Tester la récupération d'une annonce"""
    print("\n🔄 Test de récupération d'annonce...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/listings/{listing_id}", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Annonce récupérée: {data.get('listing', {}).get('title', 'N/A')}")
            return True
        else:
            print(f"❌ Erreur de récupération: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_frontend_access():
    """Tester l'accès au frontend"""
    print("\n🔄 Test d'accès au frontend...")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend accessible")
            return True
        else:
            print(f"❌ Frontend répond avec le code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Impossible d'accéder au frontend: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests d'intégration Lucky Kangaroo")
    print("=" * 60)
    
    # Test 1: Santé du backend
    backend_healthy = test_backend_health()
    if not backend_healthy:
        print("\n❌ Le backend n'est pas accessible. Vérifiez qu'il est démarré sur le port 5000.")
        return False
    
    # Test 2: Routes API
    api_working = test_api_routes()
    if not api_working:
        print("\n❌ Certaines routes API ne fonctionnent pas correctement.")
        return False
    
    # Test 3: Inscription utilisateur
    access_token, user_id = test_user_registration()
    if not access_token:
        print("\n❌ L'inscription utilisateur a échoué.")
        return False
    
    # Test 4: Création d'annonce
    listing_id = test_listing_creation(access_token, user_id)
    if not listing_id:
        print("\n❌ La création d'annonce a échoué.")
        return False
    
    # Test 5: Récupération d'annonce
    listing_retrieved = test_listing_retrieval(listing_id)
    if not listing_retrieved:
        print("\n❌ La récupération d'annonce a échoué.")
        return False
    
    # Test 6: Frontend
    frontend_accessible = test_frontend_access()
    if not frontend_accessible:
        print("\n⚠️  Le frontend n'est pas accessible. Vérifiez qu'il est démarré sur le port 3000.")
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"✅ Backend: {'OK' if backend_healthy else 'ERREUR'}")
    print(f"✅ API Routes: {'OK' if api_working else 'ERREUR'}")
    print(f"✅ Inscription: {'OK' if access_token else 'ERREUR'}")
    print(f"✅ Création annonce: {'OK' if listing_id else 'ERREUR'}")
    print(f"✅ Récupération annonce: {'OK' if listing_retrieved else 'ERREUR'}")
    print(f"{'✅' if frontend_accessible else '⚠️ '} Frontend: {'OK' if frontend_accessible else 'NON ACCESSIBLE'}")
    
    success = all([backend_healthy, api_working, access_token, listing_id, listing_retrieved])
    
    if success:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS !")
        print("🚀 Lucky Kangaroo est prêt à être utilisé !")
        print(f"\n📱 Frontend: {FRONTEND_URL}")
        print(f"🔧 Backend API: {BASE_URL}")
        print(f"📋 Annonce de test: {BASE_URL}/api/listings/{listing_id}")
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Vérifiez les erreurs ci-dessus et relancez les tests.")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
