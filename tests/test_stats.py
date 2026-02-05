from fastapi.testclient import TestClient
from banking_transaction_api.main import app

client = TestClient(app)

# =================================================================
# TEST ROUTE 9 : STATISTIQUES GLOBALES
# =================================================================
def test_route_9_stats_overview():
    """Vérifie les stats globales (Total, Fraude, Moyenne, Type)."""
    response = client.get("/api/stats/overview")
    assert response.status_code == 200
    stats = response.json()

    # Vérification présence et types
    assert "total_transactions" in stats
    assert "fraud_rate" in stats
    assert "avg_amount" in stats
    assert "most_common_type" in stats

    assert isinstance(stats["total_transactions"], int)
    assert isinstance(stats["avg_amount"], (int, float))

    # L'assertion >= 0 valide indirectement l'usage de .abs()
    assert 0 <= stats["fraud_rate"] <= 1
    assert stats["avg_amount"] >= 0


# =================================================================
# TESTS ROUTE 10 : DISTRIBUTION VARIABLE
# =================================================================

def test_route_10_distribution_default():
    """Vérifie l'histogramme par défaut si aucun bin n'est fourni."""
    response = client.get("/api/stats/amount-distribution")
    assert response.status_code == 200
    data = response.json()

    # Vérification des 4 intervalles par défaut
    assert len(data["bins"]) == 4
    assert data["bins"][0] == "0-100"


def test_route_10_distribution_variable():
    """Vérifie que l'API génère les bons intervalles selon les saisies Swagger."""
    params = {"bins": [20, 100, 150]}
    response = client.get("/api/stats/amount-distribution", params=params)

    assert response.status_code == 200
    data = response.json()

    # Vérification de la transformation dynamique
    assert len(data["bins"]) == 2
    assert data["bins"][0] == "20-100"
    assert data["bins"][1] == "100-150"

    assert isinstance(data["counts"][0], int)


def test_route_10_empty_on_invalid_bins():
    """Vérifie le comportement si les paliers sont incohérents."""
    response = client.get("/api/stats/amount-distribution?bins=50")
    assert response.status_code in [200, 404]


# =================================================================
# TEST ROUTE 11 : STATISTIQUES PAR TYPE (ALIGNÉ SUR LE JSON PROF)
# =================================================================

def test_route_11_stats_by_type():
    """Vérifie la conformité avec l'exemple JSON : count et avg_amount."""
    response = client.get("/api/stats/by-type")
    assert response.status_code == 200
    data = response.json()

    # La réponse doit être une liste d'objets
    assert isinstance(data, list)

    if len(data) > 0:
        item = data[0]
        # On teste les clés exactes de l'image du prof
        assert "type" in item
        assert "count" in item
        assert "avg_amount" in item

        # Vérification des types de données conformes
        assert isinstance(item["type"], str)
        assert isinstance(item["count"], int)
        assert isinstance(item["avg_amount"], (int, float))

        # Vérification de la cohérence (toujours positif grâce à .abs())
        assert item["count"] >= 0
        assert item["avg_amount"] >= 0