from sqlalchemy.orm import Session
from app.domain.ports.auth_ports import AuthPort
from app.infrastructure.database.models.auth_models import (
    User,
    UserStatusEnum,
    AuthIdentity,
    AuthProviderEnum,
)


class AuthRepo:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, full_name: str, email: str, password: str):
        user = User(
            full_name=full_name,
            primary_email=email,
            status=UserStatusEnum.ACTIVE,
        )
        self.db.add(user)
        self.db.flush()
        return user

    def get_user_by_email(self, email: str):
        user = self.db.query(User).filter(User.primary_email == email).first()
        return user

    def create_auth_identity(
        self,
        user_id: str,
        provider: AuthProviderEnum,
        provider_email: str,
        password_hash: str,
        provider_user_id: str = "",
    ):
        auth_identity = AuthIdentity(
            user_id=user_id,
            provider=provider,
            provider_email=provider_email,
            password_hash=password_hash,
            provider_user_id=provider_user_id,
        )
        self.db.add(auth_identity)
        self.db.flush()
        return auth_identity

    def get_user_by_auth_id(self, auth_identity_id: str):
        auth_user = (
            self.db.query(AuthIdentity)
            .filter(AuthIdentity.id == auth_identity_id)
            .first()
        )
        return auth_user

    def get_user_by_user_id(self, user_id: str):
        user = self.db.query(User).filter(User.id == user_id).first()
        return user
