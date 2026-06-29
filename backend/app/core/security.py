from argon2 import PasswordHasher, Type
from argon2.exceptions import InvalidHashError, VerificationError

# These explicit Argon2id settings meet the specification floor and remain stable across upgrades.
_password_hasher = PasswordHasher(
    time_cost=2,
    memory_cost=19 * 1024,
    parallelism=1,
    hash_len=32,
    salt_len=16,
    type=Type.ID,
)


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
