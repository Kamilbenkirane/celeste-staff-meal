# Cas d'usage et Scénarios Avancés

Ce document présente des cas d'usage détaillés pour Celeste Staff Meal, montrant comment utiliser la plateforme dans différents contextes réels.

## Table des matières

- [Cas d'usage 1 : Validation quotidienne en cuisine](#cas-dusage-1--validation-quotidienne-en-cuisine)
- [Cas d'usage 2 : Analyse hebdomadaire des performances](#cas-dusage-2--analyse-hebdomadaire-des-performances)
- [Cas d'usage 3 : Formation d'un nouvel opérateur](#cas-dusage-3--formation-dun-nouvel-opérateur)
- [Cas d'usage 4 : Intégration avec système de gestion](#cas-dusage-4--intégration-avec-système-de-gestion)
- [Cas d'usage 5 : Gestion multi-restaurants](#cas-dusage-5--gestion-multi-restaurants)
- [Scénarios d'erreur et résolution](#scénarios-derreur-et-résolution)
- [Optimisation des coûts IA](#optimisation-des-coûts-ia)

---

## Cas d'usage 1 : Validation quotidienne en cuisine

### Contexte

Un restaurant sushi reçoit en moyenne 150 commandes par jour via UberEats et Deliveroo. L'équipe de préparation doit vérifier chaque commande avant de fermer le sac pour éviter les réclamations.

### Workflow détaillé

#### Matin (9h-12h) - Préparation

1. **Configuration initiale**
   - L'opérateur ouvre l'application sur la tablette de cuisine
   - Vérifie que les clés API IA sont configurées (barre latérale)
   - Sélectionne sa langue préférée (ex: Wolof, Bambara, Arabe)

2. **Première commande de la journée**
   ```
   Commande: ORD-25011 (UberEats)
   Articles attendus:
   - 2x Boite de 6 California Rolls
   - 1x Boite de 6 Sashimi Saumon
   - 1x Soupe Miso
   - 2x Sauce
   ```

3. **Processus de validation**
   - **Étape 1** : Scan du QR code depuis le ticket de commande
     - L'application affiche immédiatement la commande attendue
   - **Étape 2** : Photo du sac avec tous les articles visibles
     - L'IA analyse l'image en 2-3 secondes
   - **Étape 3** : Résultat de validation
     - ✅ **Commande complète** : Message vert "OK", explication audio en langue choisie
     - ⚠️ **Articles manquants** : Liste claire des articles manquants, explication détaillée

#### Période de pointe (12h-14h, 19h-21h)

**Défi** : Volume élevé, stress, risque d'erreurs accru

**Solution** :
- Utilisation de l'explication audio pour validation mains libres
- Interface simplifiée avec grands boutons
- Validation en moins de 5 secondes par commande

**Exemple réel** :
```
12h45 - Pic d'activité
- 8 commandes en attente
- Opérateur: "Marie"
- Langue: Français

Commande ORD-26324 : ⚠️ 1x Sauce manquante
→ Explication audio: "Attention, il manque une sauce pour la commande ORD-26324"
→ Correction immédiate avant fermeture du sac
```

### Résultats attendus

- **Réduction des erreurs** : De 8-10% à moins de 2%
- **Temps de validation** : 3-5 secondes par commande
- **Satisfaction équipe** : Interface intuitive, moins de stress

---

## Cas d'usage 2 : Analyse hebdomadaire des performances

### Contexte

Le gérant du restaurant veut analyser les performances de la semaine écoulée pour identifier les problèmes récurrents et améliorer les processus.

### Workflow détaillé

#### Lundi matin - Analyse de la semaine précédente

1. **Accès au dashboard**
   - Navigation vers "📊 Tableau de bord"
   - Sélection de la période : 7 derniers jours

2. **Analyse des métriques principales**
   ```
   Période: 15-21 janvier 2024

   📈 Métriques:
   - Total commandes: 1,247
   - Commandes complètes: 1,198 (96.1%)
   - Taux d'erreur: 3.9%
   - Comparaison semaine précédente: ↓ 0.5% (amélioration)
   ```

3. **Examen des alertes**
   ```
   🚨 Alertes détectées:

   🟡 ATTENTION: Taux de complétude sous objectif
   Le taux de complétude est de 96.1%, en dessous de l'objectif de 95%
   → Objectif atteint ! (95% est le minimum)

   ℹ️ INFO: Pic d'erreurs identifié
   Heures critiques: 13h-14h (vendredi), 20h-21h (samedi)
   ```

4. **Analyse des erreurs par type**
   ```
   📊 Répartition des erreurs:
   - Articles manquants: 32 cas (65%)
   - Quantités insuffisantes: 12 cas (24%)
   - Articles supplémentaires: 5 cas (11%)
   ```

5. **Top articles oubliés**
   ```
   📦 Top 10 articles oubliés:
   1. Sauce: 18 occurrences
   2. Soupe Miso: 8 occurrences
   3. Boite de 6 Maki: 6 occurrences
   ```

6. **Analyse par opérateur**
   ```
   👥 Performance par opérateur:
   - Marie: 98.2% complétude (excellent)
   - Ahmed: 95.8% complétude (bon)
   - Sophie: 94.1% complétude (à améliorer)
   ```

7. **Recommandations IA**
   ```
   💡 Recommandations générées:

   🔴 CRITIQUE: Sauce oubliée 18x cette semaine
   → Action: Former équipe sur vérification systématique des sauces
   → Cible: Opérateurs Sophie et Ahmed (heures critiques)

   🟡 ATTENTION: Pic d'erreurs vendredi 13h-14h
   → Action: Renforcer équipe pendant cette période
   → Vérifier disponibilité supplémentaire

   💡 ACTION: Articles oubliés principalement pendant rush
   → Action: Créer checklist visuelle pour période de pointe
   → Afficher près de la zone de préparation
   ```

8. **Export des données**
   - Export Excel avec toutes les données enrichies
   - Partage avec l'équipe de direction
   - Archivage pour analyse historique

### Actions décidées

1. **Formation ciblée** : Session de 30 minutes avec Sophie et Ahmed sur vérification des sauces
2. **Renforcement équipe** : Ajout d'un opérateur supplémentaire vendredi 13h-14h
3. **Checklist visuelle** : Création d'un poster avec les articles les plus oubliés

### Résultats attendus

- **Amélioration continue** : Réduction progressive des erreurs
- **Décisions data-driven** : Basées sur des données réelles, pas sur des impressions
- **Traçabilité** : Historique complet pour audits qualité

---

## Cas d'usage 3 : Formation d'un nouvel opérateur

### Contexte

Un nouveau membre rejoint l'équipe de préparation. Il doit apprendre à utiliser le système de validation rapidement pour être opérationnel dès le premier jour.

### Workflow détaillé

#### Jour 1 - Formation initiale (30 minutes)

1. **Présentation du système**
   - Objectif : Vérifier chaque commande avant fermeture du sac
   - Avantages : Moins d'erreurs, moins de stress, meilleures notes

2. **Démonstration avec mode démo**
   - Navigation vers "📝 Mode démo"
   - Génération d'un QR code de test
   - Simulation complète du workflow :
     ```
     Étape 1: Scanner QR code → Commande affichée
     Étape 2: Prendre photo du sac → Analyse IA
     Étape 3: Vérifier résultat → ✅ OK ou ⚠️ Manquant
     ```

3. **Pratique guidée**
   - 5 commandes de démo avec différents scénarios :
     - Commande complète ✅
     - Article manquant ⚠️
     - Quantité insuffisante ⚠️
     - Article supplémentaire ⚠️

4. **Configuration personnelle**
   - Sélection de la langue préférée (ex: Portugais)
   - Test de l'explication audio
   - Vérification de la compréhension des messages

#### Jour 1 - Première commande réelle (supervisée)

**Scénario** :
```
Commande: ORD-28111 (Deliveroo)
Articles: 3x Boite de 6 California Rolls, 2x Sauce

Processus:
1. Scan QR code → ✅ Commande affichée correctement
2. Photo du sac → ⚠️ Détection: 1x Sauce manquante
3. Vérification manuelle → Confirme: il manque bien 1 sauce
4. Ajout de la sauce manquante
5. Nouvelle photo → ✅ Commande complète
```

**Feedback formateur** :
- "Excellent, tu as bien suivi le processus"
- "L'IA a détecté le problème avant que tu fermes le sac"
- "Continue comme ça, tu es prêt pour l'autonomie"

#### Semaine 1 - Suivi des performances

**Dashboard - Filtre par opérateur** :
```
Opérateur: Nouveau (semaine 1)
- Total commandes: 87
- Taux de complétude: 97.7%
- Erreurs: 2 (1 sauce oubliée, 1 soupe manquante)
- Comparaison équipe: Légèrement au-dessus de la moyenne
```

**Points d'amélioration identifiés** :
- Vérification systématique des sauces (erreur récurrente débutants)
- Attention particulière aux soupes (peu visibles dans le sac)

### Résultats attendus

- **Courbe d'apprentissage rapide** : Opérationnel dès le premier jour
- **Confiance** : Système rassurant pour les nouveaux
- **Qualité constante** : Pas de baisse de qualité pendant l'intégration

---

## Cas d'usage 4 : Intégration avec système de gestion

### Contexte

Un restaurant souhaite intégrer Celeste Staff Meal avec son système de gestion de restaurant existant (POS, gestion des stocks, etc.) pour une traçabilité complète.

### Architecture d'intégration

```
┌─────────────────┐
│ Système POS     │
│ (Gestion       │
│  commandes)     │
└────────┬────────┘
         │
         │ API REST / Webhook
         │
         ▼
┌─────────────────┐
│ Celeste Staff   │
│ Meal            │
│ (Validation)    │
└────────┬────────┘
         │
         │ Données validation
         │
         ▼
┌─────────────────┐
│ Supabase        │
│ (Base de        │
│  données)       │
└─────────────────┘
```

### Workflow d'intégration

#### 1. Synchronisation des commandes

**Scénario** : Le système POS envoie automatiquement les commandes à Celeste Staff Meal

```python
# Exemple d'intégration (pseudo-code)
def sync_order_from_pos(order_data):
    """Synchroniser une commande depuis le POS."""
    # Créer un QR code avec les données de commande
    qr_data = {
        "order_id": order_data["id"],
        "source": order_data["platform"],  # "ubereats" ou "deliveroo"
        "items": order_data["items"]
    }

    # Générer QR code
    qr_image = generate_qr_code(qr_data)

    # Envoyer au système de validation
    send_to_validation_system(qr_image)
```

#### 2. Récupération des résultats de validation

**Scénario** : Le système POS récupère les résultats de validation pour affichage

```python
# Récupération depuis Supabase
def get_validation_status(order_id):
    """Récupérer le statut de validation d'une commande."""
    records = get_validation_records(order_id=order_id)

    if records:
        latest = records[0]
        return {
            "order_id": latest.order_id,
            "is_complete": latest.is_complete,
            "timestamp": latest.timestamp.isoformat(),
            "operator": latest.operator,
            "missing_items": [
                {
                    "item": item.item.value,
                    "expected": item.expected_quantity,
                    "detected": item.detected_quantity
                }
                for item in latest.comparison_result.missing_items
            ]
        }
    return None
```

#### 3. Alertes automatiques

**Scénario** : Envoi d'alertes au système POS en cas d'erreur critique

```python
# Webhook vers système POS
def send_alert_to_pos(validation_record):
    """Envoyer une alerte au POS en cas d'erreur."""
    if not validation_record.is_complete:
        alert = {
            "type": "validation_error",
            "order_id": validation_record.order_id,
            "severity": "high" if len(validation_record.comparison_result.missing_items) > 2 else "medium",
            "message": f"Commande {validation_record.order_id} incomplète",
            "missing_items": [item.item.value for item in validation_record.comparison_result.missing_items]
        }

        # Envoyer webhook au POS
        send_webhook(pos_webhook_url, alert)
```

### Cas d'usage concret

**Restaurant avec système POS moderne** :

1. **Commande reçue** → POS génère automatiquement le QR code
2. **Préparation** → L'équipe scanne le QR code depuis le POS
3. **Validation** → Celeste Staff Meal valide la commande
4. **Résultat** → Le POS affiche le statut de validation
5. **Historique** → Toutes les validations sont tracées dans le POS

### Avantages de l'intégration

- **Traçabilité complète** : De la commande à la livraison
- **Alertes en temps réel** : Notification immédiate des erreurs
- **Analytics unifiés** : Données de validation intégrées aux analytics du restaurant
- **Workflow optimisé** : Pas de double saisie, tout automatisé

---

## Cas d'usage 5 : Gestion multi-restaurants

### Contexte

Une chaîne de restaurants souhaite déployer Celeste Staff Meal sur plusieurs établissements avec une vue centralisée des performances.

### Architecture multi-restaurants

```
┌─────────────────────────────────────────┐
│         Dashboard Centralisé             │
│  (Vue d'ensemble tous les restaurants)   │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
┌───────────┐ ┌───────────┐ ┌───────────┐
│ Restaurant│ │ Restaurant│ │ Restaurant│
│   Paris   │ │  Lyon     │ │ Marseille  │
│           │ │           │ │           │
│ Supabase  │ │ Supabase  │ │ Supabase  │
│ Instance  │ │ Instance  │ │ Instance  │
└───────────┘ └───────────┘ └───────────┘
```

### Configuration par restaurant

Chaque restaurant a sa propre instance Supabase avec :

```sql
-- Table validation_records avec colonne restaurant_id
CREATE TABLE validation_records (
    id SERIAL PRIMARY KEY,
    restaurant_id VARCHAR(50) NOT NULL,
    order_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    operator VARCHAR(100),
    is_complete BOOLEAN NOT NULL,
    -- ... autres champs
);
```

### Dashboard centralisé

**Vue d'ensemble** :
```
📊 Performance globale (7 derniers jours)

Restaurant          | Commandes | Complétude | Erreurs | Tendance
--------------------|-----------|------------|---------|----------
Paris Centre        | 1,247     | 96.1%      | 3.9%    | ↓ 0.5%
Lyon Part-Dieu      | 892       | 97.3%      | 2.7%    | ↑ 0.8%
Marseille Vieux-Port| 1,156     | 95.8%      | 4.2%    | → 0.0%
```

**Détail par restaurant** :
- Clic sur un restaurant → Dashboard détaillé de ce restaurant
- Comparaison entre restaurants
- Identification des meilleures pratiques

### Cas d'usage concret

**Chaîne de 5 restaurants sushi** :

1. **Déploiement progressif**
   - Semaine 1 : Restaurant pilote (Paris)
   - Semaine 2-3 : Formation et ajustements
   - Semaine 4 : Déploiement sur les 4 autres restaurants

2. **Suivi centralisé**
   - Réunion hebdomadaire avec vue d'ensemble
   - Identification des restaurants performants
   - Partage des meilleures pratiques

3. **Benchmarking**
   ```
   Restaurant le plus performant: Lyon Part-Dieu (97.3%)
   → Analyse des pratiques spécifiques
   → Partage avec autres restaurants
   → Amélioration globale de la chaîne
   ```

### Avantages

- **Vue d'ensemble** : Performance globale de la chaîne
- **Benchmarking** : Comparaison entre restaurants
- **Meilleures pratiques** : Partage des techniques efficaces
- **Scalabilité** : Facile d'ajouter de nouveaux restaurants

---

## Scénarios d'erreur et résolution

### Scénario 1 : QR Code illisible

**Problème** : Le QR code est endommagé ou flou, impossible à scanner.

**Solutions** :
1. **Réessayer** : Prendre une nouvelle photo avec meilleure lumière
2. **Saisie manuelle** : Entrer la commande manuellement (si fonctionnalité disponible)
3. **Mode démo** : Utiliser le générateur de QR code pour créer un QR de test avec les mêmes données

**Prévention** :
- Imprimer les QR codes sur papier de qualité
- Protéger les QR codes de l'humidité (laminage)

### Scénario 2 : Erreur de détection IA

**Problème** : L'IA ne détecte pas correctement les articles (faux positif/négatif).

**Solutions** :
1. **Vérification manuelle** : Toujours vérifier visuellement avant de fermer le sac
2. **Nouvelle photo** : Réorganiser les articles et reprendre une photo
3. **Ajustement de la photo** : Meilleure lumière, angle différent, articles mieux visibles

**Exemple** :
```
Détection IA: 1x Sauce manquante
Vérification manuelle: 2 sauces présentes (1 visible, 1 cachée)
Action: Réorganiser le sac, nouvelle photo → ✅ Commande complète
```

### Scénario 3 : Problème de connexion internet

**Problème** : Pas de connexion internet, impossible d'utiliser l'IA.

**Solutions** :
1. **Mode hors ligne** : Validation manuelle basique (si implémentée)
2. **Vérification visuelle** : Comparaison manuelle avec le ticket
3. **Retry** : Réessayer après rétablissement de la connexion

**Recommandation** : Toujours avoir une connexion internet stable en cuisine.

### Scénario 4 : Erreur de sauvegarde en base de données

**Problème** : La validation réussit mais l'enregistrement en base échoue.

**Solutions** :
1. **Vérifier la configuration Supabase** : URL et clé API correctes
2. **Vérifier la connexion** : Test de connexion à Supabase
3. **Réessayer** : La validation peut être refaite

**Prévention** :
- Vérifier régulièrement la connexion Supabase
- Monitorer les erreurs de sauvegarde
- Avoir un système de backup

---

## Optimisation des coûts IA

### Comprendre les coûts

Les appels IA (Google Gemini, OpenAI, etc.) ont un coût par requête. Pour un restaurant avec 150 commandes/jour :

```
Coûts estimés (exemple):
- Google Gemini Flash: ~$0.001 par image
- 150 commandes/jour × 30 jours = 4,500 images/mois
- Coût mensuel: ~$4.50
```

### Stratégies d'optimisation

#### 1. Choix du modèle IA

**Modèles économiques** :
- Google Gemini 2.5 Flash Lite : Rapide et économique
- OpenAI GPT-4o-mini : Bon rapport qualité/prix

**Recommandation** : Utiliser Gemini Flash Lite par défaut, GPT-4o uniquement si nécessaire.

#### 2. Cache des résultats similaires

**Stratégie** : Si une commande identique a déjà été validée récemment, réutiliser le résultat.

```python
# Exemple de cache (conceptuel)
def predict_order_cached(bag_image, expected_order):
    """Prédiction avec cache pour optimiser les coûts."""
    cache_key = hash_image(bag_image)

    if cache_key in cache and cache[cache_key].is_recent():
        return cache[cache_key].result

    # Appel IA uniquement si nécessaire
    result = predict_order(bag_image, expected_order)
    cache[cache_key] = CachedResult(result)
    return result
```

#### 3. Batch processing (futur)

**Stratégie** : Traiter plusieurs images en une seule requête IA (si supporté).

#### 4. Limitation des appels audio

**Stratégie** : Générer l'audio uniquement si demandé explicitement par l'utilisateur.

**Économie** :
- Sans audio : 1 appel IA par validation
- Avec audio : 2 appels IA par validation (texte + audio)
- Économie : 50% si audio optionnel

### Recommandations pratiques

1. **Utiliser Gemini Flash Lite par défaut** : Meilleur rapport qualité/prix
2. **Audio optionnel** : Activer uniquement si nécessaire
3. **Monitorer les coûts** : Suivre la consommation via les dashboards des fournisseurs IA
4. **Ajuster selon le volume** : Modèles plus performants uniquement pour périodes critiques

### Budget estimé

**Petit restaurant** (50 commandes/jour) :
- Coût mensuel : ~$1.50
- Coût annuel : ~$18

**Restaurant moyen** (150 commandes/jour) :
- Coût mensuel : ~$4.50
- Coût annuel : ~$54

**Grand restaurant** (300 commandes/jour) :
- Coût mensuel : ~$9
- Coût annuel : ~$108

**ROI** : Les économies réalisées sur les remboursements (réduction des erreurs) compensent largement ces coûts.

---

## Conclusion

Ces cas d'usage montrent la polyvalence de Celeste Staff Meal dans différents contextes. Que vous soyez un restaurant indépendant ou une chaîne, la plateforme s'adapte à vos besoins spécifiques.

Pour des questions ou des cas d'usage personnalisés, n'hésitez pas à ouvrir une issue sur GitHub ou à contacter l'équipe.
