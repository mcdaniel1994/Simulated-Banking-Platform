import logging

import pytest
from app.errors import (
    INTERNAL_ERROR,
    NOT_FOUND_ERROR,
    CsrfInvalidError,
    DomainError,
    ForbiddenError,
    InactiveAccountError,
    InactiveUserError,
    InsufficientFundsError,
    InternalError,
    NotFoundError,
    SameAccountTransferError,
    UnauthenticatedError,
    ValidationError,
)
from app.main import app
from fastapi.testclient import TestClient

DOMAIN_ERRORS: dict[str, type[DomainError]] = {
    "validation": ValidationError,
    "unauthenticated": UnauthenticatedError,
    "forbidden": ForbiddenError,
    "not-found": NotFoundError,
    "csrf-invalid": CsrfInvalidError,
    "insufficient-funds": InsufficientFundsError,
    "inactive-account": InactiveAccountError,
    "same-account-transfer": SameAccountTransferError,
    "inactive-user": InactiveUserError,
    "internal": InternalError,
}


@app.get("/api/test-only/errors/{error_name}")
def domain_error_probe(error_name: str) -> None:
    raise DOMAIN_ERRORS[error_name]()


@app.get("/api/test-only/unexpected-error")
def unexpected_error_probe() -> None:
    raise RuntimeError("SELECT password_hash FROM users; secret-token-value")


@pytest.mark.parametrize(
    ("error_name", "expected_code", "expected_status"),
    [
        ("validation", "VALIDATION_ERROR", 422),
        ("unauthenticated", "UNAUTHENTICATED", 401),
        ("forbidden", "FORBIDDEN", 403),
        ("not-found", "NOT_FOUND", 404),
        ("csrf-invalid", "CSRF_INVALID", 403),
        ("insufficient-funds", "INSUFFICIENT_FUNDS", 409),
        ("inactive-account", "INACTIVE_ACCOUNT", 409),
        ("same-account-transfer", "SAME_ACCOUNT_TRANSFER", 400),
        ("inactive-user", "INACTIVE_USER", 403),
        ("internal", "INTERNAL_ERROR", 500),
    ],
)
def test_each_domain_error_uses_common_envelope(
    error_name: str,
    expected_code: str,
    expected_status: int,
) -> None:
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get(f"/api/test-only/errors/{error_name}")

    assert response.status_code == expected_status
    assert response.json()["error"]["code"] == expected_code
    assert set(response.json()["error"]) == {"code", "message", "fields"}


def test_request_validation_error_omits_rejected_password() -> None:
    rejected_password = "should-never-be-echoed"
    with TestClient(app) as client:
        response = client.post(
            "/api/auth/login",
            json={"email": "not-an-email", "password": rejected_password},
        )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert response.json()["error"]["fields"] == {"email": "Invalid value"}
    assert rejected_password not in response.text


def test_unknown_route_uses_not_found_envelope() -> None:
    with TestClient(app) as client:
        response = client.get("/api/route-that-does-not-exist")

    assert response.status_code == 404
    assert response.json() == NOT_FOUND_ERROR


def test_unexpected_error_never_leaks_response_or_log_details(
    caplog: pytest.LogCaptureFixture,
) -> None:
    secret_fragments = ("SELECT password_hash", "secret-token-value")
    with (
        caplog.at_level(logging.ERROR, logger="app.errors"),
        TestClient(app) as client,
    ):
        response = client.get("/api/test-only/unexpected-error")

    assert response.status_code == 500
    assert response.json() == INTERNAL_ERROR
    for fragment in secret_fragments:
        assert fragment not in response.text
        assert fragment not in caplog.text
    assert "RuntimeError" in caplog.text
