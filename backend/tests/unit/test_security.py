from datetime import UTC, datetime, timedelta

import pytest
from app.core.config import get_settings
from app.core.security import (
    SESSION_TOKEN_BYTES,
    calculate_session_expiry,
    generate_session_token,
    hash_password,
    hash_session_token,
    needs_rehash,
    verify_password,
)
from argon2 import PasswordHasher, Type, extract_parameters


@pytest.fixture
def configured_session_security(monkeypatch: pytest.MonkeyPatch) -> str:
    # Isolate keyed hashing and expiry tests from a developer's real local configuration.
    session_secret = "unit-test-session-pepper"
    get_settings.cache_clear()
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://unit:password@localhost/unit_test",
    )
    monkeypatch.setenv("SESSION_SECRET", session_secret)
    monkeypatch.setenv("SESSION_ABSOLUTE_HOURS", "8")
    try:
        yield session_secret
    finally:
        get_settings.cache_clear()


def test_password_hash_uses_required_argon2id_parameters() -> None:
    password_hash = hash_password("correct horse battery staple")
    parameters = extract_parameters(password_hash)

    # Assert the security contract rather than relying on argon2-cffi's changing defaults.
    assert parameters.type is Type.ID
    assert parameters.memory_cost >= 19 * 1024
    assert parameters.time_cost >= 2
    assert parameters.parallelism >= 1


def test_equal_passwords_receive_distinct_salted_hashes() -> None:
    first_hash = hash_password("same-password")
    second_hash = hash_password("same-password")

    # Unique salts prevent identical credentials from producing recognizable database values.
    assert first_hash != second_hash
    assert "same-password" not in first_hash
    assert "same-password" not in second_hash


def test_password_verification_accepts_only_the_correct_password() -> None:
    password_hash = hash_password("expected-password")

    assert verify_password("expected-password", password_hash) is True
    assert verify_password("wrong-password", password_hash) is False


def test_password_verification_treats_malformed_hash_as_failure() -> None:
    # Corrupt database input must not leak parser details or crash the future login flow.
    assert verify_password("any-password", "not-an-argon2-hash") is False


def test_rehash_detection_flags_weaker_parameters() -> None:
    weaker_hasher = PasswordHasher(
        time_cost=1,
        memory_cost=8 * 1024,
        parallelism=1,
        hash_len=32,
        salt_len=16,
        type=Type.ID,
    )
    weak_hash = weaker_hasher.hash("upgrade-this-password")
    current_hash = hash_password("current-password")

    # Login can replace only outdated hashes after successful verification.
    assert needs_rehash(weak_hash) is True
    assert needs_rehash(current_hash) is False


def test_session_tokens_are_url_safe_unique_and_high_entropy() -> None:
    tokens = {generate_session_token() for _ in range(100)}

    # token_urlsafe encodes all 32 random bytes while avoiding cookie-hostile characters.
    assert len(tokens) == 100
    assert all(len(token) >= SESSION_TOKEN_BYTES for token in tokens)
    assert all(token.replace("-", "").replace("_", "").isalnum() for token in tokens)


def test_session_token_hash_is_deterministic_keyed_and_fixed_length(
    configured_session_security: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    token = generate_session_token()
    first_hash = hash_session_token(token)
    repeated_hash = hash_session_token(token)

    assert first_hash == repeated_hash
    assert len(first_hash) == 64
    assert token not in first_hash
    assert hash_session_token(generate_session_token()) != first_hash

    # Rotating the pepper intentionally makes every existing lookup hash unusable.
    monkeypatch.setenv("SESSION_SECRET", f"{configured_session_security}-rotated")
    get_settings.cache_clear()
    assert hash_session_token(token) != first_hash


def test_session_expiry_uses_configured_absolute_lifetime(
    configured_session_security: str,
) -> None:
    created_at = datetime(2026, 6, 29, 12, tzinfo=UTC)

    assert calculate_session_expiry(created_at) == created_at + timedelta(hours=8)


def test_session_expiry_rejects_naive_timestamps(
    configured_session_security: str,
) -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        calculate_session_expiry(datetime(2026, 6, 29, 12))


def test_session_security_helpers_do_not_log_tokens_or_hashes(
    configured_session_security: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    token = generate_session_token()
    token_hash = hash_session_token(token)

    assert token not in caplog.text
    assert token_hash not in caplog.text
