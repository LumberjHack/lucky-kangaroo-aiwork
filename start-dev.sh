#!/bin/bash

# Script de démarrage pour Lucky Kangaroo - Environnement de développement
# Usage: ./start-dev.sh

set -e

echo "🦘 Démarrage de Lucky Kangaroo - Environnement de développement"
echo "================================================================"

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages colorés
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    print_error "Docker n'est pas installé. Veuillez installer Docker d'abord."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose n'est pas installé. Veuillez installer Docker Compose d'abord."
    exit 1
fi

# Créer les dossiers nécessaires
print_status "Création des dossiers nécessaires..."
mkdir -p backend/uploads
mkdir -p nginx/ssl
mkdir -p logs

# Vérifier si les fichiers de configuration existent
if [ ! -f "backend/.env" ]; then
    print_warning "Fichier .env manquant. Création d'un fichier .env.example..."
    cp backend/.env.example backend/.env 2>/dev/null || echo "DATABASE_URL=postgresql://lucky_kangaroo:password@postgres:5432/lucky_kangaroo
REDIS_URL=redis://redis:6379/0
JWT_SECRET_KEY=jwt-secret-key-change-in-production
SECRET_KEY=dev-secret-key-change-in-production
FRONTEND_URL=http://localhost:3000" > backend/.env
fi

# Arrêter les conteneurs existants
print_status "Arrêt des conteneurs existants..."
docker-compose down --remove-orphans

# Construire et démarrer les services
print_status "Construction et démarrage des services..."
docker-compose up --build -d

# Attendre que les services soient prêts
print_status "Attente que les services soient prêts..."
sleep 10

# Vérifier la santé des services
print_status "Vérification de la santé des services..."

# Vérifier PostgreSQL
if docker-compose exec -T postgres pg_isready -U lucky_kangaroo -d lucky_kangaroo > /dev/null 2>&1; then
    print_success "PostgreSQL est prêt"
else
    print_error "PostgreSQL n'est pas prêt"
fi

# Vérifier Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    print_success "Redis est prêt"
else
    print_error "Redis n'est pas prêt"
fi

# Vérifier le backend
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    print_success "Backend est prêt"
else
    print_warning "Backend n'est pas encore prêt, attente..."
    sleep 5
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        print_success "Backend est prêt"
    else
        print_error "Backend n'est pas prêt"
    fi
fi

# Vérifier le frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_success "Frontend est prêt"
else
    print_warning "Frontend n'est pas encore prêt, attente..."
    sleep 5
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend est prêt"
    else
        print_error "Frontend n'est pas prêt"
    fi
fi

# Exécuter les migrations de base de données
print_status "Exécution des migrations de base de données..."
docker-compose exec backend python migrate_db.py

# Afficher les informations de connexion
echo ""
echo "🎉 Lucky Kangaroo est maintenant démarré !"
echo "=========================================="
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:5000"
echo "📊 API Documentation: http://localhost:5000/api/v1"
echo "🗄️  PostgreSQL: localhost:5432"
echo "🔄 Redis: localhost:6379"
echo ""
echo "📋 Commandes utiles:"
echo "  - Voir les logs: docker-compose logs -f"
echo "  - Arrêter: docker-compose down"
echo "  - Redémarrer: docker-compose restart"
echo "  - Accéder au shell backend: docker-compose exec backend bash"
echo "  - Accéder au shell frontend: docker-compose exec frontend sh"
echo ""
echo "🔍 Vérification des endpoints:"
echo "  - Health check: curl http://localhost:5000/health"
echo "  - API info: curl http://localhost:5000/"
echo ""

# Afficher les logs en temps réel
print_status "Affichage des logs en temps réel (Ctrl+C pour arrêter)..."
docker-compose logs -f
