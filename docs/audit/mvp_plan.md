# 🏁 Plan d’action pour atteindre le MVP 100% fonctionnel

## 🎯 Objectif MVP

L’objectif est d’avoir une plateforme web fullstack fonctionnelle, prête à être utilisée par les premiers utilisateurs.  
Cela comprend l’inscription, création d’annonces, recherche, matching simple, chat en temps réel, et interface responsive.

---

## 🛠️ Modules à valider pour MVP

| Étape | Module         | Description                                                                                   | Statut      |
|-------|----------------|-----------------------------------------------------------------------------------------------|-------------|
| 1     | Auth           | JWT complet, refresh tokens, vérif email, reset password                                     | 🟡 Partiel |
| 2     | Annonces       | CRUD annonces + multi-images, géolocalisation, catégorisation                                 | 🟡 Partiel |
| 3     | Recherche      | Barre de recherche, filtres, rayon distance, texte                                            | 🟡 Partiel |
| 4     | Matching       | A↔B + A→B→C matching simplifié avec pgvector                                                  | 🔴 À coder |
| 5     | Chat temps réel| SocketIO Flask ↔ React, persistance messages                                                  | 🟡 Squelette |
| 6     | Profils        | Page profil, trust score, historique, préférences                                             | 🔴 À coder |
| 7     | Frontend       | Routing complet, Redux Toolkit, formulaires & UI complète                                     | 🟡 En cours |
| 8     | Backend API    | Endpoints REST stables pour users, annonces, recherche, chat                                  | 🟡 En cours |
| 9     | Sécurité       | Rate limiting, CORS, CSRF, HTTPS                                                              | 🟢 Ok |
| 10    | Tests          | Tests unitaires et intégration minimum                                                        | 🟡 Partiel |
| 11    | Docker & Deploy| Docker backend+frontend, docker-compose, déploiement test                                     | 🟢 Ok |
| 12    | UI UX Web      | Design responsive, hero section, cards                                                        | 🟡 Partiel |
| 13    | Docs & README  | Setup, API routes, schéma BDD                                                                 | 🟡 Partiel |

> 💡 Durée estimée : **4–5 semaines de dev** fullstack avec 1 dev principal et 1 assistant.
