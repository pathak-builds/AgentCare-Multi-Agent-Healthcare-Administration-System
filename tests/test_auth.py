"""
Tests for JWT authentication and password hashing.
"""

from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.auth.jwt import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.config import settings


# ---------------------------------------------------------------------
# Password Hashing
# ---------------------------------------------------------------------

def test_password_hashing():
    """Password hashing and verification."""

    password = "secret123"

    hashed = hash_password(password)

    assert hashed != password
    assert isinstance(hashed, str)

    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


# ---------------------------------------------------------------------
# JWT Creation
# ---------------------------------------------------------------------

def test_create_access_token():
    """JWT creation."""

    token = create_access_token(
        user_id="user123",
        role="patient",
    )

    assert isinstance(token, str)
    assert len(token) > 20


# ---------------------------------------------------------------------
# JWT Decoding
# ---------------------------------------------------------------------

def test_decode_access_token():
    """JWT should decode correctly."""

    token = create_access_token(
        user_id="user123",
        role="patient",
    )

    payload = decode_access_token(token)

    assert payload["sub"] == "user123"
    assert payload["role"] == "patient"

    assert "exp" in payload
    assert "iat" in payload


# ---------------------------------------------------------------------
# Invalid Token
# ---------------------------------------------------------------------

def test_invalid_token():

    with pytest.raises(ValueError, match="Invalid token"):
        decode_access_token("invalid.token.here")


# ---------------------------------------------------------------------
# Expired Token
# ---------------------------------------------------------------------

def test_expired_token():

    expired_payload = {
        "sub": "user123",
        "role": "patient",
        "iat": datetime.now(timezone.utc) - timedelta(hours=2),
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }

    expired_token = jwt.encode(
        expired_payload,
        settings.jwt_secret,
        algorithm="HS256",
    )

    with pytest.raises(ValueError, match="Token has expired"):
        decode_access_token(expired_token)


# ---------------------------------------------------------------------
# Different Users Produce Different Tokens
# ---------------------------------------------------------------------

def test_different_users_get_different_tokens():

    token1 = create_access_token(
        user_id="user1",
        role="patient",
    )

    token2 = create_access_token(
        user_id="user2",
        role="patient",
    )

    assert token1 != token2