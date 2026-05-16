from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security.security import verify_token
from app.core.exceptions.handler import AppException
from app.core.exceptions.error_catalog import UNAUTHORIZED

bearer_scheme = HTTPBearer()


def authenticate_and_authorize(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    if not credentials:
        raise AppException(UNAUTHORIZED)
    token = credentials.credentials
    payload = verify_token(token)
    return payload
