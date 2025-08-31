# Installation Rapide - Lucky Kangaroo

## Installation en 5 minutes ⚡

### Prérequis
- Python 3.11+
- Node.js 20+
- Git

### Installation automatique

```bash
# Cloner le projet
git clone https://github.com/votre-org/lucky-kangaroo.git
cd lucky-kangaroo

# Lancer l'installation automatique
chmod +x install.sh
./install.sh
```

### Installation manuelle

#### 1. Backend
```bash
cd backend/lucky-kangaroo-backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
cp .env.example .env
python src/main.py
```

#### 2. Frontend
```bash
cd frontend/lucky-kangaroo-frontend
npm install
npm start
```

#### 3. Service IA
```bash
cd ai-service/lucky-kangaroo-ai
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

### Accès aux services

- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:5000
- **Service IA** : http://localhost:5002

### Configuration rapide

Modifiez les fichiers `.env` avec vos paramètres :
- Base de données (SQLite par défaut)
- Clés API (optionnel pour le développement)
- Configuration email (optionnel)

### Problèmes courants

**Port déjà utilisé :**
```bash
# Changer le port dans les fichiers de configuration
# Backend : src/main.py (port=5001)
# Frontend : package.json (PORT=3001)
```

**Dépendances manquantes :**
```bash
# Backend
pip install --upgrade pip
pip install -r requirements.txt

# Frontend
npm install --legacy-peer-deps
```

Pour plus de détails, consultez le [Guide de Déploiement](docs/deployment-guide.md).

