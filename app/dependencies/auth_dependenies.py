from fastapi import Depends
from app.infrastructure.database.session import get_db
from app.infrastructure.database.repositories.auth_repository import AuthRepo
from app.domain.services.auth_service import AuthService
from app.core.config import Settings


def get_auth_service(db=Depends(get_db)):
    repo = AuthRepo(db)
    return AuthService(repo)
