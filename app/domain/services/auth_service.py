from app.core.response import success_response
from app.infrastructure.database.repositories.auth_repository import AuthRepo
from app.core.exceptions.base import AppException
from app.core.exceptions.catalog import EMAIL_ALREADY_EXISTS, GENERIC_EXCEPTION
from app.core.security.password import hash_password


class AuthService:
    def __init__(self, repo: AuthRepo):
        self.repo = repo

    def create_user(self, full_name: str, email: str, password: str):
        user = self.repo.get_user_by_email(email=email)
        if user:
            raise AppException(EMAIL_ALREADY_EXISTS)
        try:
            user = self.repo.create_user(
                full_name=full_name, email=email, password=password
            )
            password_hash = hash_password(password=password)
            self.repo.create_auth_identity(
                user_id=user.id,
                provider="password",
                provider_email=user.primary_email,
                password_hash=password_hash,
                provider_user_id="",
            )
            self.repo.db.commit()
            self.repo.db.refresh(user)
            res_data = {
                "id": str(user.id),
                "name": user.full_name,
                "email": user.primary_email,
                "status": user.status,
            }
            return success_response(data=res_data)
        except Exception as e:
            self.repo.db.rollback()
            raise AppException(GENERIC_EXCEPTION)
