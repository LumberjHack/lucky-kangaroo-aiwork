# Lucky Kangaroo – Notes essentielles pour l’assistant

Date: 2025-08-31 20:57 (Europe/Paris)

Ces notes résument les règles, politiques et éléments techniques incontournables pour garantir la continuité entre les sessions.

## Règles de collaboration
- **Langue**: Français pour toutes les réponses et la documentation.
- **Commandes système**: l’utilisateur valide manuellement chaque commande. Éviter d’en proposer si un outil d’édition de fichiers suffit.
- **Commits**: privilégier commit/push automatique après chaque changement testé et fonctionnel. Demander confirmation pour opérations sensibles (rebase/merge).
- **Ne pas réinventer**: analyser l’existant avant d’agir. Ne pas recréer des fichiers déjà présents. Supprimer les doublons si nécessaire (après confirmation).

## Références produit
- Spécifications intégrées (canonique) : `docs/specifications/lucky-kangaroo-specs-integrated.md`
- Archive V4 : `docs/specifications/specifications-v4.md`

## Politique de sauvegarde (backup)
- **Objectif**: snapshot automatique dans `backend/backup/<timestamp>/` avant toute modification backend.
- **Format timestamp**: `YYYYMMDD_HHMMSS`.
- **Contenu sauvegardé**: fichiers critiques du backend (ex. `backend/app.py`, `backend/extensions.py`, `backend/api/v1/*.py`, `backend/models/*.py`, etc.), avec **arborescence conservée**.
- **Outil**: utilitaire Python dans `backend/utils/backup.py` (copie physique des fichiers vers un dossier daté, structure conservée). Utiliser cet utilitaire avant toute édition.
- **Évolution prévue**: ajouter un hook Git `pre-commit` pour déclencher une sauvegarde des fichiers modifiés.

## Périmètre du projet
- **Backends actifs**:
  - Dossier `V4/` (courant) avec backend Flask complet. Fichiers clés:
    - `backend/app.py`: app factory, config, blueprints, erreurs, CLI.
    - `backend/extensions.py`: initialisation des extensions (SQLAlchemy, JWT, CORS, SocketIO, Mail, Celery, OpenSearch, Redis, etc.).
    - `backend/api/v1/`: routes (auth, users, autres endpoints à étendre).
    - `backend/models/`: modèles (ex. `user.py` complet: sécurité, géolocalisation, scoring, etc.).
    - `backend/wsgi.py`: point d’entrée WSGI prod utilisant `create_app()`.
  - Dossier `lucky-kangaroo-modern/`: frontend Next.js existant et backend également présent. Ne pas recréer; réutiliser ce qui existe si on y travaille.
- **Bases de données et services**: PostgreSQL + PostGIS, Redis, Socket.IO, OpenSearch/Elasticsearch (selon config), Celery.

## Sécurité et auth
- **JWT** avec refresh tokens, vérification email, reset mot de passe.
- **Décorateurs à ajouter**: `admin_required` (à implémenter selon l’architecture existante, après sauvegarde préalable).

## Chat temps réel & IA
- **Chat**: Socket.IO prévu (messages texte + médias, notifications). Persistance via modèle `Message`.
- **IA Matching (option avancée)**: moteurs séparés (ML scikit-learn, analyse sémantique, OpenSearch). Développement incrémental recommandé.

## Géolocalisation
- **PostGIS** complet, calculs de distance et zones de recherche. Exposer endpoints de recherche géo.

## Workflow standard de modification (à suivre strictement)
1. **Sauvegarde**: exécuter la sauvegarde datée via `backend/utils/backup.py` pour les fichiers ciblés avant tout changement.
2. **Implémentation**: modifier/ajouter le code en respectant l’architecture (blueprints, app factory, extensions centralisées).
3. **Tests rapides**: lancer tests unitaires/rapides ciblés si disponibles; sinon ajouter des tests minimaux.
4. **Validation**: vérifier l’intégration (import, enregistrement blueprint, dépendances).
5. **Commit/Push**: si OK, commit + push automatiques (demander confirmation pour opérations sensibles).

## Tâches en cours / À faire
- [En cours] Politique de sauvegarde automatique avant chaque modification (exécutée par l’assistant).
- [À faire] Hook Git `pre-commit` pour backup des fichiers backend modifiés.
- [À faire] Test unitaire léger pour `backend/utils/backup.py` (validation chemins, timestamp, contenu copié).
- [À prioriser avec l’utilisateur] Prochaine fonctionnalité backend (ex.: `admin_required`, endpoints tags/badges/listings, recherche géo, chat Socket.IO, moteurs IA).

## Notes déploiement
- **WSGI**: `backend/wsgi.py` configure `FLASK_APP='app:create_app()'` en prod et expose `application` pour le serveur WSGI.
- **Docker/Compose**: présents; respecter variables d’environnement et secrets. Ne pas modifier sans sauvegarde et validation.

## Principes à respecter
- **Cohérence**: rester aligné avec les patterns existants (factory, blueprints, extensions).
- **Traçabilité**: une sauvegarde par lot de modifications.
- **Lisibilité**: logs clairs et messages de commit explicites.
- **Minimiser les risques**: petits incréments + tests.

---
Ces notes doivent être mises à jour à chaque itération importante (nouvelle politique, nouveaux endpoints, changements d’archi, etc.).

## Rappels & Checklists

- **Avant de coder**
  - Exécuter la sauvegarde via `backend/utils/backup.py` pour les fichiers ciblés.
  - Relire l’architecture du module (blueprint, imports dans `backend/extensions.py`).
  - Vérifier variables d’environnement requises (dev/test/prod).
  - Préparer tests rapides (unitaires ou d’intégration légers).

- **Avant commit/push**
  - Tests passent localement (au minimum les modules impactés).
  - Documentation mise à jour (`docs/assistant-notes.md`, changelog si pertinent).
  - S’assurer que les nouveaux endpoints sont enregistrés et nommés de manière cohérente.
  - Vérifier migrations BD si schéma modifié.
  - Vérifier que les secrets (API keys, DSN, tokens) ne sont pas committés (utiliser `.env`, `.env.local`, GitHub Secrets).

- **Backend Flask**
  - Enregistrer le blueprint dans `backend/app.py` et éviter les imports circulaires.
  - Centraliser extensions et configuration dans `backend/extensions.py`.
  - Sécuriser via JWT (rôles/droits) et envisager `admin_required` si pertinent.

- **Déploiement/Prod**
  - `backend/wsgi.py` expose `application` et variables `FLASK_APP`, `FLASK_ENV` correctes.
  - Secrets via environnement, jamais en dur.
  - Healthcheck opérationnel (endpoint simple JSON, statut 200).

## Backlog d’idées (à prioriser avec l’utilisateur)

- **Sécurité**
  - Décorateur `admin_required` avec tests.
  - Rate limiting sur endpoints sensibles (auth, recherche) via middleware/extension dédiée.
  - Journaux d’audit (connexion, actions critiques).

- **API & Données**
  - CRUD pour tags/badges, listings avancés (filtres, pagination, tri).
  - Recherche hybride: PostGIS (géoloc) + OpenSearch (texte/semantique).
  - Caching sélectif via Redis pour endpoints de lecture intensive.

- **Chat temps réel**
  - Indicateurs de frappe, accusés de lecture, pièces jointes (scan antivirus), notifications push.
  - Traduction automatique optionnelle côté serveur.

- **IA Matching**
  - Similarité sémantique (embeddings) + règles métier.
  - Pipeline d’entraînement/évaluation + persistance des features.

- **Qualité/DevEx**
  - Tests unitaires et d’intégration prioritaires (auth, users, géo, chat).
  - Hook Git `pre-commit` pour trigger backup des fichiers backend modifiés.
  - Documentation OpenAPI minimale des endpoints existants.

- **Ops/Observabilité**
  - Endpoint `/api/health` et métriques basiques.
  - Intégration Sentry/équivalent pour erreurs runtime.
  - Optimisation Docker (caches, multi-stage, taille image).
