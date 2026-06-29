from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session as DatabaseSession

from app.api.deps import CsrfProtected, CurrentPrincipal, CurrentUser
from app.core.config import get_settings
from app.core.security import generate_csrf_token, get_session_cookie_name
from app.db.session import get_db
from app.schemas.auth import CurrentUserResponse, LoginRequest, LoginResponse
from app.services.auth_service import login, logout

router = APIRouter(prefix="/auth", tags=["authentication"])


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
) -> LoginResponse:
    """Authenticate a user and issue the cookie pair used by later auth dependencies."""

    # The route translates HTTP context; credential rules and transaction ownership stay in service.
    result = login(
        db,
        email=credentials.email,
        password=credentials.password,
        user_agent=request.headers.get("user-agent"),
        ip=request.client.host if request.client is not None else None,
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


@router.get("/me", response_model=CurrentUserResponse)
def current_user_route(user: CurrentUser) -> CurrentUserResponse:
    """Return the user resolved from the validated server-side session."""

    # Response validation selects only explicitly safe fields from the ORM model.
    return CurrentUserResponse.model_validate(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_route(
    response: Response,
    _csrf: CsrfProtected,
    principal: CurrentPrincipal,
    db: Annotated[DatabaseSession, Depends(get_db)],
) -> None:
    """Revoke the current server-side session and clear both browser cookies."""

    # The validated principal supplies the exact session row; no raw-cookie lookup is repeated.
    logout(db, user=principal.user, session=principal.session)

    settings = get_settings()
    cookie_domain = settings.cookie_domain

    # Match issuance attributes so browsers remove the correct HttpOnly authentication cookie.
    response.delete_cookie(
        key=get_session_cookie_name(cookie_domain),
        path="/",
        domain=cookie_domain,
        secure=True,
        httponly=True,
        samesite="strict",
    )

    # The readable CSRF cookie is independent but must end with the revoked authenticated session.
    response.delete_cookie(
        key=settings.csrf_cookie_name,
        path="/",
        domain=cookie_domain,
        secure=True,
        httponly=False,
        samesite="strict",
    )
