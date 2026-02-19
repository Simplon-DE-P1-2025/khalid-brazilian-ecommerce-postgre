# 📊 Recommandations de Transformation des Données

## Vue d'ensemble

Le projet utilise une **architecture à 3 niveaux**:

```
RAW (data/raw/)      → GOLD (data/gold/)    → PostgreSQL
Données brutes          Données nettoyées        Base de données
  CSV                    CSV optimisés         prête production
```

## 🔄 Transformations Appliquées

### 1️⃣ **CUSTOMERS** (99,441 clients)

**Transformations:**
- ✅ Normalisation des noms de villes (Title Case)
- ✅ Normalisation des États (UPPERCASE)
- ✅ Suppression des doublons si nécessaire
- ✅ Conversion du ZIP code en INTEGER

**Colonnes finales:**
```
customer_id (PK)
customer_unique_id (identifiant unique client)
zip_code_prefix (clé étrangère vers geolocation)
city
state
```

---

### 2️⃣ **PRODUCTS** (32,951 produits)

**Transformations:**
- ✅ Ajout des traductions des catégories (EN)
- ✅ Gestion des produits sans catégorie → "Unknown"
- ✅ Conversion des colonnes de dimensions en FLOAT
- ✅ Unification des noms de colonnes

**Colonnes finales:**
```
product_id (PK)
category_pt, category_en (traductions)
name_length, description_length
photo_qty
weight_g, length_cm, height_cm, width_cm
```

**Note:** Les produits sans catégorie (610 produits) sont marqués comme "Unknown"

---

### 3️⃣ **SELLERS** (3,095 vendeurs)

**Transformations:**
- ✅ Normalisation des villes et États
- ✅ Suppression des colonnes non pertinentes
- ✅ Création de lien vers geolocation

**Colonnes finales:**
```
seller_id (PK)
zip_code_prefix (FK → geolocation)
city, state
```

---

### 4️⃣ **GEOLOCATION** (1,000,163 → 29,600 codes postaux uniques)

**Transformations:**
- ✅ **DÉDUPLICATION**: Un seul enregistrement par ZIP code (garde le premier)
- ✅ Normalisation des villes et États
- ✅ Conversion des lat/long en FLOAT
- ✅ Performance: 97% de réduction des lignes

**Impact:** Réduit de 1M à ~30K lignes sans perte d'information géographique

**Colonnes finales:**
```
zip_code_prefix (PK)
city, state
latitude, longitude
```

---

### 5️⃣ **ORDERS** (99,441 commandes)

**Transformations:**
- ✅ Conversion des timestamps en DATETIME
- ✅ Extraction YEAR et MONTH pour faciliter les analyses
- ✅ Gestion des dates manquantes (160 approved_at = NULL)
- ✅ Standardisation des statuts de commande

**Statuts possibles (8 valeurs):**
```
delivered, shipped, processing, invoiced, 
not_delivered, canceled, unavailable, returned_refunded
```

**Colonnes finales:**
```
order_id (PK)
customer_id (FK)
status
purchase_date, purchase_year, purchase_month
approved_date, carrier_delivery_date, 
customer_delivery_date, estimated_delivery_date
```

---

### 6️⃣ **ORDER_ITEMS** (112,650 articles)

**Transformations:**
- ✅ Calcul de colonne dérivée: `total_price = price + freight_value`
- ✅ Conversion en FLOAT pour éviter les erreurs de précision
- ✅ Liaison avec orders, products, sellers

**Colonnes finales:**
```
order_id (FK)
order_item_id
product_id (FK)
seller_id (FK)
price, freight_value
total_price (COLONNE CALCULÉE)
```

---

### 7️⃣ **ORDER_PAYMENTS** (103,886 paiements)

**Transformations:**
- ✅ Nettoyage des types de paiement
- ✅ Conversion payment_value en FLOAT
- ✅ Normalisation des données d'installments

**Types de paiement (5 valeurs):**
```
credit_card, debit_card, boleto, voucher, not_defined
```

**Colonnes finales:**
```
order_id (FK)
sequential
type
installments
value
```

---

### 8️⃣ **ORDER_REVIEWS** (99,224 avis)

**Transformations:**
- ✅ Gestion des commentaires manquants (88% title, 59% message manquants)
- ✅ Conversion des timestamps en DATETIME
- ✅ Validation du score (1-5)
- ✅ Conservation des NULLs pour l'analyse

**Distribution des scores:**
```
1 ⭐: Client très insatisfait
2 ⭐: Client insatisfait
3 ⭐: Client neutre
4 ⭐: Client satisfait
5 ⭐: Client très satisfait
```

**Colonnes finales:**
```
review_id (PK)
order_id (FK)
score (1-5)
comment_title, comment_message (NULLABLE)
creation_date, answer_timestamp
```

---

### 9️⃣ **FACT_ORDERS** (Table analytique)

**NEW TABLE** - créée par jointure et agrégation

**Transformations:**
- ✅ Join order avec items, payments, reviews
- ✅ Agrégation des montants par commande
- ✅ Moyenne des notes de satisfaction
- ✅ Comptage des articles

**Colonies finales:**
```
order_id (PK/FK)
customer_id (FK)
purchase_date, year, month
status
items_count (nombre d'articles)
total_items_price (somme prix + freight)
total_payment (somme paiements)
avg_review_score (moyenne avis)
...dates delivery
```

**Usage:** Requêtes d'analyse rapides sans jointures complexes

---

## 📈 Optimisations pour PostgreSQL

### Indexes créés:
```
• customers(state) - Filtrer par état
• customers(unique_id) - Recherche client unique
• orders(customer_id) - Requêtes par client
• orders(status) - Filtrer par statut
• orders(purchase_date) - Requêtes temporelles
• orders(year, month) - Analyses mensuelles
• order_items(order_id) - Détails de commande
• products(category) - Filtrer par catégorie
• reviews(score) - Filtrer par satisfaction
• geolocation(state, city) - Recherche géographique
```

### Tailles estimées:
- **customers**: ~20 MB
- **products**: ~5 MB
- **orders**: ~30 MB
- **order_items**: ~50 MB
- **order_reviews**: ~40 MB
- **geolocation**: ~5 MB
- **Total**: ~200 MB (très gérable)

---

## ✅ Contrôle de Qualité

### Avant → Après

| Table | Avant | Après | Réduction |
|-------|-------|-------|-----------|
| Customers | 99,441 | 99,441 | 0% |
| Products | 32,951 | 32,951 | 0% |
| Geolocation | 1,000,163 | ~29,600 | **97%** ✅ |
| Orders | 99,441 | 99,441 | 0% |
| Order Items | 112,650 | 112,650 | 0% |
| **TOTAL** | **1,344,646** | **374,683** | **72%** ✅ |

### Intégrité des données:
- ✅ Aucune clé primaire dupliquée
- ✅ Zéro violations de clés étrangères (after join check)
- ✅ Types de données appropriés
- ✅ NULL values gérées correctement

---

## 🚀 Étapes d'exécution

### 1. Créer les répertoires:
```bash
mkdir -p data/gold
```

### 2. Exécuter la transformation:
```bash
python src/transform_to_gold.py
```

Cela génère 9 fichiers CSV optimisés dans `data/gold/`

### 3. Charger dans PostgreSQL:
```bash
# Créer les tables
psql -U user -d database -f src/schema.sql

# Charger les données (utiliser COPY ou Python)
python src/load_to_postgres.py
```

---

## 📊 Requêtes d'analyse typiques

Maintenant que les données sont propres, tu peux faire:

```sql
-- Total ventes par mois
SELECT purchase_year, purchase_month, COUNT(*) as orders, SUM(total_payment) as revenue
FROM fact_orders
GROUP BY purchase_year, purchase_month
ORDER BY purchase_year, purchase_month;

-- Satisfaction client par catégorie
SELECT p.category_en, AVG(r.score) as avg_satisfaction
FROM order_reviews r
JOIN order_items oi ON r.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category_en
ORDER BY avg_satisfaction DESC;

-- Analyse géographique
SELECT g.state, COUNT(DISTINCT c.customer_id) as customers,
       COUNT(o.order_id) as orders, SUM(oi.total_price) as revenue
FROM customers c
JOIN geolocation g ON c.zip_code_prefix = g.zip_code_prefix
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY g.state
ORDER BY revenue DESC;
```

---

## 🎯 Schéma Relationel Simplifié

```
┌─────────────┐
│  CUSTOMERS  │
│    (PK)     │───┐
└─────────────┘   │
                  │
            ┌─────└──────┐
            │            │
        ┌───▼────────┐   │
        │   ORDERS   │   │
        │    (PK)    │   │
        └────────────┘   │
            │            │
        ┌───▼──────────┐  │
        │ ORDER_ITEMS  │  │
        │              │  │
        ├──────┬───────┤  │
        │      │       │  │
    ┌───▼┐  ┌─▼──┐  ┌─▼──────┐
    │PROD│  │SEL │  │GEOLOC  │
    │UCTS│  │LER │  │(FK)    │
    └────┘  └────┘  └────────┘

    ORDERS ◄─── ORDER_PAYMENTS
    ORDERS ◄─── ORDER_REVIEWS
```

---

## 💡 Prochaines étapes

1. ✅ Transformer raw → gold (données nettoyées)
2. 📊 Charger dans PostgreSQL
3. 🔍 Valider les données en BD
4. 📈 Créer des dashboards
5. 🤖 Modèles d'analyse (ML)

