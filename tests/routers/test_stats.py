
from fastapi.testclient import TestClient
from banking_transaction_api.main import app

client = TestClient(app)


# =================================================================
# TEST ROUTE 9 : STATISTIQUES GLOBALES
# =================================================================
def test_route_9_stats_overview():
    """Vérifie les indicateurs globaux (Total, Fraude, Moyenne)."""
    response = client.get("/api/stats/overview")
    assert response.status_code == 200
    stats = response.json()

    # Vérification des clés obligatoires
    required_keys = ["total_transactions", "fraud_rate", "avg_amount", "most_common_type"]
    for key in required_keys:
        assert key in stats

    # Vérification de la cohérence des types
    assert isinstance(stats["total_transactions"], int)
    assert isinstance(stats["avg_amount"], (int, float))
    assert 0 <= stats["fraud_rate"] <= 1

    # Validation du nettoyage .abs() : le montant moyen ne peut pas être négatif
    assert stats["avg_amount"] >= 0


# =================================================================
# TESTS ROUTE 10 : DISTRIBUTION (BINS)
# =================================================================

def test_route_10_distribution_default():
    """Vérifie l'histogramme avec les paliers par défaut."""
    response = client.get("/api/stats/amount-distribution")
    assert response.status_code == 200
    data = response.json()

    # Par défaut on attend 4 intervalles : 0-100, 100-500, 500-1000, 1000-5000
    assert "bins" in data
    assert "counts" in data
    assert len(data["bins"]) == 4
    assert data["bins"][0] == "0-100"


def test_route_10_distribution_custom_bins():
    """Vérifie la génération dynamique d'intervalles via query params."""
    # On définit 3 points, ce qui doit créer 2 intervalles
    params = {"bins": [0, 50, 200]}
    response = client.get("/api/stats/amount-distribution", params=params)

    assert response.status_code == 200
    data = response.json()
    assert len(data["bins"]) == 2
    assert data["bins"][0] == "0-50"
    assert data["bins"][1] == "50-200"


# =================================================================
# TEST ROUTE 11 : STATS PAR TYPE
# =================================================================

def test_route_11_stats_by_type():
    """Vérifie l'agrégation par type (conformité JSON)."""
    response = client.get("/api/stats/by-type")
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    if len(data) > 0:
        item = data[0]
        # Vérification des champs attendus
        assert "type" in item
        assert "count" in item
        assert "avg_amount" in item
        assert item["count"] > 0
        assert item["avg_amount"] >= 0


# =================================================================
# TEST ROUTE 12 : ANALYSE TEMPORELLE (JOURNALIÈRE)
# =================================================================

def test_route_12_daily_stats():
    """Vérifie le comptage des transactions par jour."""
    response = client.get("/api/stats/daily")

    # Si le dataset a des dates valides, on attend 200
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "date" in data[0]
            assert "count" in data[0]
            assert isinstance(data[0]["count"], int)
    else:
        # Si pas de colonnes dates détectées, le service renvoie 404
        assert response.status_code == 404