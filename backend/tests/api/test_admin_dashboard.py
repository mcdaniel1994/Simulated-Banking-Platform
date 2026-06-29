from app.errors import FORBIDDEN_ERROR
from app.main import app
from fastapi.testclient import TestClient


def test_admin_dashboard_returns_expected_aggregates_and_string_money(
    admin_client: TestClient,
) -> None:
    response = admin_client.get("/api/admin/dashboard")

    assert response.status_code == 200
    assert response.json() == {
        "customer_count": 2,
        "account_count": 4,
        "total_simulated_balance": "10995.00",
        "recent_transaction_count": 0,
        "recent_window_days": 30,
    }


def test_customer_cannot_access_admin_dashboard(customer_client: TestClient) -> None:
    response = customer_client.get("/api/admin/dashboard")

    assert response.status_code == 403
    assert response.json() == FORBIDDEN_ERROR


def test_admin_dashboard_money_is_string_in_openapi() -> None:
    schema = app.openapi()["components"]["schemas"]["AdminDashboardResponse"]

    assert schema["properties"]["total_simulated_balance"]["type"] == "string"
