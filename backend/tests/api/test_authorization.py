from app.api.deps import AdminUser, CustomerUser
from app.errors import FORBIDDEN_ERROR
from app.main import app
from fastapi.testclient import TestClient


# Test-only probes exercise the dependency through FastAPI without adding premature product routes.
@app.get("/api/test-only/admin-role")
def admin_role_probe(user: AdminUser) -> dict[str, str]:
    return {"role": user.role.value}


@app.get("/api/test-only/customer-role")
def customer_role_probe(user: CustomerUser) -> dict[str, str]:
    return {"role": user.role.value}


def test_admin_sql_role_is_allowed(admin_client: TestClient) -> None:
    response = admin_client.get("/api/test-only/admin-role", headers={"X-Role": "CUSTOMER"})
    assert response.status_code == 200
    assert response.json() == {"role": "ADMIN"}


def test_customer_sql_role_is_allowed(customer_client: TestClient) -> None:
    response = customer_client.get("/api/test-only/customer-role", headers={"X-Role": "ADMIN"})
    assert response.status_code == 200
    assert response.json() == {"role": "CUSTOMER"}


def test_customer_is_forbidden_from_admin_guard(customer_client: TestClient) -> None:
    response = customer_client.get("/api/test-only/admin-role", headers={"X-Role": "ADMIN"})
    assert response.status_code == 403
    assert response.json() == FORBIDDEN_ERROR


def test_admin_is_forbidden_from_customer_guard(admin_client: TestClient) -> None:
    response = admin_client.get("/api/test-only/customer-role", headers={"X-Role": "CUSTOMER"})
    assert response.status_code == 403
    assert response.json() == FORBIDDEN_ERROR
