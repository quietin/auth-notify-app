# tests/unit/test_security.py

from app.utils.security import get_password_hash, verify_password

def test_get_password_hash_returns_hash():
    password = "my_secret"
    hashed = get_password_hash(password)
    assert isinstance(hashed, str)
    assert hashed != password
    # Typical bcrypt prefixes
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")

def test_verify_password_correct():
    password = "my_secret"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True

def test_verify_password_incorrect():
    password = "my_secret"
    wrong_password = "not_my_secret"
    hashed = get_password_hash(password)
    assert verify_password(wrong_password, hashed) is False
