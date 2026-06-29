import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

from argon2 import PasswordHasher, Type
from argon2.exceptions import InvalidHashError, VerificationError

from app.core.config import get_settings

# These explicit Argon2id settings meet the specification floor and remain stable across upgrades.
_password_hasher = PasswordHasher(
    time_cost=2,
    memory_cost=19 * 1024,
    parallelism=1,
    hash_len=32,
    salt_len=16,
    type=Type.ID,
)

# Thirty-two random bytes provide 256 bits of entropy before URL-safe encoding.
SESSION_TOKEN_BYTES = 32
# The CSRF value is independent so exposing it to JavaScript never reveals the auth credential.
CSRF_TOKEN_BYTES = 32

# Domain-scoped cookies cannot use the stricter __Host- prefix defined by browser standards.
HOST_SESSION_COOKIE_NAME = "__Host-session"
DOMAIN_SESSION_COOKIE_NAME = "session"


def hash_password(plain_password: str) -> str:
    """Create a salted Argon2id hash suitable for persistent credential storage."""

    # Argon2 generates a fresh random salt internally, so equal passwords do not share a hash.
    return _password_hasher.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Return whether a password matches without exposing malformed-hash details to callers."""

    try:
        # argon2-cffi performs the password comparison inside its verified implementation.
        return _password_hasher.verify(password_hash, plain_password)
    except (VerificationError, InvalidHashError):
        # Wrong passwords and invalid stored hashes are both authentication failures.
        return False


def needs_rehash(password_hash: str) -> bool:
    """Report whether a valid stored hash should be upgraded to the current parameters."""

    return _password_hasher.check_needs_rehash(password_hash)


def generate_session_token() -> str:
    """Create a high-entropy opaque value safe for transport in an authentication cookie."""

    # Only the future HTTP layer receives this raw value; persistence receives hash_session_token().
    return secrets.token_urlsafe(SESSION_TOKEN_BYTES)


def generate_csrf_token() -> str:
    """Create the readable random value used by the future double-submit CSRF check."""

    # This token may be read by the SPA, so it must never be reused as the authentication token.
    return secrets.token_urlsafe(CSRF_TOKEN_BYTES)


def get_session_cookie_name(cookie_domain: str | None) -> str:
    """Use the hardened __Host- prefix only when no Domain attribute will be set."""

    return HOST_SESSION_COOKIE_NAME if cookie_domain is None else DOMAIN_SESSION_COOKIE_NAME


def hash_session_token(token: str) -> str:
    """Create the deterministic keyed lookup value stored in the sessions table."""

    # HMAC uses SESSION_SECRET as a pepper, so a database leak alone cannot reproduce token hashes.
    secret = get_settings().session_secret.get_secret_value().encode("utf-8")
    return hmac.new(secret, token.encode("utf-8"), hashlib.sha256).hexdigest()


def calculate_session_expiry(created_at: datetime) -> datetime:
    """Calculate D1's absolute expiry from an unambiguous timezone-aware creation time."""

    if created_at.utcoffset() is None:
        raise ValueError("created_at must be timezone-aware")

    absolute_hours = get_settings().session_absolute_hours
    return created_at.astimezone(UTC) + timedelta(hours=absolute_hours)
