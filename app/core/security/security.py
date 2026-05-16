from pwdlib import PasswordHash
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import time
from app.core.config import Settings
from app.core.exceptions.handler import AppException
from app.core.exceptions.error_catalog import (
    INVALID_SESSION,
    SESSION_EXPIRED,
    SESSION_EXPIRED,
)
import secrets

settings = Settings()

password_hash = PasswordHash.recommended()


def hash_value(value: str) -> str:
    return password_hash.hash(value)


def verify_hash(plain_value: str, hash_value: str) -> bool:
    return password_hash.verify(plain_value, hash_value)


def get_iat():
    return int(time.time())


def create_jwt(user_id: str, tenant_id: str, session_id: str):
    iat_time = get_iat()
    payload = {
        "user_id": str(user_id),
        "tenant_id": str(tenant_id),
        "session_id": str(session_id),
        "exp": iat_time + 15 * 60,
        "iat": iat_time,
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")


def generator_random_token():
    return secrets.token_urlsafe(64)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms="HS256")
        if payload.get("type") != "access":
            raise AppException(INVALID_SESSION)
        return payload
    except ExpiredSignatureError:
        raise AppException(SESSION_EXPIRED)
    except InvalidTokenError:
        raise AppException(INVALID_SESSION)
