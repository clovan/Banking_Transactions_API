"""
Unit tests for customer routes (Routes 16-18).

Estructura:
- Route 16: GET /api/customers
- Route 17: GET /api/customers/{customer_id}
- Route 18: GET /api/customers/top
"""

import pytest
from fastapi.testclient import TestClient

# IMPORTANTE: Importamos 'app' desde tu estructura específica
# Asumiendo que en src/banking_transaction_api/main.py está definida tu instancia de FastAPI
from banking_transaction_api.main import app

@pytest.fixture
def client():
    """Fixture para inicializar el cliente de pruebas de FastAPI."""
    return TestClient(app)


class TestCustomersList:
    """Tests for Route 16: GET /api/customers"""

    def test_customers_list_returns_200(self, client: TestClient):
        response = client.get("/api/customers")
        assert response.status_code == 200

    def test_customers_list_contains_required_fields(self, client: TestClient):
        response = client.get("/api/customers")
        data = response.json()
        assert all(k in data for k in ["page", "limit", "total", "customers"])

    def test_customers_list_returns_list_of_customers(self, client: TestClient):
        response = client.get("/api/customers")
        data = response.json()
        assert isinstance(data["customers"], list)

    def test_customers_list_customer_has_id(self, client: TestClient):
        response = client.get("/api/customers")
        data = response.json()
        if not data["customers"]:
            pytest.skip("No customers available")
        for customer in data["customers"]:
            assert "id" in customer
            assert isinstance(customer["id"], str)

    def test_customers_list_id_format(self, client: TestClient):
        response = client.get("/api/customers")
        data = response.json()
        if not data["customers"]:
            pytest.skip("No customers available")
        for customer in data["customers"]:
            assert customer["id"].startswith("C")

    def test_customers_list_default_pagination(self, client: TestClient):
        response = client.get("/api/customers")
        data = response.json()
        assert data["page"] == 1
        assert data["limit"] == 10


class TestCustomerProfile:
    """Tests for Route 17: GET /api/customers/{customer_id}"""

    def test_customer_profile_returns_200(self, client: TestClient):
        list_response = client.get("/api/customers?limit=1")
        customers = list_response.json()["customers"]
        if not customers:
            pytest.skip("No customers available")

        customer_id = customers[0]["id"]
        response = client.get(f"/api/customers/{customer_id}")
        assert response.status_code == 200

    def test_customer_profile_contains_required_fields(self, client: TestClient):
        list_response = client.get("/api/customers?limit=1")
        customers = list_response.json()["customers"]
        if not customers:
            pytest.skip("No customers available")

        customer_id = customers[0]["id"]
        response = client.get(f"/api/customers/{customer_id}")
        data = response.json()
        assert all(k in data for k in ["id", "transactions_count", "avg_amount", "fraudulent"])

    def test_customer_profile_not_found_returns_404(self, client: TestClient):
        # Un ID que probablemente no exista
        response = client.get("/api/customers/C9999999999")
        assert response.status_code == 404

    def test_customer_profile_accepts_id_without_prefix(self, client: TestClient):
        list_response = client.get("/api/customers?limit=1")
        customers = list_response.json()["customers"]
        if not customers:
            pytest.skip("No customers available")

        customer_id = customers[0]["id"]
        numeric_id = customer_id[1:] # Quitamos la 'C'
        response = client.get(f"/api/customers/{numeric_id}")
        assert response.status_code == 200


class TestTopCustomers:
    """Tests for Route 18: GET /api/customers/top"""

    def test_top_customers_returns_200(self, client: TestClient):
        response = client.get("/api/customers/top")
        assert response.status_code == 200

    def test_top_customers_returns_list(self, client: TestClient):
        response = client.get("/api/customers/top")
        data = response.json()
        assert isinstance(data, list)

    def test_top_customers_items_have_required_fields(self, client: TestClient):
        response = client.get("/api/customers/top")
        data = response.json()
        if not data:
            pytest.skip("No top customers available")
        for item in data:
            assert "id" in item
            assert "total_volume" in item
            assert "transactions_count" in item

    def test_top_customers_sorted_by_volume(self, client: TestClient):
        response = client.get("/api/customers/top")
        data = response.json()
        if len(data) < 2:
            pytest.skip("Not enough customers to test sorting")
        
        volumes = [item["total_volume"] for item in data]
        assert volumes == sorted(volumes, reverse=True)