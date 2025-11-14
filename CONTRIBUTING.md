# Guide de Contribution

Merci de votre intérêt pour contribuer à Celeste Staff Meal ! Ce guide vous aidera à comprendre comment contribuer efficacement au projet.

## Table des matières

- [Code de conduite](#code-de-conduite)
- [Comment contribuer](#comment-contribuer)
- [Configuration de l'environnement de développement](#configuration-de-lenvironnement-de-développement)
- [Standards de code](#standards-de-code)
- [Processus de développement](#processus-de-développement)
- [Tests](#tests)
- [Documentation](#documentation)
- [Processus de Pull Request](#processus-de-pull-request)
- [Questions et support](#questions-et-support)

---

## Code de conduite

En participant à ce projet, vous acceptez de respecter un environnement respectueux et inclusif pour tous les contributeurs.

---

## Comment contribuer

### Types de contributions

Nous accueillons plusieurs types de contributions :

- 🐛 **Rapports de bugs** : Signalez les problèmes que vous rencontrez
- 💡 **Suggestions de fonctionnalités** : Proposez de nouvelles idées
- 📝 **Documentation** : Améliorez la documentation existante
- 🔧 **Code** : Corrigez des bugs ou ajoutez des fonctionnalités
- 🧪 **Tests** : Ajoutez ou améliorez les tests

### Avant de commencer

1. **Vérifiez les issues existantes** : Votre problème ou idée existe-t-il déjà ?
2. **Créez une issue** : Pour les bugs ou nouvelles fonctionnalités importantes
3. **Discutez** : Pour les changements majeurs, discutez-les d'abord dans une issue

---

## Configuration de l'environnement de développement

### Prérequis

- Python 3.12 ou supérieur
- [UV](https://github.com/astral-sh/uv) (gestionnaire de paquets)
- Git
- Compte Supabase (pour les tests d'intégration)

### Installation

1. **Fork et clone le dépôt**

```bash
git clone https://github.com/VOTRE-USERNAME/celeste-staff-meal.git
cd celeste-staff-meal
```

2. **Installer les dépendances**

```bash
make sync
```

Cela installe toutes les dépendances de production et de développement.

3. **Configurer les variables d'environnement**

Créez un fichier `.env` à la racine :

```bash
# Configuration Supabase (requis pour les tests)
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# Clés API IA (optionnel pour développement local)
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
```

4. **Vérifier l'installation**

```bash
make test
make lint
make typecheck
```

Tous les tests doivent passer et le linting doit être propre.

---

## Standards de code

### Type hints

**TOUS les fichiers Python DOIVENT avoir des type hints complets.**

```python
# ✅ Bon
def calculate_statistics(records: list[ValidationRecord]) -> Statistics:
    """Calculate statistics."""
    ...

# ❌ Mauvais
def calculate_statistics(records):
    ...
```

### Noms de variables

Utilisez des noms **descriptifs et explicites**. Évitez les abréviations cryptiques.

```python
# ✅ Bon
def filter_validation_records(
    records: list[ValidationRecord],
    operator: str | None = None,
) -> list[ValidationRecord]:
    ...

# ❌ Mauvais
def fvr(recs, op=None):
    ...
```

### Docstrings

**Style Google** pour les fonctions complexes, **one-liner** pour les fonctions simples.

```python
# ✅ Fonction simple - one-liner
def total_items(self) -> int:
    """Total quantity of all items."""
    return sum(item.quantity for item in self.items)

# ✅ Fonction complexe - Google style
def compare_orders(expected: Order, detected: Order) -> ComparisonResult:
    """Compare expected and detected orders.

    Args:
        expected: Expected order from QR code.
        detected: Detected order from bag image.

    Returns:
        ComparisonResult with comparison details.
    """
    ...
```

### Formatage

Le projet utilise **Ruff** pour le formatage et le linting. Formatez toujours votre code avant de commiter :

```bash
make format
make lint-fix
```

### Imports

Les imports doivent être triés avec `isort` (via Ruff) :

```python
# Ordre : stdlib, third-party, local
from datetime import datetime
from typing import Any

import streamlit as st
from pydantic import BaseModel

from staff_meal.models import Order, ValidationRecord
```

---

## Processus de développement

### 1. Créer une branche

```bash
git checkout -b feat/ma-nouvelle-fonctionnalite
# ou
git checkout -b fix/correction-bug
```

**Convention de nommage des branches** :
- `feat/` : Nouvelles fonctionnalités
- `fix/` : Corrections de bugs
- `docs/` : Documentation uniquement
- `refactor/` : Refactoring
- `test/` : Ajout de tests

### 2. Développer

- Écrivez du code propre et bien typé
- Ajoutez des tests pour toute nouvelle fonctionnalité
- Mettez à jour la documentation si nécessaire
- Vérifiez que les tests passent : `make test`
- Vérifiez le linting : `make lint`

### 3. Commit

Utilisez le format **Conventional Commits** :

```bash
git commit -m "feat(validation): add batch validation support"
git commit -m "fix(dashboard): resolve date filter issue"
git commit -m "docs: update architecture diagrams"
```

**Format** : `<type>(<scope>): <description>`

Types :
- `feat` : Nouvelle fonctionnalité
- `fix` : Correction de bug
- `docs` : Documentation
- `style` : Formatage (pas de changement de code)
- `refactor` : Refactoring
- `test` : Tests
- `chore` : Tâches de maintenance

### 4. Tests avant commit

Exécutez le pipeline CI complet avant de pousser :

```bash
make ci
```

Cela exécute :
- Linting (Ruff)
- Formatage (Ruff)
- Vérification de types (mypy)
- Scan de sécurité (Bandit)
- Tests avec couverture

**Tous doivent passer avant de créer une PR.**

---

## Tests

### Structure des tests

```
tests/
├── unit_tests/          # Tests unitaires (pas d'appels réseau)
└── integration_tests/  # Tests d'intégration (nécessitent API keys)
```

### Écrire des tests

**Tous les nouveaux fichiers DOIVENT avoir des tests correspondants.**

```python
# tests/unit_tests/test_validation.py
import pytest
from staff_meal.models import Item, Order, OrderItem, OrderSource
from ui.services.validation import compare_orders

def test_compare_orders_complete_match():
    """Test comparison with complete match."""
    expected = Order(
        order_id="ORD-123",
        source=OrderSource.UBER_EATS,
        items=[OrderItem(item=Item.MAKI_CALIFORNIA, quantity=2)],
    )
    detected = Order(
        order_id="ORD-123",
        source=OrderSource.UBER_EATS,
        items=[OrderItem(item=Item.MAKI_CALIFORNIA, quantity=2)],
    )

    result = compare_orders(expected, detected)

    assert result.is_complete is True
    assert len(result.missing_items) == 0
```

### Exécuter les tests

```bash
# Tous les tests unitaires
make test

# Tests spécifiques
uv run pytest tests/unit_tests/test_validation.py -v

# Avec couverture
uv run pytest tests/unit_tests/ --cov=staff_meal --cov-report=term-missing
```

### Couverture minimale

**80% de couverture minimale** est requise. Le projet actuel maintient **99.57%**.

Vérifiez la couverture :

```bash
make test
# Le rapport de couverture s'affiche à la fin
```

### Tests async

Pour les tests async, utilisez `pytest-asyncio` :

```python
import pytest_asyncio

@pytest_asyncio.fixture
async def async_client():
    """Provide async client."""
    client = AsyncClient()
    yield client

async def test_async_operation():
    """Test async operation."""
    result = await async_function()
    assert result is not None
```

---

## Documentation

### Docstrings

- **Fonctions simples** (0-1 param, comportement évident) : One-liner
- **Fonctions complexes** (APIs publiques, plusieurs params) : Style Google avec Args/Returns

```python
# Simple
def has_content(self) -> bool:
    """Check if artifact has content."""
    return self.content is not None

# Complexe
async def generate_explanation(
    comparison_result: ComparisonResult,
    language: Language = Language.FRENCH,
) -> str:
    """Generate explanation for validation result.

    Args:
        comparison_result: Result of order comparison.
        language: Target language for explanation.

    Returns:
        Explanation text in specified language.

    Raises:
        ValueError: If comparison_result is invalid.
    """
    ...
```

### Documentation Markdown

- Mettez à jour `README.md` pour les changements utilisateur-visibles
- Ajoutez des exemples dans `docs/use-cases.md` si pertinent
- Mettez à jour `docs/architecture.md` pour les changements d'architecture

---

## Processus de Pull Request

### Avant de créer une PR

1. ✅ Tous les tests passent (`make test`)
2. ✅ Linting propre (`make lint`)
3. ✅ Types vérifiés (`make typecheck`)
4. ✅ Pipeline CI complet (`make ci`)
5. ✅ Documentation mise à jour
6. ✅ Code formaté (`make format`)

### Créer la PR

1. **Poussez votre branche**

```bash
git push origin feat/ma-fonctionnalite
```

2. **Créez la PR sur GitHub**

- Titre : Format Conventional Commits (`feat(scope): description`)
- Description : Décrivez les changements et pourquoi
- Référencez les issues liées (`Fixes #123`)

3. **Template de description PR**

```markdown
## Description
Brève description des changements.

## Type de changement
- [ ] Bug fix
- [ ] Nouvelle fonctionnalité
- [ ] Breaking change
- [ ] Documentation

## Tests
- [ ] Tests unitaires ajoutés/mis à jour
- [ ] Tests d'intégration si applicable
- [ ] Tous les tests passent

## Checklist
- [ ] Code formaté (`make format`)
- [ ] Linting passé (`make lint`)
- [ ] Types vérifiés (`make typecheck`)
- [ ] Tests passent (`make test`)
- [ ] Documentation mise à jour
- [ ] Pas de breaking changes (ou documentés)
```

### Review process

1. **Attendez la review** : Au moins un mainteneur doit approuver
2. **Répondez aux commentaires** : Adressez tous les commentaires
3. **Mettez à jour si nécessaire** : Poussez de nouveaux commits
4. **Merge** : Un mainteneur merge après approbation

---

## Standards spécifiques au projet

### Gestion des erreurs

**Préférence** : Éviter try/except sauf si explicitement demandé (selon les règles du projet).

Utilisez des validations Pydantic et laissez les erreurs remonter naturellement.

### API Keys

- **Jamais** hardcoder les clés API dans le code
- Utilisez `SecretStr` de Pydantic pour les clés API
- Ne loggez jamais les valeurs de clés API
- Utilisez les variables d'environnement ou la configuration UI

### Modèles Pydantic

- Utilisez **Pydantic BaseModel**, jamais `dataclasses`
- Tous les champs doivent avoir des types explicites
- Utilisez `Field()` pour les descriptions et validations

```python
from pydantic import BaseModel, Field

class Order(BaseModel):
    """Complete order from QR code."""

    order_id: str = Field(..., description="Unique order identifier")
    source: OrderSource = Field(..., description="Order source platform")
    items: list[OrderItem] = Field(..., min_length=1, description="Items in the order")
```

### Gestion des dépendances

- **Toujours utiliser `uv`**, jamais `pip`
- Ajoutez les dépendances dans `pyproject.toml`
- Exécutez `make sync` après modification

---

## Questions et support

### Obtenir de l'aide

- 📖 **Documentation** : Consultez `README.md` et `docs/`
- 🐛 **Bugs** : Créez une issue sur GitHub
- 💬 **Questions** : Ouvrez une discussion GitHub
- 📧 **Contact** : benkirane.kamil@gmail.com

### Ressources

- [Architecture du système](docs/architecture.md)
- [Guide utilisateur Dashboard](docs/dashboard-guide.md)
- [Cas d'usage](docs/use-cases.md)
- [Standards de développement](AGENTS.md)

---

## Remerciements

Merci de contribuer à Celeste Staff Meal ! 🎉

Vos contributions aident à améliorer l'expérience des restaurants et à réduire les erreurs de commandes.
