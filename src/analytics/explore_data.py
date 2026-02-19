"""
Script pour explorer le dataset Brazilian E-commerce
"""
import pandas as pd
import os
from pathlib import Path

# Chemin vers les données brutes
data_raw_path = Path(__file__).parent.parent / "data" / "raw"

print("=" * 80)
print("EXPLORATION DU DATASET BRAZILIAN E-COMMERCE")
print("=" * 80)

# Lister tous les fichiers CSV
csv_files = sorted([f for f in os.listdir(data_raw_path) if f.endswith('.csv')])

print(f"\nNombre de fichiers CSV: {len(csv_files)}\n")

# Explorer chaque fichier
for csv_file in csv_files:
    file_path = os.path.join(data_raw_path, csv_file)
    df = pd.read_csv(file_path)
    
    print(f"\n{'─' * 80}")
    print(f"📊 {csv_file}")
    print(f"{'─' * 80}")
    print(f"  Dimensions: {df.shape[0]} lignes × {df.shape[1]} colonnes")
    print(f"  Colonnes: {', '.join(df.columns.tolist())}")
    print(f"\n  Aperçu des 3 premières lignes:")
    print(df.head(3).to_string())
    print()
