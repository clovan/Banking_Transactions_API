import pytest
from fastapi.testclient import TestClient
from banking_transaction_api.main import app

client = TestClient(app)

# ============================================================
# 9. GET /api/stats/overview
# ============================================================

def test_stats_overview_structure():
    response = client.get("/api/stats/overview")
    assert response.status_code == 200

    data = response.json()

    # Vérification des clés
    assert "total_transactions" in data
    assert "fraud_rate" in data
    assert "avg_amount" in data
    assert "most_common_type" in data

    # Vérification des types
    assert isinstance(data["total_transactions"], int)
    assert isinstance(data["fraud_rate"], (float, type(None)))
    assert isinstance(data["avg_amount"], (float, type(None)))
    assert isinstance(data["most_common_type"], str)


# ============================================================
# 10. GET /api/stats/amount-distribution
# ============================================================
from fastapi import APIRouter
import numpy as np

router = APIRouter()

# Exemple : tu récupères tes montants depuis ta base ou ton dataset
# Ici je simule un dataset pour l'exemple
from banking_transaction_api.data_loader import load_dataset
import numpy as np

def load_transaction_amounts(nrows: int = 5000):
    # Charge ton dataset principal
    df = load_dataset("transactions.csv", nrows=nrows)

    # Vérifie que la colonne existe
    if "amount" not in df.columns:
        # Tu peux adapter le nom ici si ta colonne s'appelle différemment
        return []

    # Convertit en liste de valeurs numériques
    return df["amount"].astype(float).tolist()


@router.get("/api/stats/amount-distribution")
def amount_distribution():
    amounts = load_transaction_amounts()

    # Définition des classes (bins)
    bin_edges = [0, 100, 500, 1000, 5000]

    # Comptage par classe
    counts, _ = np.histogram(amounts, bins=bin_edges)

    # Formatage des bins en chaînes de caractères
    bins = [
        f"{bin_edges[i]}-{bin_edges[i+1]}"
        for i in range(len(bin_edges) - 1)
    ]

    return {
        "bins": bins,
        "counts": counts.tolist()
    }

"""def test_amount_distribution_structure():
    response = client.get("/api/stats/amount-distribution")
    assert response.status_code == 200

    data = response.json()

    assert "bins" in data
    assert "counts" in data

    assert isinstance(data["bins"], list)
    assert isinstance(data["counts"], list)

    # Les deux listes doivent avoir la même longueur
    assert len(data["bins"]) == len(data["counts"])

    # Vérification des types internes
    for b in data["bins"]:
        assert isinstance(b, str)

    for c in data["counts"]:
        assert isinstance(c, int)
"""

# ============================================================
# 11. GET /api/stats/by-type
# ============================================================

def test_stats_by_type_structure():
    response = client.get("/api/stats/by-type")
    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0, "Aucun type trouvé, dataset vide ?"

    for item in data:
        assert "type" in item
        assert "count" in item
        assert "avg_amount" in item

        assert isinstance(item["type"], str)
        assert isinstance(item["count"], int)
        assert isinstance(item["avg_amount"], float)


# ============================================================
# 12. GET /api/stats/daily
# ============================================================

def test_stats_daily_structure():
    response = client.get("/api/stats/daily")
    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    if len(data) > 0:
        item = data[0]

        assert "date" in item
        assert "count" in item
        assert "avg_amount" in item

        assert isinstance(item["date"], str)
        assert isinstance(item["count"], int)
        assert isinstance(item["avg_amount"], float)
