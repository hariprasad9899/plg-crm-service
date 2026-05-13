from app.core.response import success_response
from app.infrastructure.database.repositories.auth_repository import AuthRepo
from app.core.exceptions.base import AppException
from app.core.exceptions.error_catalog import EMAIL_ALREADY_EXISTS
from app.core.security.security import hash_value
from app.domain.services.otp_service import OtpService
from app.infrastructure.integrations.email.ses_email_service import SeSEmailService
from app.infrastructure.database.models.otp_models import OTPPurposeEnum


class AuthService:
    def __init__(
        self,
        auth_repo: AuthRepo,
        otp_service: OtpService,
        ses_email_service: SeSEmailService,
    ):
        self.auth_repo = auth_repo
        self.otp_service = otp_service
        self.email_service = ses_email_service

    def create_user(
        self,
        full_name: str,
        email: str,
        password: str,
        background_tasks,
    ):
        user = self.auth_repo.get_user_by_email(email=email)
        if user:
            if user.is_email_verified:
                raise AppException(EMAIL_ALREADY_EXISTS)
            else:
                # TODO
                pass
        try:
            user = self.auth_repo.create_user(
                full_name=full_name, email=email, password=password
            )
            password_hash = hash_value(value=password)
            auth_identity = self.auth_repo.create_auth_identity(
                user_id=user.id,
                provider="password",
                provider_email=user.primary_email,
                password_hash=password_hash,
                provider_user_id="",
            )

            self.auth_repo.db.commit()
            self.auth_repo.db.refresh(user)

            otp_data = self.otp_service.create_otp(
                auth_identity.id, OTPPurposeEnum.EMAIL_VERIFICATION
            )
            background_tasks.add_task(
                self.email_service.send_otp_verification_mail,
                to_email=user.primary_email,
                otp=otp_data["otp"],
            )
            res_data = {
                "id": str(user.id),
                "name": user.full_name,
                "email": user.primary_email,
                "status": user.status,
                "is_email_verified": False,
            }
            return success_response(data=res_data)
        except Exception:
            self.auth_repo.db.rollback()
            raise
