import logging
import sys

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes.accounts import router as accounts_router
from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.money import router as money_router
from app.api.routes.transactions import router as transactions_router
from app.api.routes.transfers import router as transfers_router
from app.errors import (
    DomainError,
    catch_unexpected_exceptions,
    domain_exception_handler,
    http_exception_handler,
    request_validation_exception_handler,
)

# Emit intentionally sanitized application audit logs even when Uvicorn filters the root logger.
app_logger = logging.getLogger("app")
app_logger.setLevel(logging.INFO)
if not app_logger.handlers:
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(logging.Formatter("%(levelname)s [%(name)s] %(message)s"))
    app_logger.addHandler(stdout_handler)

# Create the central ASGI application that Uvicorn will serve.
app = FastAPI(title="Simulated Banking API")

# Expected failures, framework validation, routing failures, and unexpected exceptions all share
# the same public envelope while retaining distinct status codes and machine-readable codes.
app.add_exception_handler(DomainError, domain_exception_handler)
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)

# Catch unexpected failures before Starlette's outer server layer can re-log raw exception text.
app.middleware("http")(catch_unexpected_exceptions)

# Keep every backend endpoint under /api so the frontend and API can share one origin.
app.include_router(health_router, prefix="/api")

# Authentication joins the same public namespace while retaining its own focused router module.
app.include_router(auth_router, prefix="/api")

# Customer account reads reuse the shared role and ownership dependencies.
app.include_router(accounts_router, prefix="/api")

# Transaction history shares the same customer and account ownership boundaries.
app.include_router(transactions_router, prefix="/api")

# Money mutations add explicit CSRF and locked service-layer transaction boundaries.
app.include_router(money_router, prefix="/api")

# Transfers lock two owned accounts and persist both ledger legs atomically.
app.include_router(transfers_router, prefix="/api")

# Admin routes use SQL-backed role checks and never reuse customer ownership dependencies.
app.include_router(admin_router, prefix="/api")
