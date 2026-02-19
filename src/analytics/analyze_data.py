"""
Script pour analyser les CSV bruts et proposer un schéma pour PostgreSQL
"""
import pandas as pd
import os
from pathlib import Path

data_raw_path = Path(__file__).parent.parent / "data" / "raw"

print("=" * 100)
print("ANALYSE DÉTAILLÉE DU DATASET BRAZILIAN E-COMMERCE")
print("=" * 100)

# Charger tous les CSVs
csv_files = sorted([f for f in os.listdir(data_raw_path) if f.endswith('.csv')])
dataframes = {}

for csv_file in csv_files:
    file_path = os.path.join(data_raw_path, csv_file)
    df = pd.read_csv(file_path)
    dataframes[csv_file.replace('.csv', '')] = df

# Analyser chaque dataset
for name, df in dataframes.items():
    print(f"\n{'─' * 100}")
    print(f"📊 {name}")
    print(f"{'─' * 100}")
    print(f"  Lignes: {len(df):,} | Colonnes: {len(df.columns)}")
    print(f"\n  Colonnes et types:")
    
    for col in df.columns:
        dtype = df[col].dtype
        non_null = df[col].notna().sum()
        null_count = df[col].isna().sum()
        
        # Afficher des stats
        if dtype == 'object':
            unique = df[col].nunique()
            print(f"    - {col:40s} | {str(dtype):15s} | Non-null: {non_null:7,} | Null: {null_count:6,} | Unique: {unique:6,}")
        elif 'datetime' in str(dtype):
            print(f"    - {col:40s} | {str(dtype):15s} | Non-null: {non_null:7,} | Null: {null_count:6,}")
        else:
            min_val = df[col].min() if null_count < len(df) else 'N/A'
            max_val = df[col].max() if null_count < len(df) else 'N/A'
            print(f"    - {col:40s} | {str(dtype):15s} | Non-null: {non_null:7,} | Null: {null_count:6,}")
    
    print(f"\n  Aperçu (3 premières lignes):")
    print(df.head(3).to_string())
    
    # Infos manquantes
    if df.isnull().sum().sum() > 0:
        print(f"\n  ⚠️  Données manquantes:")
        for col in df.columns:
            null_count = df[col].isna().sum()
            if null_count > 0:
                pct = (null_count / len(df)) * 100
                print(f"    - {col}: {null_count} ({pct:.1f}%)")

print("\n" + "=" * 100)
print("RELATIONS DE CLÉS ÉTRANGÈRES SUGGÉRÉES")
print("=" * 100)
print("""
1. orders → customers (customer_id)
2. order_items → orders (order_id)
3. order_items → products (product_id)
4. order_items → sellers (seller_id)
5. order_payments → orders (order_id)
6. order_reviews → orders (order_id)
7. orders → geolocation (customer_zip_code_prefix)
8. sellers → geolocation (seller_zip_code_prefix)
9. products → product_category_name_translation (product_category_name)
""")
