# Brazilian E-commerce Dataset

Projet pour télécharger et explorer le dataset Kaggle sur le commerce électronique brésilien.

## 📁 Structure du Projet

```
khalid-brazilian-ecommerce-postgre/
├── src/
│   ├── download_data.py             # Télécharge les données Kaggle
│   ├── transform_to_gold.py         # Transforme raw → gold
│   ├── load_to_docker.py            # Charge les données dans Docker
│   ├── load_to_postgres.py          # Charge les données PostgreSQL local
│   ├── analytics/                   # Scripts d'exploration
│   │   ├── analyze_data.py
│   │   ├── explore_data.py
│   │   ├── load_data.py
│   │   └── check_gold_quality.py
│   └── schema/
│       └── schema.sql               # Schéma PostgreSQL
│
├── data/
│   ├── raw/                         # Données brutes (Kaggle)
│   └── gold/                        # Données optimisées pour la BD
│
├── docker-compose.yml               # PostgreSQL + pgAdmin
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation

### 1. Créer et activer un environnement virtuel

**Sur PowerShell (Windows):**
```powershell
# Créer le venv
python -m venv venv

# Activer le venv
.\venv\Scripts\Activate.ps1
```

**Sur CMD (Windows):**
```cmd
# Créer le venv
python -m venv venv

# Activer le venv
venv\Scripts\activate.bat
```

**Sur macOS/Linux:**
```bash
# Créer le venv
python3 -m venv venv

# Activer le venv
source venv/bin/activate
```

### 2. Installer les dépendances

Une fois le venv activé:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

2. Configurer Kaggle (si ce n'est pas déjà fait):
   - Créer un compte sur [Kaggle](https://www.kaggle.com)
   - Accéder à Settings > API > Create new API token
   - Placer le fichier `kaggle.json` dans `~/.kaggle/`

### 3. Désactiver le venv (quand tu as terminé)
```bash
deactivate
```

## Utilisation

### 1. Télécharger et explorer les données brutes (RAW)

Télécharger depuis Kaggle:
```bash
python src/download_data.py
```

Analyser la structure:
```bash
python src/analytics/analyze_data.py
```

Charger et afficher les données:
```bash
python src/analytics/load_data.py
```

Exploration rapide:
```bash
python src/analytics/explore_data.py
```

### 2. Transformer les données (RAW → GOLD)

Nettoyer et optimiser les données pour PostgreSQL:
```bash
python src/transform_to_gold.py
```

Vérifier la qualité:
```bash
python src/analytics/check_gold_quality.py
```

Cela génère 9 fichiers CSV optimisés dans `data/gold/`:
- Données dédupliquées et nettoyées
- Types de données appropriés
- Colonnes calculées (ex: total_price)
- Prêt pour l'intégration PostgreSQL

**Exemple de transformations:**
- Geolocation: réduit de 1M à 19K lignes (97% de compression) ✨
- Dates converties en DATETIME
- Catégories avec traductions EN/PT
- Calculs de totaux par commande

### 3. Charger dans PostgreSQL (Docker)

```bash
# Démarrer les services (PostgreSQL + pgAdmin)
docker-compose up -d

# Charger les données
python src/load_to_docker.py

# Accéder à pgAdmin
# http://localhost:5050
# Email: admin@example.com | Password: admin

# Arrêter les services
docker-compose down
```

**Credentials:**
- PostgreSQL: `localhost:5432` (postgres / postgres)
- pgAdmin: `http://localhost:5050` (admin@example.com / admin)

## Dataset

Source: [Brazilian E-commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

Le dataset contient:
- **orders**: Informations des commandes
- **order_items**: Articles dans les commandes
- **customers**: Informations des clients
- **products**: Informations des produits
- **order_reviews**: Avis et notes des commandes
- Et d'autres fichiers connexes

## 📊 Schéma de la Base de Données

### Tables de Dimensions
```
┌──────────────────────────────────────┐
│         CUSTOMERS                    │ 99,441 clients
├──────────────────────────────────────┤
│ customer_id (PK)                     │
│ customer_unique_id                   │
│ zip_code_prefix (FK → geolocation)   │
│ city, state                          │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│         PRODUCTS                     │ 32,951 produits
├──────────────────────────────────────┤
│ product_id (PK)                      │
│ category_pt, category_en (traduit)   │
│ weight_g, length_cm, height_cm       │
│ photo_qty, description_length        │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│         SELLERS                      │ 3,095 vendeurs
├──────────────────────────────────────┤
│ seller_id (PK)                       │
│ zip_code_prefix (FK → geolocation)   │
│ city, state                          │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│         GEOLOCATION                  │ 19,015 ZIP codes
├──────────────────────────────────────┤
│ zip_code_prefix (PK)                 │
│ city, state                          │
│ latitude, longitude                  │
└──────────────────────────────────────┘
```

### Tables de Faits
```
┌──────────────────────────────────────┐
│         ORDERS                       │ 99,441 commandes
├──────────────────────────────────────┤
│ order_id (PK)                        │
│ customer_id (FK)                     │
│ status, purchase_date                │
│ purchase_year, purchase_month        │
│ approved_date, delivery_dates        │
└──────────────────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│         ORDER_ITEMS                  │ 112,650 articles
├──────────────────────────────────────┤
│ order_id (FK → orders)               │
│ product_id (FK → products)           │
│ seller_id (FK → sellers)             │
│ price, freight_value, total_price    │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│         ORDER_PAYMENTS               │ 103,886 paiements
├──────────────────────────────────────┤
│ order_id (FK)                        │
│ type (credit_card, debit_card, etc.) │
│ installments, value                  │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│         ORDER_REVIEWS                │ 99,224 avis
├──────────────────────────────────────┤
│ review_id (PK)                       │
│ order_id (FK)                        │
│ score (1-5 ⭐)                       │
│ comment_title, comment_message       │
│ creation_date, answer_timestamp      │
└──────────────────────────────────────┘
```

### Table Analytique
```
┌──────────────────────────────────────┐
│         FACT_ORDERS                  │ 99,441 (précalculé)
├──────────────────────────────────────┤
│ order_id (PK/FK)                     │
│ customer_id (FK)                     │
│ purchase_date, year, month           │
│ status                               │
│ items_count                          │
│ total_items_price                    │
│ total_payment                        │
│ avg_review_score                     │
└──────────────────────────────────────┘
```

**note:** `FACT_ORDERS` est une table dénormalisée pour l'analyse rapide sans jointures complexes.

## 📈 Statistiques

| Métrique | Valeur |
|----------|--------|
| Total clients | 99,441 |
| Total commandes | 99,441 |
| Total articles vendus | 112,650 |
| Total produits | 32,951 |
| Total vendeurs | 3,095 |
| Total avis | 99,224 |
| Codes postaux uniques | 19,015 |
| **Taille totale BD** | **~79 MB** |

### Transformations appliquées
- ✅ Geolocation: 1,000,163 → 19,015 lignes (-98%)
- ✅ Dates converties en DATETIME
- ✅ Catégories traduites EN/PT
- ✅ Colonnes calculées (total_price)
- ✅ Zéro doublons de clés primaires

Pour plus de détails: voir [TRANSFORMATION_GUIDE.md](TRANSFORMATION_GUIDE.md)

## Notes

- Le premier téléchargement peut prendre du temps selon votre connexion internet
- Les données sont sauvegardées localement dans `data/raw/` pour un accès rapide

## Tips & Aide

### Comment savoir si mon venv est activé?

Quand ton venv est activé, tu devrais voir `(venv)` au début de ta ligne de commande:

```
(venv) PS D:\data eng\khalid-brazilian-ecommerce-postgre>
```

### Python dans VS Code

Si Python n'utilise pas le venv automatiquement:
1. Ouvre la palette de commandes: `Ctrl + Shift + P`
2. Tape: `Python: Select Interpreter`
3. Choisis le chemin avec `./venv`
