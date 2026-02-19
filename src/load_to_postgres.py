import pandas as pd
import os
from pathlib import Path
from sqlalchemy import create_engine, text
import time

# ============================================================================
# CONFIGURATION
# ============================================================================

# Chemins
data_gold_path = Path(__file__).parent.parent / "data" / "gold"

# Paramètres de connexion (basés sur ton docker-compose)
DB_USER = "postgres"
DB_PASS = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "brazilian_ecommerce"

# Chaîne de connexion SQLAlchemy
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def get_engine():
    """Crée la connexion à la base de données"""
    return create_engine(DATABASE_URL)

def load_csv_to_postgres(file_path, table_name, engine):
    """Charge un fichier CSV dans PostgreSQL"""
    print(f"   ⏳ Chargement de {table_name}...")
    
    # Lecture du CSV
    df = pd.read_csv(file_path)
    
    # Supprimer la table avec CASCADE pour éviter les erreurs de dépendances (FK)
    with engine.connect() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
        conn.commit()

    # Chargement dans SQL (replace = écrase la table si elle existe)
    # chunksize aide à ne pas surcharger la mémoire pour les gros fichiers
    df.to_sql(table_name, engine, if_exists='replace', index=False, chunksize=10000)
    
    print(f"   ✅ {table_name} chargé ({len(df):,} lignes)")

def add_primary_keys(engine):
    """Ajoute les contraintes de clé primaire pour un schéma propre"""
    print("\n🔧 Optimisation du schéma (Ajout des Clés Primaires)...")
    
    # Dictionnaire : Table -> Colonne(s) Clé Primaire
    pks = {
        "customers": "customer_id",
        "geolocation": "zip_code_prefix",
        "products": "product_id",
        "sellers": "seller_id",
        "orders": "order_id",
        "order_items": ["order_id", "order_item_id"], # Clé composite
        "order_payments": None, # Pas d'ID unique évident, on laisse sans PK ou on crée un index
        "order_reviews": "review_id",
        "fact_orders": "order_id"
    }

    with engine.connect() as conn:
        for table, pk_col in pks.items():
            if pk_col:
                try:
                    # Si c'est une liste, on joint par des virgules (ex: order_id, order_item_id)
                    pk_str = ", ".join(pk_col) if isinstance(pk_col, list) else pk_col
                    
                    # Commande SQL pour ajouter la PK
                    query = text(f"ALTER TABLE {table} ADD PRIMARY KEY ({pk_str});")
                    conn.execute(query)
                    conn.commit()
                    print(f"   🔑 PK ajoutée sur {table} ({pk_str})")
                except Exception as e:
                    print(f"   ⚠️  Impossible d'ajouter PK sur {table} (déjà existante ou doublons ?)")
                    # print(e) # Décommenter pour voir l'erreur exacte

def add_foreign_keys(engine):
    """Ajoute les clés étrangères pour relier les tables (Star Schema)"""
    print("\n🔗 Création des relations (Foreign Keys)...")
    
    # Liste des relations : (Table Enfant, Colonne Enfant, Table Parent, Colonne Parent)
    fks = [
        ("orders", "customer_id", "customers", "customer_id"),
        ("order_items", "order_id", "orders", "order_id"),
        ("order_items", "product_id", "products", "product_id"),
        ("order_items", "seller_id", "sellers", "seller_id"),
        ("fact_orders", "customer_id", "customers", "customer_id"),
    ]

    with engine.connect() as conn:
        for table, col, ref_table, ref_col in fks:
            try:
                constraint_name = f"fk_{table}_{col}"
                query = text(f"ALTER TABLE {table} ADD CONSTRAINT {constraint_name} FOREIGN KEY ({col}) REFERENCES {ref_table} ({ref_col});")
                conn.execute(query)
                conn.commit()
                print(f"   🔗 FK ajoutée : {table}.{col} -> {ref_table}.{ref_col}")
            except Exception:
                print(f"   ⚠️  FK échouée : {table}.{col} (Données orphelines ou contrainte déjà là)")

def main():
    print("=" * 80)
    print("🚀 CHARGEMENT DES DONNÉES DANS POSTGRESQL")
    print("=" * 80)

    # 1. Connexion
    try:
        engine = get_engine()
        # Test de connexion simple
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Connexion à la base de données réussie.\n")
    except Exception as e:
        print("❌ Erreur de connexion. Vérifie que ton conteneur Docker tourne.")
        print(e)
        return

    # 2. Mapping Fichiers -> Tables
    # On définit l'ordre pour charger les dimensions avant les faits (bonne pratique)
    files_map = [
        ("01_customers.csv", "customers"),
        ("02_products.csv", "products"),
        ("03_geolocation.csv", "geolocation"),
        ("04_sellers.csv", "sellers"),
        ("05_orders.csv", "orders"),
        ("06_order_items.csv", "order_items"), # Fact Sales
        ("07_order_payments.csv", "order_payments"),
        ("08_order_reviews.csv", "order_reviews"),
        ("09_fact_orders.csv", "fact_orders")
    ]

    # 3. Boucle de chargement
    start_time = time.time()
    
    for filename, table_name in files_map:
        file_path = data_gold_path / filename
        if file_path.exists():
            load_csv_to_postgres(file_path, table_name, engine)
        else:
            print(f"   ⚠️  Fichier introuvable : {filename}")

    # 4. Ajout des contraintes
    add_primary_keys(engine)
    
    # 5. Ajout des relations
    add_foreign_keys(engine)

    duration = time.time() - start_time
    print("\n" + "=" * 80)
    print(f"🎉 TERMINÉ en {duration:.2f} secondes !")
    print("=" * 80)

if __name__ == "__main__":
    main()