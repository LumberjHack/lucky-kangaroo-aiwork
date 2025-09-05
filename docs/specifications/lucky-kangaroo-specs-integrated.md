# 🦘 Lucky Kangaroo — Spécifications complètes (version intégrée, canonique)

Note: Ce document est la référence produit canonique côté `lk-audit`. Il consolide la version intégrée existante et sert de source de vérité unique. L’archive provenant de `V4/` est disponible séparément dans `docs/specifications/specifications-v4.md`.

---

🦘 Lucky Kangaroo — Spécifications complètes (version intégrée)

Cette version intègre l’intégralité du cahier des charges original et les ajustements discutés dans nos échanges : architecture monolithique pragmatique, recherche basée sur PostgreSQL (pg_trgm et pgvector) avec migration vers OpenSearch en cas de volumétrie importante, matching simplifié au départ, tarification agressive pour concurrencer Anibis/AutoScout/Ricardo, et surtout un catalogue de catégories largement enrichi inspiré de Craigslist et Anibis. Toutes les fonctionnalités mentionnées sont destinées à être développées sans être différées ; les phases proposées servent uniquement à structurer le travail.

## 🎨 Design à conserver
- Logo et identité : kangourou violet avec patte dans un cercle, palette en dégradé violet → bleu (#8B5CF6 → #3B82F6).
- Typographie : Inter, moderne et lisible.
- Layout : header + hero section + cards, mobile first (responsive).

## 🏗️ Architecture technique

### Backend
- Python 3.11+ avec Flask 2.3+, SQLAlchemy 2+.
- PostgreSQL 15+ avec PostGIS (géolocalisation), pg_trgm (recherche), pgvector (similarité sémantique).
- Redis 7+ (cache/sessions/queues).
- Celery + Redis (tâches asynchrones).
- Flask-SocketIO (chat temps réel) avec adaptateur Redis.
- Authentification JWT avec refresh tokens (Flask-JWT-Extended).
- Limitation de débit via Flask-Limiter.
- Validation avec Marshmallow ou Pydantic.

### Frontend web
- React 18+ (TypeScript) ou Vue.js 3.
- TailwindCSS.
- Redux Toolkit ou Pinia.
- React Router 6+ ou Vue Router.
- Axios avec intercepteurs.
- Socket.io-client (temps réel).
- React-Dropzone / Vue-Dropzone (upload).
- Leaflet ou Google Maps (cartes).
- Chart.js ou D3.js (graphiques).
- Framer Motion (animations).
- React Hook Form (formulaires).

### Mobile
- React Native 0.72+ avec Expo ; React Navigation 6 ; Redux Toolkit ; React Native Maps ; Expo Camera/Location/Notifications ; AsyncStorage.
- Mode hors-ligne, deep linking, authentification biométrique.

### DevOps & infrastructure
- Docker + Docker Compose ; Nginx reverse proxy ; hébergement Infomaniak/OVH ; CDN Cloudflare.
- Monitoring Sentry + DataDog ; logs ELK Stack ; CI/CD GitHub Actions ; SSL Let’s Encrypt ; sauvegardes automatiques ; Load Balancer Nginx ; OpenTelemetry.

## 👤 Gestion utilisateurs et sécurité
- Inscription/connexion ; social login (Google, Facebook, Apple) ; vérification email ; reset mot de passe ; 2FA optionnel ; chiffrement des données sensibles ; rate limiting anti-brute force.
- Profils : informations personnelles, photo, géolocalisation, préférences (langue, devise, notifications), trust score 0–100, historique d’échanges, badges, statistiques, confidentialité.
- Trust score : identité, historique, taux de réponse, signaux IA, complétude de profil.

## 📦 Gestion des annonces
- Création avancée : upload multiple, optimisation images, analyse IA, estimation de valeur, tags intelligents, catégorisation auto, géolocalisation auto, preview temps réel, détection de doublons, anti-spam.
- Catégories étendues (biens) : Antiquités, Électroménager, Art & loisirs créatifs, Véhicules récréatifs, Pièces auto, Aviation, Bébé & enfant, Barter & troc, Beauté & bien‑être, Vélos, Bateaux, Livres/BD/CD/DVD, Pro & industriel, Auto/moto/scooters/utilitaires, Mobiles & tablettes, Vêtements & accessoires, Ordinateurs & périphériques, Électronique grand public, Agricole & jardin, Meubles & déco, Ventes de garage & free stuff, Articles généraux, Engins & matériel lourd, Bijoux & montres, Matériaux & bricolage, Pièces & accessoires moto, Instruments de musique, Photo & vidéo, Camping & plein air, Sport & fitness, Billetterie & événements, Jeux & jouets, Jeux vidéo & consoles, Jantes & pneus, Animaux & accessoires, Immobilier & hébergement.
- Catégories de services (si activées) : Automobile ; Beauté & soins ; Informatique & mobile ; Créatifs ; Événementiel ; Agricole & jardinage ; Financier & juridique ; Santé & bien‑être non médicaux ; Maison & ménage ; Cours & formation ; Marine & nautique ; Petits travaux & artisanat ; Voyages & tourisme ; Services animaliers ; Publicité/marketing & services pro ; Services médicaux & paramédicaux (conformité requise).

## 🔍 Recherche & matching
- Recherche avancée (FTS + synonymes), filtres, tri pertinence/date/distance/valeur, géoloc (rayon), recherche visuelle par image, favoris/alertes.
- Moteur IA multi‑moteurs (sémantique multilingue, compatibilité objets, optimisation géographique, préférences, prédiction de succès). Détection de cycles A↔B, A→B→C→A (espace local, rayon 25 km, ≤ 100 candidats, fond de tâche).

## 💬 Communication & échanges
- Chat WebSockets, traduction automatique (8 langues), partages fichiers/images, statuts, modération automatique, E2E.
- Notifications push/email/SMS/WhatsApp optionnelle, préférences granulaires.
- Processus d’échange : proposition, négociation, validation, RDV, géolocalisation, confirmation, évaluations, gestion des litiges.

## 🌍 Géolocalisation & devises
- Haversine + PostGIS ; points de rencontre ; itinéraires ; zones de sécurité ; multi‑pays.
- 6 devises (CHF par défaut en Suisse) ; conversions automatiques ; UI en 8 langues.

## 🤖 IA & modération
- Détection d’objets, estimation valeur, tags intelligents, classification, état visuel, suggestions d’amélioration d’annonces.
- Assistant IA conversationnel multilingue (>50 langues).
- Modération automatique : contenu, sentiment, spam/fraude, validation images, score de confiance, interface de modération humaine.

## 🎮 Gamification
- Badges d’activité/écologiques/sociaux/qualité/géographiques/temporels ; points & niveaux ; leaderboards ; défis mensuels ; récompenses & avantages.

## 💰 Monétisation
- Particuliers : 2 CHF/14 j ; auto/moto 3 CHF/14 j ; « jusqu’à la vente » 7.90 CHF ; renew 0.50 CHF (≤ 1/j) ; Boost 24 h 0.79 CHF ; Top 7 j 1.49 CHF ; Pack 10 renew 3.90 CHF ; Badge identité 0.99 CHF ; Assurance échange 0.99–1.99 CHF ; escrow 0–0.8 % plafonné 9 CHF.
- Professionnels (garages) : plans S10→S120 et Illimité (voir barème), import inventaire, auto‑renew, branding, stats, crédits Top 7 j par palier, tolérance +10 % 48 h.

## 🛡️ Sécurité & conformité
- HTTPS, rotation JWT, chiffrement AES‑256, protection CSRF/XSS, rate limiting adaptatif, audit logs immuables, sauvegardes quotidiennes.
- RGPD, cookies, confidentialité, modération conforme aux lois locales.

## 📊 Analytics
- Dashboard utilisateur (stats, activité, trust, CO₂, badges) ; analytics admin (business, technique, géo, comportement, A/B testing, rapports). ClickHouse en option.

## 🚀 Performance & scalabilité
- Caches Redis, index PostgreSQL, partitionnement, pagination, compression, CDN, Nginx LB, autoscaling. Migration OpenSearch/ClickHouse au‑delà de 5 M d’annonces ; sharding/partitions > 20 M.
- Objectifs: API P95 < 100 ms ; pages < 2 s ; uptime ≥ 99.9 % ; >10 000 concurrents ; upload/processing images < 5 s.

## 🧪 Qualité & doc
- Tests unitaires ≥ 90 %, intégration, E2E, perfs, sécu, accessibilité. CI/CD ; SonarQube ; Snyk ; Lighthouse ; k6/Locust.
- Documentation: OpenAPI, diagrammes, guide déploiement/dev, schéma BD & migrations, guide sécurité.

## 📅 Roadmap
- Phase 1 (MVP) ; Phase 2 (IA & mobile) ; Phase 3 (avancé) ; Phase 4 (scale) — cf. détails ci‑dessus.
