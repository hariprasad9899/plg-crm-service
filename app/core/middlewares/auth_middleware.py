from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security.security import verify_token
from app.core.exceptions.handler import AppException
from app.core.exceptions.error_catalog import (
    UNAUTHORIZED,
    SESSION_REVOKED,
    INVALID_SESSION,
)
from app.domain.services.auth_service import AuthService
from app.dependencies.auth_dependenies import get_auth_service

bearer_scheme = HTTPBearer()


def authenticate_user(
    request: Request,
    service: AuthService = Depends(get_auth_service),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    # try cookie first (browser)
    token = request.cookies.get("access_token")

    # fallback to bearer header (microservices / mobile)
    if not token:
        if not credentials:
            raise AppException(UNAUTHORIZED)
        token = credentials.credentials

    payload = verify_token(token)
    session_id = payload["session_id"]
    session = service.get_session(session_id=session_id)

    if not session:
        raise AppException(INVALID_SESSION)
    if session.revoked_at:
        raise AppException(SESSION_REVOKED)

    request.state.session_id = payload["session_id"]
    request.state.user_id = payload["user_id"]
    request.state.tenant_id = payload["tenant_id"]

    return payload
