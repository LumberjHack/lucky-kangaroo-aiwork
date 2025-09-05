# 🔍 Audit technique Lucky Kangaroo — Repo `aiwork`

## Backend `/backend`

### `app.py`
- Entrée principale de l’app Flask
- Initialise toutes les extensions
- Requiert refactor en `create_app()` pour tests

### `config.py`
- Séparation config dev/prod
- Manque headers sécurisés (prod)

### `routes/`
- `auth.py`: Login/register, JWT → ✅ OK
- `ads.py`: CRUD annonces → 🟡 Partiel
- `search.py`: Recherche simple → 🟡 Basique
- `matching.py`: Vide → 🔴 À coder
- `chat.py`: SocketIO routes → 🟡 Squelette
- `user.py`: infos profil → 🟡 Incomplet

### `models/`
- `user.py`, `ad.py`, `message.py`, `category.py`
- Bien modélisé mais pas tous exploités

### `services/`
- `geo.py`: calcul distances → ✅ Ok
- `matching.py`: vide → 🔴
- `auth.py`: JWT utils → ✅

### `schemas/`
- Marshmallow → ✅

---

## Frontend `/frontend`

### `pages/`
- `Login`, `Register`, `Home`, `AdList`, `AdDetail` → ✅
- `Profile`, `NewAd`, `Chat` → 🟡 Incomplets

### `components/`
- `Navbar`, `Footer`, `AdCard`, `ChatBox`, `MapView`
- Squelettes en place

---

## DevOps

### `Dockerfile`, `docker-compose.yml`
- ✅ Ok

### `nginx/default.conf`
- Reverse proxy vers React & Flask
- ❗ Pas de HTTPS encore

---

## Tests

- `tests/` : auth, ads, models
- Pas de E2E encore

---

## Scripts

- `init_db.sh` + `seed_data.py` → ✅ Setup rapide
