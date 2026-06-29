import pytest
from app.api.deps import FORBIDDEN_ERROR, AdminUser, CustomerUser
from app.main import app
from app.seed import ADMIN_EMAIL, ADMIN_PASSWORD, CUSTOMER_PASSWORD
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import sessionmaker

CUSTOMER_EMAIL = "alex.customer@demo.bank.test"


# Test-only probes exercise the dependency through FastAPI without adding premature product routes.
@app.get("/api/test-only/admin-role")
def admin_role_probe(user: AdminUser) -> dict[str, str]:
    return {"role": user.role.value}


@app.get("/api/test-only/customer-role")
def customer_role_probe(user: CustomerUser) -> dict[str, str]:
    return {"role": user.role.value}


@pytest.mark.parametrize(
    ("email", "password", "path", "expected_role"),
    [
        (ADMIN_EMAIL, ADMIN_PASSWORD, "/api/test-only/admin-role", "ADMIN"),
        (CUSTOMER_EMAIL, CUSTOMER_PASSWORD, "/api/test-only/customer-role", "CUSTOMER"),
    ],
    ids=["admin-allowed", "customer-allowed"],
)
def test_matching_sql_role_is_allowed(
    email: str,
    password: str,
    path: str,
    expected_role: str,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    client, _session_factory = login_test_context
    login_response = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200

    response = client.get(path, headers={"X-Role": "ADMIN"})

    assert response.status_code == 200
    assert response.json() == {"role": expected_role}


@pytest.mark.parametrize(
    ("email", "password", "path", "spoofed_role"),
    [
        (CUSTOMER_EMAIL, CUSTOMER_PASSWORD, "/api/test-only/admin-role", "ADMIN"),
        (ADMIN_EMAIL, ADMIN_PASSWORD, "/api/test-only/customer-role", "CUSTOMER"),
    ],
    ids=["customer-denied-admin", "admin-denied-customer"],
)
def test_mismatched_sql_role_is_forbidden_despite_client_role_input(
    email: str,
    password: str,
    path: str,
    spoofed_role: str,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    client, _session_factory = login_test_context
    login_response = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200

    response = client.get(path, headers={"X-Role": spoofed_role})

    assert response.status_code == 403
    assert response.json() == FORBIDDEN_ERROR
