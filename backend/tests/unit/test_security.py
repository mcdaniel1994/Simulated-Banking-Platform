from app.core.security import hash_password, needs_rehash, verify_password
from argon2 import PasswordHasher, Type, extract_parameters


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
