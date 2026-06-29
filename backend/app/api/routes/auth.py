from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session as DatabaseSession

from app.core.config import get_settings
from app.core.security import generate_csrf_token, get_session_cookie_name
from app.db.session import get_db
from app.schemas.auth import LoginRequest, LoginResponse
from app.services.auth_service import LoginFailedError, login

router = APIRouter(prefix="/auth", tags=["authentication"])

# Every credential-related failure uses the same shape and wording to prevent account discovery.
GENERIC_LOGIN_ERROR = {
    "error": {
        "code": "UNAUTHENTICATED",
        "message": "Invalid email or password",
        "fields": {},
    }
}


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Invalid credentials"}},
)
def login_route(
    credentials: LoginRequest,
    request: Request,
    response: Response,
    db: Annotated[DatabaseSession, Depends(get_db)],
) -> LoginResponse | JSONResponse:
    """Authenticate a user and issue the cookie pair used by later auth dependencies."""

    # The route translates HTTP context; credential rules and transaction ownership stay in service.
    try:
        result = login(
            db,
            email=credentials.email,
            password=credentials.password,
            user_agent=request.headers.get("user-agent"),
            ip=request.client.host if request.client is not None else None,
        )
    except LoginFailedError:
        # Phase 17 will centralize this already-correct public envelope.
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=GENERIC_LOGIN_ERROR,
        )

    settings = get_settings()

    # Cookie lifetime cannot exceed the absolute server-side session lifetime selected in D1.
    max_age = settings.session_absolute_hours * 60 * 60
    cookie_domain = settings.cookie_domain

    # The raw session token exists only in the HttpOnly cookie; SQL stores its HMAC lookup hash.
    response.set_cookie(
        key=get_session_cookie_name(cookie_domain),
        value=result.raw_session_token,
        max_age=max_age,
        expires=result.expires_at,
        path="/",
        domain=cookie_domain,
        secure=True,
        httponly=True,
        samesite="strict",
    )

    # JavaScript may read this independent value later and echo it in X-CSRF-Token.
    response.set_cookie(
        key=settings.csrf_cookie_name,
        value=generate_csrf_token(),
        max_age=max_age,
        expires=result.expires_at,
        path="/",
        domain=cookie_domain,
        secure=True,
        httponly=False,
        samesite="strict",
    )
    return LoginResponse()
