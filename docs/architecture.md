# Architecture du Système

Ce document décrit l'architecture technique de Celeste Staff Meal, incluant les diagrammes de flux de données, l'architecture système, les séquences d'interaction et les composants.

## Table des matières

- [Flux de données principal](#flux-de-données-principal)
- [Architecture système](#architecture-système)
- [Diagramme de séquence - Validation](#diagramme-de-séquence---validation)
- [Diagramme de composants](#diagramme-de-composants)
- [Flux de données - Dashboard](#flux-de-données---dashboard)

---

## Flux de données principal

Ce diagramme illustre le workflow complet de validation d'une commande, depuis le scan du QR code jusqu'à l'enregistrement du résultat.

```mermaid
flowchart TD
    Start([Utilisateur démarre la validation]) --> ScanQR[📱 Scanner QR Code]
    ScanQR --> ExtractQR{QR Code valide?}
    ExtractQR -->|Non| ErrorQR[❌ Erreur: QR Code invalide]
    ErrorQR --> ScanQR
    ExtractQR -->|Oui| OrderExtracted[✅ Commande extraite]
    OrderExtracted --> UploadImage[📸 Upload Image du Sac]
    UploadImage --> PredictAI[🤖 Prédiction IA - Analyse Image]
    PredictAI --> DetectedOrder[📦 Commande détectée]
    DetectedOrder --> Compare[🔍 Comparaison: Attendu vs Détecté]
    Compare --> ValidationResult{Validation OK?}
    ValidationResult -->|Oui| Complete[✅ Commande complète]
    ValidationResult -->|Non| Incomplete[⚠️ Articles manquants/excès]
    Complete --> GenerateExplanation[💬 Génération Explication]
    Incomplete --> GenerateExplanation
    GenerateExplanation --> GenerateAudio[🔊 Génération Audio Multi-langues]
    GenerateAudio --> SaveDB[💾 Sauvegarde Supabase]
    SaveDB --> DisplayResult[📊 Affichage Résultat]
    DisplayResult --> End([Fin])

    style Start fill:#e1f5ff
    style End fill:#e1f5ff
    style Complete fill:#d4edda
    style Incomplete fill:#fff3cd
    style ErrorQR fill:#f8d7da
```

---

## Architecture système

Ce diagramme montre la décomposition en couches de l'application et les interactions entre les différentes couches.

```mermaid
graph TB
    subgraph "Couche UI - Streamlit"
        UI_Validator[Order Validator Component]
        UI_Dashboard[Dashboard Component]
        UI_QRGen[QR Generator Component]
        UI_Config[AI Config Sidebar]
    end

    subgraph "Couche Service"
        Service_Validation[Validation Service<br/>compare_orders]
        Service_Prediction[Prediction Service<br/>predict_order]
        Service_Explanation[Explanation Service<br/>generate_explanation]
        Service_Statistics[Statistics Service<br/>calculate_statistics]
        Service_Alerts[Alerts Service<br/>detect_alerts]
    end

    subgraph "Couche Stockage - Supabase"
        DB_ValidationRecords[(validation_records)]
        DB_Orders[(orders)]
        DB_Client[Supabase Client]
    end

    subgraph "Intégration IA - Celeste AI"
        AI_ImageIntelligence[Image Intelligence<br/>Vision par ordinateur]
        AI_TextGeneration[Text Generation<br/>Explications]
        AI_SpeechGeneration[Speech Generation<br/>Audio multi-langues]
        AI_ImageGeneration[Image Generation<br/>Mode démo]
    end

    subgraph "Modèles de données - Pydantic"
        Models_Order[Order]
        Models_ValidationRecord[ValidationRecord]
        Models_ComparisonResult[ComparisonResult]
        Models_Statistics[Statistics]
    end

    UI_Validator --> Service_Validation
    UI_Validator --> Service_Prediction
    UI_Validator --> Service_Explanation
    UI_Dashboard --> Service_Statistics
    UI_Dashboard --> Service_Alerts

    Service_Validation --> Models_ComparisonResult
    Service_Prediction --> AI_ImageIntelligence
    Service_Prediction --> Models_Order
    Service_Explanation --> AI_TextGeneration
    Service_Explanation --> AI_SpeechGeneration
    Service_Statistics --> Models_Statistics

    Service_Validation --> DB_Client
    Service_Prediction --> DB_Client
    Service_Statistics --> DB_Client

    DB_Client --> DB_ValidationRecords
    DB_Client --> DB_Orders

    Models_Order --> DB_ValidationRecords
    Models_ValidationRecord --> DB_ValidationRecords
    Models_ComparisonResult --> DB_ValidationRecords

    style UI_Validator fill:#e3f2fd
    style UI_Dashboard fill:#e3f2fd
    style Service_Validation fill:#fff3e0
    style Service_Prediction fill:#fff3e0
    style DB_Client fill:#e8f5e9
    style AI_ImageIntelligence fill:#f3e5f5
```

---

## Diagramme de séquence - Validation

Ce diagramme détaille les interactions entre les composants lors du processus de validation d'une commande.

```mermaid
sequenceDiagram
    participant User as 👤 Utilisateur
    participant UI as UI Component<br/>(Order Validator)
    participant QR as QR Service<br/>(read_qr_order)
    participant Predict as Prediction Service<br/>(predict_order)
    participant AI as Celeste AI<br/>(Image Intelligence)
    participant Compare as Validation Service<br/>(compare_orders)
    participant Explain as Explanation Service<br/>(generate_explanation)
    participant DB as Supabase<br/>(save_validation_result)

    User->>UI: 1. Upload QR Code Image
    UI->>QR: 2. Decode QR Code
    QR-->>UI: 3. Order Object (expected_order)
    UI->>User: 4. Display Expected Order

    User->>UI: 5. Upload Bag Image
    UI->>Predict: 6. predict_order(bag_image, expected_order)
    Predict->>AI: 7. Image Analysis Request
    AI-->>Predict: 8. Detected Items JSON
    Predict-->>UI: 9. Order Object (detected_order)

    UI->>Compare: 10. compare_orders(expected, detected)
    Compare-->>UI: 11. ComparisonResult

    UI->>Explain: 12. generate_explanation(comparison_result)
    Explain->>AI: 13. Text Generation Request
    AI-->>Explain: 14. Explanation Text
    Explain->>AI: 15. Speech Generation Request
    AI-->>Explain: 16. Audio File
    Explain-->>UI: 17. Explanation + Audio

    UI->>DB: 18. save_validation_result(...)
    DB-->>UI: 19. Confirmation

    UI->>User: 20. Display Validation Result<br/>(✅ OK / ⚠️ Missing Items)
```

---

## Diagramme de composants

Ce diagramme montre les composants UI et leurs interactions avec les services backend.

```mermaid
graph LR
    subgraph "Streamlit Application"
        subgraph "Main Router"
            Main[main.py<br/>render]
        end

        subgraph "UI Components"
            Comp_Validator[order_validator.py<br/>Validation Workflow]
            Comp_Dashboard[dashboard.py<br/>Analytics Dashboard]
            Comp_QRGen[qr_generator.py<br/>Demo QR Generator]
            Comp_OrderList[order_list.py<br/>Saved Orders]
            Comp_Config[ai_config.py<br/>AI Configuration]
        end

        subgraph "UI Services"
            Svc_Validation[validation.py<br/>compare_orders]
            Svc_Prediction[prediction.py<br/>predict_order]
            Svc_Explanation[explanation.py<br/>generate_explanation]
            Svc_Statistics[statistics.py<br/>calculate_statistics]
            Svc_Alerts[alerts.py<br/>detect_alerts]
        end
    end

    subgraph "Core Library"
        Core_Storage[storage.py<br/>DB Operations]
        Core_QR[qr.py<br/>QR Encoding/Decoding]
        Core_Models[models.py<br/>Pydantic Models]
        Core_DB[database.py<br/>Supabase Client]
    end

    subgraph "External Services"
        Ext_Supabase[(Supabase<br/>PostgreSQL)]
        Ext_Celeste[Celeste AI<br/>Multi-capability]
    end

    Main --> Comp_Validator
    Main --> Comp_Dashboard
    Main --> Comp_QRGen
    Main --> Comp_OrderList
    Main --> Comp_Config

    Comp_Validator --> Svc_Validation
    Comp_Validator --> Svc_Prediction
    Comp_Validator --> Svc_Explanation
    Comp_Dashboard --> Svc_Statistics
    Comp_Dashboard --> Svc_Alerts
    Comp_Dashboard --> Svc_Explanation

    Svc_Validation --> Core_Models
    Svc_Prediction --> Ext_Celeste
    Svc_Explanation --> Ext_Celeste
    Svc_Statistics --> Core_Models

    Svc_Validation --> Core_Storage
    Svc_Prediction --> Core_Storage
    Svc_Statistics --> Core_Storage

    Comp_QRGen --> Core_QR
    Comp_Validator --> Core_QR

    Core_Storage --> Core_DB
    Core_DB --> Ext_Supabase

    style Main fill:#bbdefb
    style Comp_Validator fill:#c8e6c9
    style Comp_Dashboard fill:#c8e6c9
    style Svc_Validation fill:#fff9c4
    style Svc_Prediction fill:#fff9c4
    style Core_Storage fill:#f8bbd0
    style Ext_Supabase fill:#e1bee7
    style Ext_Celeste fill:#e1bee7
```

---

## Flux de données - Dashboard

Ce diagramme illustre le flux de données pour le tableau de bord analytique.

```mermaid
flowchart LR
    Start([Accès Dashboard]) --> LoadFilters[Chargement Filtres<br/>Date, Opérateur, Source]
    LoadFilters --> QueryDB[Requête Supabase<br/>get_all_validation_records]
    QueryDB --> FilterData[Filtrage Données<br/>Par opérateur/source/erreur]
    FilterData --> CalcStats[Calcul Statistiques<br/>calculate_statistics]
    CalcStats --> DetectAlerts[Détection Alertes<br/>detect_alerts]

    CalcStats --> Metrics[📈 Métriques<br/>Total, Complétude, Erreurs]
    DetectAlerts --> AlertDisplay[🚨 Affichage Alertes]

    CalcStats --> Charts[📊 Graphiques<br/>Plotly Visualizations]
    Charts --> Trends[Tendances<br/>Évolution temporelle]
    Charts --> Errors[Analyse Erreurs<br/>Par type/heure/jour]
    Charts --> Items[Articles Oubliés<br/>Top 10]
    Charts --> Performance[Performance Opérateurs<br/>Comparaison]

    FilterData --> AIInsights[💡 Recommandations IA<br/>generate_dashboard_insights]
    AIInsights --> ExtCeleste[Celeste AI<br/>Text Generation]
    ExtCeleste --> AIInsights
    AIInsights --> InsightsDisplay[Affichage Insights]

    FilterData --> Export[💾 Export Données<br/>CSV / Excel]

    Metrics --> Display[📱 Affichage Dashboard]
    AlertDisplay --> Display
    Trends --> Display
    Errors --> Display
    Items --> Display
    Performance --> Display
    InsightsDisplay --> Display
    Export --> Display

    Display --> End([Dashboard Rendu])

    style Start fill:#e1f5ff
    style End fill:#e1f5ff
    style CalcStats fill:#fff3e0
    style DetectAlerts fill:#ffebee
    style AIInsights fill:#f3e5f5
    style ExtCeleste fill:#e1bee7
```

---

## Technologies et dépendances

### Stack technique

- **Langage** : Python 3.12+ avec type hints complets
- **Framework UI** : Streamlit pour l'interface web interactive
- **IA** : Celeste AI pour les capacités multi-modales
- **Base de données** : Supabase (PostgreSQL) pour la persistance
- **Visualisation** : Plotly pour les graphiques interactifs
- **Validation** : Pydantic pour la validation de données type-safe
- **Traitement d'images** : Pillow (PIL) pour la manipulation d'images
- **Codes QR** : qrcode + zxing-cpp pour l'encodage/décodage

### Flux de données clés

1. **Validation** : QR Code → Image → IA → Comparaison → DB
2. **Dashboard** : DB → Filtrage → Statistiques → Visualisations → Export
3. **Explications** : Résultat → IA Text → IA Speech → Affichage

### Points d'intégration

- **Supabase** : Client singleton pour toutes les opérations DB
- **Celeste AI** : Configuration par capacité (Image, Text, Speech)
- **Streamlit** : Session state pour la gestion de l'état UI

---

## Notes d'architecture

### Principes de conception

1. **Séparation des responsabilités** : UI, Services, Stockage clairement séparés
2. **Type safety** : Pydantic models pour validation runtime + type hints pour validation statique
3. **Async-first** : Services async avec wrapper sync pour Streamlit
4. **Configuration flexible** : Clés API configurables via UI ou env vars
5. **Testabilité** : Services isolés et mockables pour tests unitaires

### Patterns utilisés

- **Singleton** : Supabase client (une instance globale)
- **Service Layer** : Logique métier dans `ui/services/`
- **Repository Pattern** : `storage.py` abstrait l'accès DB
- **Factory Pattern** : `create_client()` pour Celeste AI
- **Strategy Pattern** : Multi-providers IA (Google, OpenAI, etc.)

### Scalabilité

- **Stateless UI** : Streamlit session state pour état temporaire
- **Database** : Supabase scalable avec PostgreSQL
- **Caching** : Streamlit `@st.cache_data` pour optimiser les requêtes
- **Async** : Opérations IA non-bloquantes
