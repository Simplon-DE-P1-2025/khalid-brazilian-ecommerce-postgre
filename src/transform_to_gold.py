"""
Script pour transformer les données brutes (raw) en données optimisées (gold)
prêtes pour PostgreSQL
"""
import pandas as pd
import os
from pathlib import Path
from datetime import datetime

# Chemins
data_raw_path = Path(__file__).parent.parent / "data" / "raw"
data_gold_path = Path(__file__).parent.parent / "data" / "gold"
data_gold_path.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("🛠️  TRANSFORMATION DES DONNÉES (RAW → GOLD)")
print("=" * 80)

# ============================================================================
# 1. CUSTOMERS - Nettoyer et transformer
# ============================================================================
print("\n1️⃣  Transforming customers...")
customers = pd.read_csv(data_raw_path / "olist_customers_dataset.csv")

# Garder les colonnes utiles
customers_gold = customers[[
    'customer_id', 'customer_unique_id', 'customer_zip_code_prefix', 
    'customer_city', 'customer_state'
]].copy()

# Renommer pour clarity
customers_gold.columns = [
    'customer_id', 'customer_unique_id', 'zip_code_prefix', 
    'city', 'state'
]

# Normaliser les états en majuscules
customers_gold['state'] = customers_gold['state'].str.upper()
customers_gold['city'] = customers_gold['city'].str.title()

# Assurer que le code postal est une chaîne de 5 caractères (padding avec zéros)
customers_gold['zip_code_prefix'] = customers_gold['zip_code_prefix'].astype(str).str.zfill(5)

customers_gold.to_csv(data_gold_path / "01_customers.csv", index=False)
print(f"   ✓ {len(customers_gold):,} clients | {len(customers_gold.columns)} colonnes")

# ============================================================================
# 2. PRODUCTS - Nettoyer et ajouter traduction des catégories
# ============================================================================
print("\n2️⃣  Transforming products...")
products = pd.read_csv(data_raw_path / "olist_products_dataset.csv")
categories = pd.read_csv(data_raw_path / "product_category_name_translation.csv")

# Joindre avec les traductions
products_gold = products.merge(
    categories, 
    on='product_category_name', 
    how='left'
)

# Garder les colonnes utiles
products_gold = products_gold[[
    'product_id', 'product_category_name', 'product_category_name_english',
    'product_name_lenght', 'product_description_lenght', 'product_photos_qty',
    'product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm'
]].copy()

# Renommer pour clarity
products_gold.columns = [
    'product_id', 'category_pt', 'category_en', 'name_length', 'description_length', 
    'photo_qty', 'weight_g', 'length_cm', 'height_cm', 'width_cm'
]

# Remplir les valeurs manquantes
products_gold['category_en'] = products_gold['category_en'].fillna('Unknown')
products_gold['category_pt'] = products_gold['category_pt'].fillna('Desconhecido')

products_gold.to_csv(data_gold_path / "02_products.csv", index=False)
print(f"   ✓ {len(products_gold):,} produits | {len(products_gold.columns)} colonnes")

# ============================================================================
# 3. SELLERS - Nettoyer
# ============================================================================
# 3. GEOLOCATION - Simplifier (une seule entrée par zip code)
# ============================================================================
print("\n3️⃣  Transforming geolocation...")
geolocation = pd.read_csv(data_raw_path / "olist_geolocation_dataset.csv")

# Garder une seule ligne par zip code (prendre la première)
geo_gold = geolocation.drop_duplicates(
    subset=['geolocation_zip_code_prefix'], 
    keep='first'
)

geo_gold = geo_gold[[
    'geolocation_zip_code_prefix', 'geolocation_city', 'geolocation_state',
    'geolocation_lat', 'geolocation_lng'
]].copy()

geo_gold.columns = ['zip_code_prefix', 'city', 'state', 'latitude', 'longitude']
geo_gold['state'] = geo_gold['state'].str.upper()
geo_gold['city'] = geo_gold['city'].str.title()

# Standardiser le code postal
geo_gold['zip_code_prefix'] = geo_gold['zip_code_prefix'].astype(str).str.zfill(5)

geo_gold.to_csv(data_gold_path / "03_geolocation.csv", index=False)
print(f"   ✓ {len(geo_gold):,} codes postaux | {len(geo_gold.columns)} colonnes")

# ============================================================================
# 4. SELLERS - Nettoyer
# ============================================================================
print("\n4️⃣  Transforming sellers...")
sellers = pd.read_csv(data_raw_path / "olist_sellers_dataset.csv")

sellers_gold = sellers[[
    'seller_id', 'seller_zip_code_prefix', 'seller_city', 'seller_state'
]].copy()

sellers_gold.columns = ['seller_id', 'zip_code_prefix', 'city', 'state']
sellers_gold['state'] = sellers_gold['state'].str.upper()
sellers_gold['city'] = sellers_gold['city'].str.title()

# Standardiser le code postal
sellers_gold['zip_code_prefix'] = sellers_gold['zip_code_prefix'].astype(str).str.zfill(5)

# Filtrer pour ne garder que les zip_codes qui existent dans geolocation
geo_zips = geo_gold['zip_code_prefix'].unique()
sellers_gold = sellers_gold[sellers_gold['zip_code_prefix'].isin(geo_zips)].copy()

sellers_gold.to_csv(data_gold_path / "04_sellers.csv", index=False)
print(f"   ✓ {len(sellers_gold):,} vendeurs | {len(sellers_gold.columns)} colonnes")

# ============================================================================
# 5. ORDERS - Transformer les dates
# ============================================================================
print("\n5️⃣  Transforming orders...")
orders = pd.read_csv(data_raw_path / "olist_orders_dataset.csv")

orders_gold = orders[[
    'order_id', 'customer_id', 'order_status', 'order_purchase_timestamp',
    'order_approved_at', 'order_delivered_carrier_date', 
    'order_delivered_customer_date', 'order_estimated_delivery_date'
]].copy()

orders_gold.columns = [
    'order_id', 'customer_id', 'status', 'purchase_date',
    'approved_date', 'carrier_delivery_date', 'customer_delivery_date', 
    'estimated_delivery_date'
]

# Convertir en datetime
date_columns = [
    'purchase_date', 'approved_date', 'carrier_delivery_date',
    'customer_delivery_date', 'estimated_delivery_date'
]
for col in date_columns:
    orders_gold[col] = pd.to_datetime(orders_gold[col], errors='coerce')

# Extraire l'année et le mois
orders_gold['purchase_year'] = orders_gold['purchase_date'].dt.year
orders_gold['purchase_month'] = orders_gold['purchase_date'].dt.month

orders_gold.to_csv(data_gold_path / "05_orders.csv", index=False)
print(f"   ✓ {len(orders_gold):,} commandes | {len(orders_gold.columns)} colonnes")

# ============================================================================
# 6. ORDER_ITEMS - Transformer et calculer totaux
# ============================================================================
print("\n Transforming order_items...")
order_items = pd.read_csv(data_raw_path / "olist_order_items_dataset.csv")

order_items_gold = order_items[[
    'order_id', 'order_item_id', 'product_id', 'seller_id', 
    'price', 'freight_value'
]].copy()

# Convertir en float
order_items_gold['price'] = order_items_gold['price'].astype(float)
order_items_gold['freight_value'] = order_items_gold['freight_value'].astype(float)

# Calculer les totaux
order_items_gold['total_price'] = order_items_gold['price'] + order_items_gold['freight_value']

# Enrichir avec des infos de commande pour faciliter l'analyse (Fact Sales)
# Cela évite des jointures complexes pour des requêtes simples (ex: Ventes par Client)
order_items_gold = order_items_gold.merge(
    orders_gold[['order_id', 'customer_id', 'purchase_date', 'status']],
    on='order_id',
    how='left'
)

order_items_gold.to_csv(data_gold_path / "06_order_items.csv", index=False)
print(f"   ✓ {len(order_items_gold):,} articles | {len(order_items_gold.columns)} colonnes")

# ============================================================================
# 7. ORDER_PAYMENTS - Transformer
# ============================================================================
print("\n7️⃣  Transforming order_payments...")
payments = pd.read_csv(data_raw_path / "olist_order_payments_dataset.csv")

payments_gold = payments[[
    'order_id', 'payment_type', 
    'payment_installments', 'payment_value'
]].copy()

payments_gold.columns = [
    'order_id', 'type', 'installments', 'value'
]

payments_gold['value'] = payments_gold['value'].astype(float)

payments_gold.to_csv(data_gold_path / "07_order_payments.csv", index=False)
print(f"   ✓ {len(payments_gold):,} paiements | {len(payments_gold.columns)} colonnes")

# ============================================================================
# 8. ORDER_REVIEWS - Transformer
# ============================================================================
print("\n8️⃣  Transforming order_reviews...")
reviews = pd.read_csv(data_raw_path / "olist_order_reviews_dataset.csv")

reviews_gold = reviews[[
    'review_id', 'order_id', 'review_score', 'review_comment_title',
    'review_comment_message', 'review_creation_date', 'review_answer_timestamp'
]].copy()

reviews_gold.columns = [
    'review_id', 'order_id', 'score', 'comment_title', 'comment_message',
    'creation_date', 'answer_timestamp'
]

# Convertir en datetime
reviews_gold['creation_date'] = pd.to_datetime(reviews_gold['creation_date'])
reviews_gold['answer_timestamp'] = pd.to_datetime(reviews_gold['answer_timestamp'])

reviews_gold.to_csv(data_gold_path / "08_order_reviews.csv", index=False)
print(f"   ✓ {len(reviews_gold):,} avis | {len(reviews_gold.columns)} colonnes")

# ============================================================================
# 9. FACT_ORDERS (Table centralisée pour l'analyse)
# ============================================================================
print("\n9️⃣  Creating FACT_ORDERS (analytical table)...")

# Joindre tous les éléments
fact_orders = orders_gold.merge(
    order_items_gold.groupby('order_id').agg({
        'total_price': 'sum',
        'product_id': 'count'  # Nombre d'articles
    }).reset_index().rename(columns={'product_id': 'items_count'}),
    on='order_id',
    how='left'
)

fact_orders = fact_orders.merge(
    payments_gold.groupby('order_id')['value'].sum().reset_index().rename(columns={'value': 'payment_total'}),
    on='order_id',
    how='left'
)

fact_orders = fact_orders.merge(
    reviews_gold[['order_id', 'score']].groupby('order_id')['score'].mean().reset_index().rename(columns={'score': 'avg_review_score'}),
    on='order_id',
    how='left'
)

# Réorganiser et renommer
fact_orders = fact_orders[[
    'order_id', 'customer_id', 'purchase_date', 'purchase_year', 'purchase_month',
    'status', 'items_count', 'total_price', 'payment_total', 'avg_review_score',
    'approved_date', 'carrier_delivery_date', 'customer_delivery_date',
    'estimated_delivery_date'
]].copy()

fact_orders['total_price'] = fact_orders['total_price'].fillna(0)
fact_orders['payment_total'] = fact_orders['payment_total'].fillna(0)

fact_orders.to_csv(data_gold_path / "09_fact_orders.csv", index=False)
print(f"   ✓ {len(fact_orders):,} fact records | {len(fact_orders.columns)} colonnes")

# ============================================================================
# Résumé
# ============================================================================
print("\n" + "=" * 80)
print("✅ TRANSFORMATION COMPLÉTÉE!")
print("=" * 80)
print(f"\nFichiers créés dans: {data_gold_path}")
print(f"\n📊 Statistiques globales:")
print(f"   • Clients: {len(customers_gold):,}")
print(f"   • Commandes: {len(orders_gold):,}")
print(f"   • Articles de commande: {len(order_items_gold):,}")
print(f"   • Produits: {len(products_gold):,}")
print(f"   • Vendeurs: {len(sellers_gold):,}")
print(f"   • Avis: {len(reviews_gold):,}")
print(f"   • Codes postaux: {len(geo_gold):,}")
print(f"\n💾 Fichiers générés:")

gold_files = sorted([f for f in os.listdir(data_gold_path) if f.endswith('.csv')])
for file in gold_files:
    file_path = os.path.join(data_gold_path, file)
    size = os.path.getsize(file_path) / (1024 * 1024)
    print(f"   • {file:30s} ({size:.2f} MB)")
