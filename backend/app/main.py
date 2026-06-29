from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.errors import (
    DomainError,
    catch_unexpected_exceptions,
    domain_exception_handler,
    http_exception_handler,
    request_validation_exception_handler,
)

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
