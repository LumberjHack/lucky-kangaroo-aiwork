# 🦘 Lucky Kangaroo — Spécifications complètes (version intégrée)

## 🎨 Design à conserver
- Logo et identité : kangourou violet avec patte dans un cercle, palette en dégradé violet → bleu (#8B5CF6 → #3B82F6)
- Typographie : Inter, moderne et lisible
- Layout : header + hero section + cards, mobile first (responsive)

## 🏗️ Architecture technique

### Backend
- Python 3.11+ avec Flask 2.3+
- Base de données PostgreSQL 15+ avec PostGIS, pg_trgm, pgvector
- Redis 7+ pour cache/sessions/queues
- Celery + Redis pour tâches asynchrones
- Flask-SocketIO pour le temps réel
- Authentification JWT avec refresh tokens
- Limitation de débit via Flask-Limiter
- Validation avec Marshmallow ou Pydantic

### Frontend web
- React 18+ (TypeScript) ou Vue.js 3
- TailwindCSS
- Redux Toolkit ou Pinia pour l'état
- React Router 6+ ou Vue Router
- Socket.io-client pour le temps réel
- React-Dropzone / Vue-Dropzone
- Leaflet ou Google Maps
- Chart.js ou D3.js
- Framer Motion pour les animations

### Mobile
- React Native 0.72+ avec Expo
- Navigation React Navigation 6
- Redux Toolkit
- React Native Maps
- Expo Camera/Location/Notifications
- Mode hors-ligne
- Deep linking
- Authentification biométrique

### DevOps & infrastructure
- Docker + Docker Compose
- Nginx comme reverse proxy
- Hébergement Infomaniak ou OVH
- CDN Cloudflare
- Monitoring via Sentry et DataDog
- Logs ELK Stack
- CI/CD avec GitHub Actions
- SSL via Let's Encrypt
- Sauvegardes automatiques
- Load Balancer Nginx
- Observabilité via OpenTelemetry

## 👤 Gestion utilisateurs et sécurité

### Authentification complète
- Inscription/connexion par email + mot de passe
- Authentification sociale (Google, Facebook, Apple)
- Vérification d'email
- Réinitialisation de mot de passe sécurisée
- Authentification 2FA optionnelle
- Chiffrement des données sensibles
- Rate limiting anti-brute force

### Profils utilisateurs
- Informations personnelles
- Photo de profil
- Géolocalisation
- Préférences (langue, devise, notifications)
- Trust score dynamique 0-100
- Historique d'échanges et évaluations
- Badges et récompenses
- Statistiques personnelles
- Paramètres de confidentialité

## 📦 Gestion des annonces

### Catégories principales
1. Antiquités & objets de collection
2. Appareils électroménagers & petit ménager
3. Art, artisanat & loisirs créatifs
4. Véhicules récréatifs (quads, motoneiges, caravanes...)
5. Pièces auto & accessoires
6. Aviation & sports aériens
7. Articles pour bébés & enfants
8. Barter & troc
9. Beauté, santé & bien-être
10. Vélos & pièces de vélo
11. Bateaux & pièces de bateau
12. Livres, BD, CD, DVD
13. Matériel professionnel & industriel
14. Voitures, motos, scooters, utilitaires
15. Téléphones mobiles & tablettes
16. Vêtements, chaussures & accessoires
17. Ordinateurs & périphériques
18. Électronique grand public
19. Équipement agricole, ferme & jardin
20. Meubles & décoration
21. Ventes de garage & "free stuff"
22. Articles généraux
23. Engins & matériel lourd
24. Bijoux & montres
25. Matériaux & bricolage
26. Pièces & accessoires moto
27. Instruments de musique
28. Photo & vidéo
29. Camping & plein air
30. Articles de sport & fitness
31. Billetterie & événements
32. Jeux & jouets
33. Jeux vidéo & consoles
34. Jantes & pneus
35. Animaux & accessoires
36. Immobilier & hébergement

### Catégories de services
1. Automobile (réparation, entretien, lavage, dépannage)
2. Beauté, bien-être & soins
3. Informatique & mobile
4. Créatifs (graphisme, photographie, musique...)
5. Événementiel
6. Agricole & jardinage
7. Financier & juridique
8. Santé & bien-être non médicaux
9. Maison & ménage
10. Cours & formation
11. Marine & nautique
12. Petits travaux & artisanat
13. Voyages & tourisme
14. Services animaliers
15. Publicité, marketing & services pro
16. Services médicaux & paramédicaux (sous réserve de conformité légale)

## 💰 Modèle économique

### Pour les particuliers
- Publication d'annonce : CHF 2.- pour 14 jours
- Annonces auto/moto : CHF 3.- pour 14 jours
- Option "jusqu'à la vente" : CHF 7.90 (véhicules)
- Remise en tête : CHF 0.50 (1x/jour max)
- Boost 24h : CHF 0.79
- Top 7 jours : CHF 1.49
- Pack 10 renew : CHF 3.90
- Badge identité : CHF 0.99
- Assurance échange : CHF 0.99-1.99

### Pour les professionnels (garages)
| Plan | Véhicules actifs max | Prix/mois |
|------|----------------------|-----------|
| S10  | 10                   | CHF 9.90  |
| S20  | 20                   | CHF 19.90 |
| S30  | 30                   | CHF 29.90 |
| S40  | 40                   | CHF 39.90 |
| S50  | 50                   | CHF 49.90 |
| S80  | 80                   | CHF 69.90 |
| S120 | 120                  | CHF 89.90 |
| Illimité | -                | CHF 99.90 |

## 🚀 Roadmap

### Phase 1 - MVP (4 semaines)
- Architecture PostgreSQL + Redis
- Authentification et profils
- Création/recherche d'annonces
- Chat temps réel basique
- Interface responsive
- Tarification de base
- Algorithme de matching simplifié

### Phase 2 - IA & Mobile (6 semaines)
- Moteurs IA (reconnaissance d'objets, estimation de valeur)
- Application mobile React Native
- Géolocalisation avancée
- Système d'évaluation
- Premiers éléments de gamification

### Phase 3 - Fonctionnalités avancées (8 semaines)
- Chaînes d'échange complexes (jusqu'à 8 participants)
- Gamification complète
- Monétisation premium
- Analytics avancées
- Intégration OpenSearch et ClickHouse

### Phase 4 - Passage à l'échelle (4 semaines)
- Optimisation des performances
- Tests de charge
- Déploiement multi-régions
- Monitoring complet
- Auto-scaling
