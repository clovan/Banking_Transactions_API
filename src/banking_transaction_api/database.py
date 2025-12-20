import csv
from pathlib import Path
from src.banking_transaction_api.models import Transaction

# 1. On définit le chemin de manière ultra-précise
# On part de l'endroit où se trouve ce fichier (database.py)
BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "data" / "transactions.csv"


def get_all_transactions():
    transactions = []

    print(f"DEBUG: Recherche du fichier ici -> {CSV_FILE.absolute()}")  # Ajoute cette ligne
    transactions = []

    # 2. Sécurité : On vérifie si le fichier existe avant de tenter de l'ouvrir
    if not CSV_FILE.exists():
        print(f"Erreur : Le fichier {CSV_FILE} est introuvable.")
        return []

    with open(CSV_FILE, mode="r", encoding="utf-8") as file:
        # DictReader utilise la première ligne du CSV comme clés (id, sender, amount, etc.)
        reader = csv.DictReader(file)

        for row in reader:
            try:
                # 3. On crée l'objet Transaction
                # Pydantic va automatiquement essayer de convertir :
                # "1" (texte) -> 1 (int)
                # "150.50" (texte) -> 150.50 (float)
                transaction_obj = Transaction(**row)
                transactions.append(transaction_obj)
            except Exception as e:
                print(f"Erreur de conversion sur une ligne : {e}")
                continue

    return transactions