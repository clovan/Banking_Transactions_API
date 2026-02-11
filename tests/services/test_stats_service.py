import pytest
import pandas as pd
from banking_transaction_api.services.stats_service import StatsService


# =================================================================
# FIXTURE : Simulation des données pour les stats
# =================================================================

class MockTransactionService:
    """Simule le TransactionService pour ne pas dépendre du CSV."""

    def get_all(self):
        return pd.DataFrame([
            {"id": 1, "use_chip": "Chip", "amount":
                - 100.0, "isFraud": 0, "date": "2025-01-01"},
            {"id": 2, "use_chip": "Online", "amount": 200.0,
                "isFraud": 1, "date": "2025-01-01"},
            {"id": 3, "use_chip": "Chip", "amount":
                - 300.0, "isFraud": 0, "date": "2025-01-02"},
            {"id": 4, "use_chip": "Online", "amount": 400.0,
                "isFraud": 0, "date": "2025-01-02"}
        ])


@pytest.fixture
def stats_service():
    # On injecte le faux service de transaction
    mock_tx = MockTransactionService()
    return StatsService(mock_tx)


# =================================================================
# TESTS DES LOGIQUES DE CALCUL
# =================================================================

def test_global_stats_calculation(stats_service):
    """Vérifie les calculs globaux (Moyenne, Fraude, Total)."""
    stats = stats_service.get_global_stats()

    assert stats["total_transactions"] == 4
    # Moyenne des montants (valeurs absolues) : (100+200+300+400)/4 = 250
    assert stats["avg_amount"] == 250.0
    # Taux de fraude : 1 fraude sur 4 = 0.25
    assert stats["fraud_rate"] == 0.25
    # Type le plus fréquent : Chip et Online sont à égalité (mode renvoie le 1er)
    assert stats["most_common_type"] in ["Chip", "Online"]


def test_amount_distribution_logic(stats_service):
    """Vérifie que la répartition par paliers (bins) est correcte."""
    # On définit des paliers personnalisés pour le test
    custom_bins = [0, 150, 500]
    dist = stats_service.get_amount_distribution(custom_bins=custom_bins)

    # Montants abs : 100, 200, 300, 400
    # 0-150 : contient 100 -> count = 1
    # 150-500 : contient 200, 300, 400 -> count = 3
    assert dist["counts"] == [1, 3]
    assert dist["bins"] == ["0-150", "150-500"]


def test_stats_by_type_logic(stats_service):
    """Vérifie le groupement par type de transaction."""
    results = stats_service.get_stats_by_type()

    # On cherche les stats pour le type "Chip"
    chip_stats = next(item for item in results if item["type"] == "Chip")
    assert chip_stats["count"] == 2
    # Moyenne Chip abs : (100 + 300) / 2 = 200
    assert chip_stats["avg_amount"] == 200.0


def test_daily_stats_grouping(stats_service):
    """Vérifie que les transactions sont bien groupées par jour."""
    daily = stats_service.get_daily_stats()

    # Il y a deux dates différentes dans notre mock
    assert len(daily) == 2
    # Pour le 2025-01-01, on doit avoir 2 transactions
    assert daily[0]["count"] == 2
