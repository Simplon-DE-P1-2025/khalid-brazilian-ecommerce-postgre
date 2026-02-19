"""
Script pour charger les données des fichiers CSV du dossier data/raw
"""
import pandas as pd
from pathlib import Path
import os

# Chemin vers les données brutes
data_raw_path = Path(__file__).parent.parent / "data" / "raw"

print("=" * 80)
print("CHARGEMENT DES DONNÉES CSV")
print("=" * 80)

# Dictionnaire pour stocker tous les DataFrames
dataframes = {}

# Charger tous les fichiers CSV
csv_files = sorted([f for f in os.listdir(data_raw_path) if f.endswith('.csv')])

if not csv_files:
    print("\n⚠️  Aucun fichier CSV trouvé dans data/raw/")
    print("Veuillez d'abord exécuter: python src/download_data.py")
else:
    for csv_file in csv_files:
        file_path = os.path.join(data_raw_path, csv_file)
        file_name = csv_file.replace('.csv', '')
        
        try:
            df = pd.read_csv(file_path)
            dataframes[file_name] = df
            print(f"✓ {csv_file}: {df.shape[0]} lignes, {df.shape[1]} colonnes")
        except Exception as e:
            print(f"✗ Erreur lors du chargement de {csv_file}: {str(e)}")
    
    # Afficher un résumé
    print(f"\n{'─' * 80}")
    print(f"Fichiers chargés: {len(dataframes)}")
    print(f"{'─' * 80}\n")
    
    # Afficher les 5 premières lignes de chaque dataset
    for name, df in dataframes.items():
        print(f"\n📊 {name}")
        print(f"Colonnes: {', '.join(df.columns.tolist())}")
        print(f"Premier aperçu:")
        print(df.head())
