# 🔧 Scripts & Outils

## 📁 Organisation

```
src/
├── 📥 Scripts de Chargement/Transformation
│   ├── download_data.py        # Télécharge depuis Kaggle
│   ├── transform_to_gold.py    # Raw → Gold (nettoyage)
│   └── load_to_postgres.py     # Gold → PostgreSQL
│
├── 📊 analytics/               # Exploration & Analyse
│   ├── analyze_data.py
│   ├── explore_data.py
│   ├── load_data.py
│   ├── check_gold_quality.py
│   └── README.md
│
└── 🗄️ schema/                 # Base de Données
    ├── schema.sql
    └── README.md
```

## 🚀 Workflow Recommandé

### Phase 1: Préparation
```bash
# Télécharger les données
python src/download_data.py
```

### Phase 2: Exploration
```bash
# Analyser les données brutes
python src/analytics/analyze_data.py
python src/analytics/explore_data.py
python src/analytics/load_data.py
```

### Phase 3: Transformation
```bash
# Transformer raw → gold avec nettoyage
python src/transform_to_gold.py

# Vérifier la qualité
python src/analytics/check_gold_quality.py
```

### Phase 4: Intégration PostgreSQL
```bash
# Créer le schéma
psql -U postgres -d brazilian_ecommerce -f src/schema/schema.sql

# Charger les données
python src/load_to_postgres.py
```

---

## 📖 Scripts en Détail

### 🔽 **download_data.py**
**Télécharge** le dataset Brazilian E-commerce depuis Kaggle.

- Nécessite: `kagglehub` et configuration Kaggle API
- Output: Fichiers CSV dans `data/raw/`

### 🔄 **transform_to_gold.py**
**Transforme** les données raw en données optimisées (gold).

- Inputs: Fichiers CSV bruts
- Transformations: Nettoyage, déduplication, normalisation, calculs
- Outputs: 9 fichiers CSV dans `data/gold/`

### 📤 **load_to_postgres.py**
**Charge** les données gold dans PostgreSQL.

- Inputs: Fichiers CSV dans `data/gold/`
- Supports: `--host`, `--user`, `--password`, `--database`
- Output: Données chargées dans les tables de la BD

### 📊 **analytics/analyze_data.py**
**Analyse détaillée** des CSVs bruts.

- Affiche: Types, dimensions, valeurs manquantes
- Usage: Comprendre la structure des données

### 🔍 **analytics/explore_data.py**
**Exploration rapide** avec aperçus.

- Affiche: Colonnes et premières lignes
- Usage: Vue d'ensemble rapide

### 💾 **analytics/load_data.py**
**Charge** les CSVs bruts en mémoire.

- Affiche: Infos de chargement et stats
- Usage: Vérification du chargement

### ✅ **analytics/check_gold_quality.py**
**Vérifications de qualité** des données transformées.

- Checks: Intégrité, statistiques, distribution
- Affiche: Rapports détaillés
- Usage: Valider les transformations

### 🗄️ **schema/schema.sql**
**Définition complète** du schéma PostgreSQL.

- Contient: Toutes les tables, indexes, contraintes
- Usage: `psql -f src/schema/schema.sql`

---

## 💡 Tips

1. **Commencer par explorer**: `python src/analytics/analyze_data.py`
2. **Vérifier après transformation**: `python src/analytics/check_gold_quality.py`
3. **Lire les READMEs**: Chaque dossier a son propre README.md
4. **Consulter TRANSFORMATION_GUIDE.md**: Pour les détails des transformations
