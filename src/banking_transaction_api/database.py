import csv
from pathlib import Path
from src.banking_transaction_api.models import Transaction

# Chemin dynamique vers le fichier CSV
BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "data" / "transactions.csv"

def get_all_transactions():
    transactions = []
    with open(CSV_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # On convertit chaque ligne du CSV en objet Transaction
            transactions.append(Transaction(**row))
    return transactions