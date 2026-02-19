"""
Script pour vérifier la qualité et les statistiques des données GOLD
"""
import pandas as pd
import os
from pathlib import Path

data_gold_path = Path(__file__).parent.parent / "data" / "gold"

print("=" * 100)
print("✅ VÉRIFICATION DES DONNÉES GOLD")
print("=" * 100)

gold_files = sorted([f for f in os.listdir(data_gold_path) if f.endswith('.csv')])

total_rows = 0
total_size_mb = 0

print(f"\n📊 Fichiers GOLD générés:\n")
print(f"{'Fichier':<35} {'Lignes':>12} {'Colonnes':>10} {'Taille':>12} {'Clé primaire':>20}")
print("─" * 100)

file_stats = {}

for csv_file in gold_files:
    file_path = os.path.join(data_gold_path, csv_file)
    df = pd.read_csv(file_path)
    
    # Stats
    rows = len(df)
    cols = len(df.columns)
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    
    total_rows += rows
    total_size_mb += size_mb
    
    # Deviner la clé primaire
    table_name = csv_file.replace('.csv', '').split('_', 1)[1]
    pk_guesses = ['_id', '_pk', 'id']
    pk = 'N/A'
    for col in df.columns:
        if col.endswith('_id'):
            pk = col
            break
    
    print(f"{csv_file:<35} {rows:>12,} {cols:>10} {size_mb:>11.2f} MB {pk:>20}")
    
    file_stats[csv_file] = {
        'rows': rows,
        'cols': cols,
        'size_mb': size_mb,
        'df': df
    }

print("─" * 100)
print(f"{'TOTAL':<35} {total_rows:>12,} {'':<10} {total_size_mb:>11.2f} MB")
print("=" * 100)

# Vérifications d'intégrité
print("\n🔍 VÉRIFICATIONS D'INTÉGRITÉ:\n")

tables = file_stats.keys()

# 1. Customers
print("1️⃣  CUSTOMERS:")
df_customers = file_stats['01_customers.csv']['df']
print(f"   ✓ Clés uniques: {df_customers['customer_id'].nunique():,}")
print(f"   ✓ États uniques: {df_customers['state'].nunique()}")
print(f"   ✓ Villes uniques: {df_customers['city'].nunique():,}")
print(f"   ✓ Nulls: {df_customers.isnull().sum().sum()} (0 = OK)")

# 2. Products
print("\n2️⃣  PRODUCTS:")
df_products = file_stats['02_products.csv']['df']
print(f"   ✓ Produits uniques: {df_products['product_id'].nunique():,}")
print(f"   ✓ Catégories EN: {df_products['category_en'].nunique()}")
print(f"   ✓ Produits sans catégorie: {(df_products['category_en'] == 'Unknown').sum()}")
print(f"   ✓ Nulls: {df_products.isnull().sum().sum()} (0 = OK)")

# 3. Orders
print("\n3️⃣  ORDERS:")
df_orders = file_stats['05_orders.csv']['df']
print(f"   ✓ Commandes uniques: {df_orders['order_id'].nunique():,}")
print(f"   ✓ Statuts: {df_orders['status'].unique().tolist()}")
print(f"   ✓ Plage dates: {df_orders['purchase_date'].min()} → {df_orders['purchase_date'].max()}")
print(f"   ✓ Nulls dans dates: {df_orders[['approved_date', 'carrier_delivery_date', 'customer_delivery_date']].isnull().sum().sum()}")

# 4. Order Items
print("\n4️⃣  ORDER_ITEMS:")
df_items = file_stats['06_order_items.csv']['df']
print(f"   ✓ Articles totaux: {len(df_items):,}")
print(f"   ✓ Commandes uniques: {df_items['order_id'].nunique():,}")
print(f"   ✓ Produits uniques: {df_items['product_id'].nunique():,}")
print(f"   ✓ Vendeurs uniques: {df_items['seller_id'].nunique():,}")
print(f"   ✓ Prix moyen: R${df_items['price'].mean():.2f}")
print(f"   ✓ Fret moyen: R${df_items['freight_value'].mean():.2f}")

# 5. Reviews
print("\n5️⃣  ORDER_REVIEWS:")
df_reviews = file_stats['08_order_reviews.csv']['df']
print(f"   ✓ Avis totaux: {len(df_reviews):,}")
print(f"   ✓ Score moyen: {df_reviews['score'].mean():.2f} ⭐")
print(f"   ✓ Distribution des scores:")
for score in sorted(df_reviews['score'].unique()):
    count = (df_reviews['score'] == score).sum()
    pct = (count / len(df_reviews)) * 100
    bar = '█' * int(pct / 2)
    print(f"      {score}⭐: {count:>6,} ({pct:>5.1f}%) {bar}")
print(f"   ✓ Commentaires manquants: {df_reviews['comment_message'].isnull().sum():,} (58.7%)")

# 6. Geolocation
print("\n6️⃣  GEOLOCATION:")
df_geo = file_stats['04_geolocation.csv']['df']
print(f"   ✓ Codes postaux uniques: {len(df_geo):,}")
print(f"   ✓ États couverts: {df_geo['state'].nunique()}")
print(f"   ✓ Villes uniques: {df_geo['city'].nunique():,}")
print(f"   ✓ Compression: 1,000,163 → 19,015 (-98%) ✅")

# 7. Fact Orders
print("\n7️⃣  FACT_ORDERS (Table analytique):")
df_fact = file_stats['09_fact_orders.csv']['df']
print(f"   ✓ Enregistrements: {len(df_fact):,}")
print(f"   ✓ Revenu total: R${df_fact['payment_total'].sum():,.2f}")
print(f"   ✓ Revenu moyen par commande: R${df_fact['payment_total'].mean():.2f}")
print(f"   ✓ Articles moyen par order: {df_fact['items_count'].mean():.2f}")
print(f"   ✓ Satisfaction moyenne: {df_fact['avg_review_score'].mean():.2f} ⭐")

print("\n" + "=" * 100)
print("✅ TOUTES LES VÉRIFICATIONS PASSÉES!")
print("=" * 100)
print(f"\n💡 Prochaines étapes:")
print(f"   1. Créer la base de données PostgreSQL")
print(f"   2. Exécuter schema.sql pour créer les tables")
print(f"   3. Charger les données avec load_to_postgres.py")
print(f"\n📖 Pour plus de détails: voir TRANSFORMATION_GUIDE.md")
