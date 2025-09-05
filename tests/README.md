# Lucky Kangaroo - Tests

Ce répertoire contient tous les tests de l'application Lucky Kangaroo.

## 🏗️ Structure des tests

```
tests/
├── __init__.py              # Package de tests
├── conftest.py              # Configuration pytest et fixtures
├── test_schemas.py          # Tests des schémas de validation
├── test_api.py              # Tests d'intégration API
├── test_models.py           # Tests des modèles de données
├── test_services.py         # Tests des services métier
├── test_utils.py            # Tests des utilitaires
└── README.md                # Cette documentation
```

## 🚀 Exécution des tests

### Prérequis

1. **Python 3.8+** installé
2. **pytest** installé : `pip install -r requirements-test.txt`
3. **Environnement virtuel** activé (recommandé)

### Commandes de base

```bash
# Tous les tests
pytest

# Tests avec couverture
pytest --cov=backend --cov-report=html

# Tests spécifiques
pytest tests/test_api.py
pytest tests/test_schemas.py

# Tests par marqueurs
pytest -m unit          # Tests unitaires
pytest -m integration   # Tests d'intégration
pytest -m api           # Tests d'API
pytest -m database      # Tests de base de données
pytest -m slow          # Tests lents (optionnel)
pytest -m external      # Tests de services externes (optionnel)

# Tests en parallèle
pytest -n auto

# Tests avec rapport HTML
pytest --html=reports/report.html
```

### Scripts PowerShell

```powershell
# Tous les tests
.\scripts\run-tests.ps1

# Tests unitaires avec couverture
.\scripts\run-tests.ps1 -TestType "unit" -Coverage "true"

# Tests d'API en mode verbeux
.\scripts\run-tests.ps1 -TestType "api" -Verbose "true"

# Tests en parallèle
.\scripts\run-tests.ps1 -Parallel "true"
```

## 🧪 Types de tests

### Tests unitaires (`@pytest.mark.unit`)
- **Objectif** : Tester une fonction ou classe isolément
- **Portée** : Code métier, utilitaires, schémas
- **Exemples** : Validation de données, calculs, transformations

### Tests d'intégration (`@pytest.mark.integration`)
- **Objectif** : Tester l'interaction entre composants
- **Portée** : Services, modèles, base de données
- **Exemples** : Création d'utilisateur, gestion des annonces

### Tests d'API (`@pytest.mark.api`)
- **Objectif** : Tester les endpoints HTTP
- **Portée** : Routes, contrôleurs, réponses
- **Exemples** : Authentification, CRUD des ressources

### Tests de base de données (`@pytest.mark.database`)
- **Objectif** : Tester les opérations de persistance
- **Portée** : Modèles, migrations, requêtes
- **Exemples** : Relations, contraintes, performances

### Tests lents (`@pytest.mark.slow`)
- **Objectif** : Tests nécessitant du temps
- **Portée** : Intégrations externes, traitements lourds
- **Exemples** : Upload de fichiers, génération de rapports

### Tests de services externes (`@pytest.mark.external`)
- **Objectif** : Tester les intégrations tierces
- **Portée** : Stripe, OpenAI, géolocalisation
- **Exemples** : Paiements, IA, cartes

## 🔧 Configuration

### Fichier `conftest.py`
Contient la configuration globale et les fixtures communes :
- Configuration de l'application de test
- Fixtures de base de données
- Mocks des services externes
- Données de test

### Fichier `pytest.ini`
Configuration pytest avec :
- Marqueurs personnalisés
- Options par défaut
- Filtres d'avertissements

### Variables d'environnement
```bash
# Configuration de test
FLASK_ENV=testing
TESTING=true
DATABASE_URL=sqlite:///:memory:
```

## 📊 Couverture de code

### Génération du rapport
```bash
pytest --cov=backend --cov-report=html --cov-report=term-missing
```

### Rapport HTML
Le rapport est généré dans `htmlcov/` et peut être ouvert dans un navigateur.

### Métriques cibles
- **Couverture globale** : > 90%
- **Couverture des modèles** : > 95%
- **Couverture des services** : > 85%
- **Couverture des routes** : > 80%

## 🎭 Mocks et stubs

### Services externes
- **Stripe** : Mock des paiements
- **OpenAI** : Mock des réponses IA
- **Géolocalisation** : Mock des coordonnées
- **Redis** : Mock du cache
- **Celery** : Mock des tâches asynchrones

### Base de données
- **SQLite en mémoire** pour les tests
- **Transactions** avec rollback automatique
- **Fixtures** pour les données de test

## 📝 Écriture de tests

### Structure recommandée
```python
class TestUserService:
    """Tests pour le service utilisateur"""
    
    def test_create_user_success(self, db_session):
        """Test la création réussie d'un utilisateur"""
        # Arrange
        user_data = {...}
        
        # Act
        result = user_service.create_user(user_data)
        
        # Assert
        assert result.username == user_data['username']
        assert result.is_active is True
    
    def test_create_user_duplicate_email(self, db_session, existing_user):
        """Test la création avec un email dupliqué"""
        # Arrange
        user_data = {'email': existing_user.email}
        
        # Act & Assert
        with pytest.raises(ValidationError):
            user_service.create_user(user_data)
```

### Bonnes pratiques
1. **Noms descriptifs** : `test_create_user_with_valid_data_succeeds`
2. **Une assertion par test** : Plus facile à déboguer
3. **Fixtures réutilisables** : Éviter la duplication
4. **Mocks appropriés** : Isoler les dépendances
5. **Données de test réalistes** : Éviter les valeurs magiques

### Assertions recommandées
```python
# Égalité
assert result.status_code == 200
assert user.username == "testuser"

# Exceptions
with pytest.raises(ValidationError):
    service.process_data(invalid_data)

# Collections
assert len(users) == 3
assert "admin" in [u.role for u in users]

# Types
assert isinstance(result, dict)
assert hasattr(user, 'email')
```

## 🚨 Gestion des erreurs

### Tests d'erreurs attendues
```python
def test_invalid_input_raises_error(self):
    """Test que les données invalides lèvent une erreur"""
    with pytest.raises(ValidationError) as exc_info:
        validate_user_data(invalid_data)
    
    assert "email" in str(exc_info.value)
    assert exc_info.value.status_code == 400
```

### Tests de robustesse
```python
def test_service_handles_database_error(self, mock_db):
    """Test que le service gère les erreurs de base de données"""
    mock_db.side_effect = DatabaseError("Connection failed")
    
    with pytest.raises(ServiceError):
        user_service.get_user(1)
```

## 📈 Performance

### Tests de performance
```python
@pytest.mark.benchmark
def test_search_performance(self, benchmark, sample_data):
    """Test les performances de la recherche"""
    result = benchmark(search_service.search, "test")
    assert len(result) > 0
```

### Tests de charge
```python
@pytest.mark.slow
def test_concurrent_users(self):
    """Test la gestion de plusieurs utilisateurs simultanés"""
    # Simuler 100 utilisateurs simultanés
    results = []
    for i in range(100):
        result = user_service.create_user(f"user{i}")
        results.append(result)
    
    assert len(results) == 100
```

## 🔍 Débogage

### Mode verbeux
```bash
pytest -v -s --tb=long
```

### Arrêt au premier échec
```bash
pytest -x
```

### Tests spécifiques
```bash
pytest -k "test_user"  # Tests contenant "test_user"
pytest tests/test_api.py::TestAuthAPI::test_login  # Test spécifique
```

### Logs de débogage
```python
import logging
logging.basicConfig(level=logging.DEBUG)

def test_with_logs():
    logging.debug("Début du test")
    # ... test ...
    logging.debug("Fin du test")
```

## 🚀 Intégration continue

### GitHub Actions
```yaml
- name: Run tests
  run: |
    pip install -r requirements-test.txt
    pytest --cov=backend --cov-report=xml
```

### Pre-commit hooks
```yaml
- repo: local
  hooks:
    - id: pytest
      name: pytest
      entry: pytest
      language: system
      pass_filenames: false
      always_run: true
```

## 📚 Ressources

- [Documentation pytest](https://docs.pytest.org/)
- [Guide des fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Paramétrage des tests](https://docs.pytest.org/en/stable/parametrize.html)
- [Mocks et patches](https://docs.python.org/3/library/unittest.mock.html)

## 🤝 Contribution

### Ajouter de nouveaux tests
1. Créer le fichier de test dans le bon répertoire
2. Suivre la convention de nommage
3. Ajouter les marqueurs appropriés
4. Documenter les cas de test complexes
5. Vérifier la couverture

### Maintenir les tests existants
1. Mettre à jour les fixtures si nécessaire
2. Adapter les mocks aux changements d'API
3. Vérifier que les tests restent pertinents
4. Nettoyer les données de test obsolètes

---

**Note** : Les tests sont essentiels pour maintenir la qualité du code. Exécutez-les régulièrement et maintenez une couverture élevée !
