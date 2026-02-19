"""
Script pour télécharger le dataset Brazilian E-commerce de Kaggle
"""
import kagglehub
import os
from pathlib import Path

# Définir le chemin de destination
data_raw_path = Path(__file__).parent.parent / "data" / "raw"
data_raw_path.mkdir(parents=True, exist_ok=True)

print(f"Téléchargement du dataset dans: {data_raw_path}")

# Télécharger le dataset complet
dataset_path = kagglehub.dataset_download("olistbr/brazilian-ecommerce")

print(f"Dataset téléchargé de: {dataset_path}")

# Copier tous les fichiers CSV vers le dossier data/raw
import shutil
for file in os.listdir(dataset_path):
    if file.endswith('.csv'):
        src = os.path.join(dataset_path, file)
        dst = os.path.join(data_raw_path, file)
        shutil.copy(src, dst)
        print(f"✓ Copié: {file}")

print(f"\n✓ Tous les fichiers CSV sont dans: {data_raw_path}")

# Afficher la liste des fichiers disponibles
print("\nFichiers CSV disponibles:")
for file in sorted(os.listdir(data_raw_path)):
    if file.endswith('.csv'):
        file_path = os.path.join(data_raw_path, file)
        size = os.path.getsize(file_path) / (1024 * 1024)  # En MB
        print(f"  - {file} ({size:.2f} MB)")
