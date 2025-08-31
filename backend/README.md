# Lucky Kangaroo Backend

Backend API pour l'application Lucky Kangaroo, une plateforme d'échange et de troc d'objets avec système de notation, paiements sécurisés et fonctionnalités avancées.

## Fonctionnalités

- Authentification utilisateur sécurisée avec JWT
- Gestion des profils utilisateurs
- Publications et recherches d'annonces
- Système de messagerie en temps réel
- Paiements en ligne via Stripe
- Système de notation et d'avis
- Fonctionnalités d'IA pour la modération et les recommandations
- API RESTful complète
- Documentation Swagger/OpenAPI
- Cache et optimisation des performances
- Tâches asynchrones avec Celery
- Recherche avancée avec OpenSearch

## Prérequis

- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- OpenSearch 2.0+
- Node.js 16+ (pour certains outils de développement)

## Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/yourusername/lucky-kangaroo-backend.git
   cd lucky-kangaroo-backend
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: .\venv\Scripts\activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer l'environnement**
   Copier le fichier `.env.example` vers `.env` et modifier les variables selon votre configuration :
   ```bash
   cp .env.example .env
   ```
   
   Configurer au minimum :
   - `DATABASE_URL`
   - `REDIS_URL`
   - `JWT_SECRET_KEY`
   - `SECRET_KEY`
   - `MAIL_SERVER`, `MAIL_USERNAME`, `MAIL_PASSWORD`

5. **Initialiser la base de données**
   ```bash
   flask db upgrade
   ```

6. **Lancer l'application**
   ```bash
   flask run
   ```

   L'API sera disponible sur `http://localhost:5000/api/v1`
   La documentation Swagger sera disponible sur `http://localhost:5000/api/v1/doc`

## Structure du projet

```
backend/
├── api/                    # Package principal de l'API
│   └── v1/                 # Version 1 de l'API
│       ├── __init__.py     # Initialisation de l'API
│       ├── auth.py         # Authentification
│       ├── users.py        # Gestion des utilisateurs
│       ├── listings.py     # Gestion des annonces
│       ├── chat.py         # Messagerie
│       ├── payments.py     # Paiements
│       ├── reports.py      # Signalements
│       ├── ai.py           # Fonctionnalités IA
│       └── gamification.py # Système de gamification
├── models/                 # Modèles de données
├── services/               # Services métier
├── utils/                  # Utilitaires
├── migrations/             # Migrations de base de données
├── tests/                  # Tests
├── .env.example            # Exemple de configuration
├── config.py               # Configuration de l'application
├── requirements.txt        # Dépendances
└── app.py                 # Point d'entrée de l'application
```

## Variables d'environnement

Copiez `.env.example` vers `.env` et configurez les variables nécessaires :

```
# Application
FLASK_ENV=development
SECRET_KEY=votre_cle_secrete

# Base de données
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=votre_cle_jwt_secrete
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=votre@email.com
MAIL_PASSWORD=votre_mot_de_passe

# Stripe (paiements)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# OpenAI (IA)
OPENAI_API_KEY=sk-...

# Autres
SENTRY_DSN=votre_dsn_sentry
```

## Développement

### Lancer les tests
```bash
pytest
```

### Formater le code
```bash
black .
isort .
```

### Vérifier la qualité du code
```bash
flake8
pylint --load-plugins pylint_flask_sqlalchemy app.py api/ models/
```

### Mettre à jour les dépendances
```bash
pip freeze > requirements.txt
```

## Déploiement

### Avec Gunicorn
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 --threads 2 --worker-class gevent --timeout 120 wsgi:app
```

### Avec Docker
```bash
docker-compose up --build
```

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Auteurs

- [Votre Nom](https://github.com/votre-username)

## Remerciements

- À toutes les bibliothèques open-source utilisées
- À la communauté pour son soutien
