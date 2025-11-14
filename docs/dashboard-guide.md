# Guide Utilisateur - Dashboard

## Vue d'ensemble

Le dashboard vous permet d'analyser les performances de validation des commandes et d'identifier les problèmes de production.

## Sections principales

### 📈 Métriques principales

Affiche 4 indicateurs clés avec comparaison période précédente :
- **Total commandes** : Nombre total de commandes validées
- **Commandes complètes** : Nombre de commandes sans erreur
- **Taux de complétude** : Pourcentage de commandes complètes (objectif: 95%)
- **Taux d'erreur** : Pourcentage de commandes avec erreurs

Les indicateurs de tendance (↑↓) montrent l'évolution par rapport à la période précédente.

### 🚨 Alertes

Alertes automatiques détectées :
- **🔴 Critique** : Taux d'erreur > 20%
- **🟡 Attention** : Taux de complétude < 95%, pics d'erreurs, articles fréquemment oubliés
- **ℹ️ Info** : Heures critiques identifiées

### 💡 Recommandations IA

Génère automatiquement des recommandations actionnables basées sur vos données :
- Cliquez sur "✨ Générer" pour analyser vos données
- Les recommandations sont formatées par niveau de priorité
- Chaque recommandation propose une action concrète

### 🔍 Filtres avancés

Permet de filtrer les données par :
- **Opérateur(s)** : Sélectionner un ou plusieurs opérateurs
- **Source(s)** : UberEats ou Deliveroo
- **Type(s) d'erreur** : Articles manquants, quantités insuffisantes, etc.

### 📊 Visualisations

#### Onglet "📈 Tendances"
- **Évolution du taux de complétude** : Graphique en aires avec ligne d'objectif (95%)
- **Nombre d'erreurs par jour** : Graphique en barres pour suivre l'évolution

#### Onglet "🔍 Analyse des erreurs"
- **Répartition des types d'erreurs** : Graphique en secteurs (pie chart)
- **Heatmap erreurs** : Visualisation des erreurs par jour et heure
- **Erreurs par heure** : Graphique en barres avec heures critiques
- **Erreurs par jour** : Graphique en barres par jour de la semaine

#### Onglet "📦 Articles"
- **Top 10 articles oubliés** : Graphique en barres horizontales
- **Tableau détaillé** : Liste complète des articles oubliés

#### Onglet "👥 Performance"
- **Taux de complétude par opérateur** : Comparaison des performances
- **Taux d'erreur par opérateur** : Identification des opérateurs à risque
- **Tableau détaillé** : Métriques complètes par opérateur
- **Articles oubliés par opérateur** : Détail des erreurs par opérateur

#### Onglet "📱 Sources"
- **Comparaison UberEats vs Deliveroo** : Graphiques comparatifs
- **Répartition des commandes** : Graphique en secteurs
- **Types d'erreurs par source** : Analyse détaillée

### 💾 Export des données

- **CSV** : Export avec colonnes calculées (date, heure, jour, nombre d'erreurs) et résumé
- **Excel** : Export formaté avec en-têtes stylisés et résumé (nécessite openpyxl)

## Interprétation des recommandations IA

Les recommandations sont classées par priorité :

- **🔴 CRITIQUE** : Actions urgentes à prendre immédiatement
- **🟡 ATTENTION/FOCUS** : Points à surveiller et améliorer
- **💡 ACTION** : Recommandations pratiques pour améliorer les processus
- **🟢 OK** : Confirmations positives

## Conseils d'utilisation

1. **Période d'analyse** : Utilisez des périodes de 7-30 jours pour des analyses significatives
2. **Filtres** : Combinez plusieurs filtres pour des analyses ciblées
3. **Alertes** : Consultez régulièrement les alertes pour détecter les problèmes rapidement
4. **Recommandations IA** : Régénérez les recommandations après avoir appliqué des filtres
5. **Export** : Utilisez l'export Excel pour des analyses approfondies dans Excel

## Seuils et objectifs

- **Objectif taux de complétude** : 95%
- **Seuil critique taux d'erreur** : 20%
- **Seuil d'alerte articles oubliés** : 5+ occurrences
