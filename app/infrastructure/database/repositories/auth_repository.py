from sqlalchemy.orm import Session as SQLAlchemySession
from app.infrastructure.database.models.auth_models import (
    User,
    UserStatusEnum,
    AuthIdentity,
    AuthProviderEnum,
    Session,
)
from pydantic import EmailStr


class AuthRepo:
    def __init__(self, db: SQLAlchemySession):
        self.db = db

    def create_user(self, full_name: str, email: EmailStr, password: str):
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
        provider_email: EmailStr,
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

    def get_auth_by_provider_email(self, email: EmailStr):
        auth_identity = (
            self.db.query(AuthIdentity)
            .filter(AuthIdentity.provider_email == email)
            .first()
        )
        return auth_identity

    def create_session(
        self,
        user_id: str,
        tenant_id: str,
        ip_address: str,
        user_agent: str,
        expires_at: str,
        refresh_token_hash: str,
    ):
        session = Session(
            user_id=user_id,
            tenant_id=tenant_id,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            refresh_token_hash=refresh_token_hash,
        )
        self.db.add(session)
        self.db.flush()
        return session

    def get_session_by_id(self, session_id: str):
        session = self.db.query(Session).filter(Session.id == session_id).first()
        return session

    def get_session_by_refresh_token_hash(self, refresh_token_hash: str):
        session = (
            self.db.query(Session)
            .filter(Session.refresh_token_hash == refresh_token_hash)
            .first()
        )
        return session
