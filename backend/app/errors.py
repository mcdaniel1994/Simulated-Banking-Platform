import logging
from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

logger = logging.getLogger(__name__)


class DomainError(Exception):
    """Carry the complete public API error contract without exposing internal state."""

    code = "INTERNAL_ERROR"
    default_message = "An unexpected error occurred"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        message: str | None = None,
        fields: dict[str, str] | None = None,
        *,
        code: str | None = None,
        status_code: int | None = None,
    ) -> None:
        self.code = code or self.code
        self.message = message or self.default_message
        self.fields = fields or {}
        self.status_code = status_code or self.status_code
        super().__init__(self.message)


# Concrete types keep service code expressive while centralizing status and public wording.
class ValidationError(DomainError):
    code = "VALIDATION_ERROR"
    default_message = "Request validation failed"
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT


class UnauthenticatedError(DomainError):
    code = "UNAUTHENTICATED"
    default_message = "Authentication required"
    status_code = status.HTTP_401_UNAUTHORIZED


class ForbiddenError(DomainError):
    code = "FORBIDDEN"
    default_message = "Insufficient permissions"
    status_code = status.HTTP_403_FORBIDDEN


class NotFoundError(DomainError):
    code = "NOT_FOUND"
    default_message = "Resource not found"
    status_code = status.HTTP_404_NOT_FOUND


class CsrfInvalidError(DomainError):
    code = "CSRF_INVALID"
    default_message = "Invalid CSRF token"
    status_code = status.HTTP_403_FORBIDDEN


class InsufficientFundsError(DomainError):
    code = "INSUFFICIENT_FUNDS"
    default_message = "Insufficient funds"
    status_code = status.HTTP_409_CONFLICT


class InactiveAccountError(DomainError):
    code = "INACTIVE_ACCOUNT"
    default_message = "Account is not active"
    status_code = status.HTTP_409_CONFLICT


class SameAccountTransferError(DomainError):
    code = "SAME_ACCOUNT_TRANSFER"
    default_message = "Source and destination accounts must differ"
    status_code = status.HTTP_400_BAD_REQUEST


class InactiveUserError(DomainError):
    code = "INACTIVE_USER"
    default_message = "User is not active"
    status_code = status.HTTP_403_FORBIDDEN


class EmailAlreadyExistsError(DomainError):
    code = "EMAIL_ALREADY_EXISTS"
    default_message = "A customer with this email already exists"
    status_code = status.HTTP_409_CONFLICT

    def __init__(self) -> None:
        # The field-level message lets the administrator correct the form without exposing SQL.
        super().__init__(fields={"email": "A customer with this email already exists."})


class InternalError(DomainError):
    """Represent an intentionally generic server failure."""

    def __init__(self) -> None:
        # Internal failures must never accept an exception message that could reach the client.
        super().__init__()


def error_envelope(error: DomainError) -> dict[str, dict[str, Any]]:
    """Build the one public error shape consumed by every API client."""

    # Serialize only public attributes—never an exception representation or traceback.
    return {
        "error": {
            "code": error.code,
            "message": error.message,
            "fields": error.fields,
        }
    }


# Stable constants keep focused contract assertions concise without duplicating response shapes.
UNAUTHENTICATED_ERROR = error_envelope(UnauthenticatedError())
CSRF_INVALID_ERROR = error_envelope(CsrfInvalidError())
FORBIDDEN_ERROR = error_envelope(ForbiddenError())
NOT_FOUND_ERROR = error_envelope(NotFoundError())
INTERNAL_ERROR = error_envelope(InternalError())


async def domain_exception_handler(
    _request: Request,
    error: DomainError,
) -> JSONResponse:
    """Render every expected domain failure through the common envelope."""

    return JSONResponse(
        status_code=error.status_code,
        content=error_envelope(error),
    )


async def request_validation_exception_handler(
    _request: Request,
    error: RequestValidationError,
) -> JSONResponse:
    """Describe invalid fields without echoing rejected passwords or other submitted values."""

    # Framework details contain rejected input, so copy only location and a generic reason.
    fields: dict[str, str] = {}
    for detail in error.errors():
        location = ".".join(str(part) for part in detail["loc"] if part not in {"body", "query"})
        reason = "Field required" if detail["type"] == "missing" else "Invalid value"
        fields[location or "request"] = reason

    validation_error = ValidationError(fields=fields)
    return await domain_exception_handler(_request, validation_error)


async def http_exception_handler(
    request: Request,
    error: StarletteHTTPException,
) -> JSONResponse:
    """Normalize framework-generated routing and authorization failures."""

    # Translate Starlette defaults so clients never receive a second {"detail": ...} shape.
    if error.status_code == status.HTTP_404_NOT_FOUND:
        domain_error = NotFoundError()
    elif error.status_code == status.HTTP_401_UNAUTHORIZED:
        domain_error = UnauthenticatedError()
    elif error.status_code == status.HTTP_403_FORBIDDEN:
        domain_error = ForbiddenError()
    else:
        domain_error = DomainError(
            code="HTTP_ERROR",
            message="Request failed",
            status_code=error.status_code,
        )
    return await domain_exception_handler(request, domain_error)


async def unexpected_exception_handler(
    request: Request,
    error: Exception,
) -> JSONResponse:
    """Log only safe diagnostics and return no internal exception details."""

    # Exception messages and concrete URL values can contain secrets, so use the route template.
    route = request.scope.get("route")
    route_template = getattr(route, "path", "<unmatched>")
    logger.error(
        "Unhandled %s while processing %s %s",
        type(error).__name__,
        request.method,
        route_template,
    )
    internal_error = InternalError()
    return await domain_exception_handler(request, internal_error)


async def catch_unexpected_exceptions(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:
    """Convert unexpected failures before the outer server layer can log secret-bearing details."""

    # Catching here prevents Uvicorn from re-logging the original message and traceback.
    try:
        return await call_next(request)
    except Exception as error:
        return await unexpected_exception_handler(request, error)
