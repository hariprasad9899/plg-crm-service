from app.core.response import success_response
from app.infrastructure.database.repositories.auth_repository import AuthRepo
from app.core.exceptions.base import AppException
from app.core.exceptions.error_catalog import (
    EMAIL_ALREADY_EXISTS,
    USER_NOT_FOUND,
    INVALID_CREDENTIALS,
    USER_DISABLED,
    SESSION_NOT_FOUND,
    INVALID_TOKEN,
    SESSION_REVOKED,
    SESSION_EXPIRED,
    GOOGLE_EMAIL_NOT_VERIFIED,
)
from app.core.security.security import (
    hash_value,
    verify_hash,
    create_jwt,
    generator_random_token,
    hash_refresh_token,
)
from app.domain.services.otp_service import OtpService
from app.infrastructure.integrations.email.ses_email_service import SeSEmailService
from app.infrastructure.database.models.otp_models import OTPPurposeEnum
from app.domain.ports.auth_ports import AuthPort
from datetime import datetime, UTC, timedelta
from app.core.constants import TokenConstants
from app.infrastructure.integrations.google.google_oauth_service import (
    GoogleOAuthService,
)


class AuthService(AuthPort):
    def __init__(
        self,
        auth_repo: AuthRepo,
        otp_service: OtpService,
        ses_email_service: SeSEmailService,
        google_oauth_service: GoogleOAuthService,
    ):
        self.auth_repo = auth_repo
        self.otp_service = otp_service
        self.email_service = ses_email_service
        self.google_oauth_service = google_oauth_service

    def create_user(
        self,
        full_name: str,
        email: str,
        password: str,
        background_tasks,
    ):
        user = self.auth_repo.get_user_by_email(email=email)
        if user:
            raise AppException(EMAIL_ALREADY_EXISTS)
        try:
            password_hash = hash_value(value=password)
            user = self.auth_repo.create_user(
                full_name=full_name,
                email=email,
                avatar_url=None,
                is_email_verified=False,
            )
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
                auth_identity_id=auth_identity.id,
                purpose=OTPPurposeEnum.EMAIL_VERIFICATION,
            )
            background_tasks.add_task(
                self.email_service.send_otp_verification_mail,
                to_email=user.primary_email,
                otp=otp_data["otp"],
            )
            res_data = {
                "id": str(user.id),
                "auth_id": str(auth_identity.id),
                "name": user.full_name,
                "email": user.primary_email,
                "status": user.status,
                "is_email_verified": False,
            }
            return success_response(data=res_data)
        except Exception:
            self.auth_repo.db.rollback()
            raise

    def send_otp(
        self, auth_identity_id: str, purpose: OTPPurposeEnum, background_tasks
    ):
        try:
            auth_user = self.auth_repo.get_user_by_auth_id(
                auth_identity_id=auth_identity_id
            )
            auth_user_email = auth_user.provider_email
            otp_data = self.otp_service.resend_otp(
                auth_identity_id=auth_identity_id,
                purpose=OTPPurposeEnum.EMAIL_VERIFICATION,
            )
            background_tasks.add_task(
                self.email_service.send_otp_verification_mail,
                to_email=auth_user_email,
                otp=otp_data["otp"],
            )
            res_data = {
                "message": "OTP resent successfully",
                "expires_at": otp_data["expires_at"].isoformat(),
            }
            return success_response(res_data)
        except Exception:
            raise

    def verify_otp(self, auth_identity_id: str, purpose: OTPPurposeEnum, otp: int):
        try:
            self.otp_service.verify_otp(
                auth_identity_id=auth_identity_id,
                purpose=purpose,
                inp_otp=otp,
            )

            auth_user = self.auth_repo.get_user_by_auth_id(
                auth_identity_id=auth_identity_id
            )

            if not auth_user:
                raise AppException(USER_NOT_FOUND)

            auth_user.user.is_email_verified = True

            self.auth_repo.db.commit()
            self.auth_repo.db.refresh(auth_user.user)

            res_data = {
                "message": "OTP verified successfully",
            }

            return success_response(res_data)
        except Exception:
            raise

    def login_user(self, email: str, password: str, ip_address: str, user_agent: str):
        try:
            auth_identity = self.auth_repo.get_auth_by_provider_email(email=email)
            if not auth_identity:
                raise AppException(INVALID_CREDENTIALS)

            is_valid = verify_hash(
                plain_value=password, hash_value=auth_identity.password_hash
            )

            if not is_valid:
                raise AppException(INVALID_CREDENTIALS)

            user = auth_identity.user
            if not user.is_active:
                raise AppException(USER_DISABLED)

            expires_at = datetime.now(UTC) + timedelta(
                days=TokenConstants.REFRESH_TOKEN_EXP_PERIOD_DAYS
            )

            refresh_token = generator_random_token()
            refresh_token_hash = hash_refresh_token(refresh_token)
            session = self.auth_repo.create_session(
                user_id=user.id,
                tenant_id=None,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=expires_at,
                refresh_token_hash=refresh_token_hash,
            )

            access_token = create_jwt(
                user_id=user.id, tenant_id=None, session_id=session.id
            )

            self.auth_repo.db.commit()

            user_data = {
                "id": str(user.id),
                "auth_id": str(auth_identity.id),
                "name": user.full_name,
                "email": user.primary_email,
                "is_email_verified": user.is_email_verified,
            }

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user_data": user_data,
            }

        except Exception:
            self.auth_repo.db.rollback()
            raise

    def get_user(self, user_id: str):
        try:
            user = self.auth_repo.get_user_by_user_id(user_id=user_id)
            if not user:
                raise AppException(USER_NOT_FOUND)
            res_data = {
                "id": str(user.id),
                "name": user.full_name,
                "email": user.primary_email,
                "is_email_verified": user.is_email_verified,
            }
            return success_response(res_data)
        except Exception:
            raise

    def get_session(self, session_id: str):
        session = self.auth_repo.get_session_by_id(session_id=session_id)
        if not session:
            raise AppException(SESSION_NOT_FOUND)
        return session

    def rotate_refresh_token(self, refresh_token: str):
        try:
            refresh_token_hash = hash_refresh_token(refresh_token)
            session = self.auth_repo.get_session_by_refresh_token_hash(
                refresh_token_hash=refresh_token_hash
            )
            if not session:
                raise AppException(INVALID_TOKEN)
            if session.revoked_at:
                raise AppException(SESSION_REVOKED)
            if session.expires_at < datetime.now(UTC):
                raise AppException(SESSION_EXPIRED)

            user = session.user

            new_access_token = create_jwt(
                user_id=user.id, tenant_id=None, session_id=session.id
            )
            new_refresh_token = generator_random_token()
            new_refresh_token_hash = hash_refresh_token(new_refresh_token)

            session.refresh_token_hash = new_refresh_token_hash
            self.auth_repo.db.commit()

            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
            }
        except Exception:
            self.auth_repo.db.rollback()
            raise

    def logout_user(self, session_id: str):
        try:
            session = self.auth_repo.get_session_by_id(session_id=session_id)
            if session:
                session.revoked_at = datetime.now(UTC)
            self.auth_repo.db.commit()
            return True
        except Exception:
            raise

    def authenticate_google_user(
        self, google_auth_code: str, ip_address: str, user_agent: str
    ):
        try:
            # verifiy and get google data
            google_user = self.google_oauth_service.exchange_code(code=google_auth_code)
            google_data = self.google_oauth_service.verify_google_id_token(
                google_user["id_token"]
            )

            # extract google info
            google_sub = google_data["sub"]
            email = google_data["email"]
            name = google_data["name"]
            avatar = google_data.get("picture")

            if not google_data.get("email_verified"):
                raise AppException(GOOGLE_EMAIL_NOT_VERIFIED)

            # check google identity exist
            auth_identity = self.auth_repo.get_auth_identity_by_provider(
                provider_user_id=google_sub, provider="google"
            )

            # case1: existing google user
            if auth_identity:
                user = auth_identity.user
            else:
                # check user exist by email
                user = self.auth_repo.get_user_by_email(email=email)

                # case2: existing password user
                if user:
                    user.is_email_verified = True
                    # link google account
                    auth_identity = self.auth_repo.create_auth_identity(
                        user_id=user.id,
                        provider="google",
                        provider_user_id=google_sub,
                        provider_email=email,
                        password_hash=None,
                    )
                # case3: new user
                else:
                    user = self.auth_repo.create_user(
                        full_name=name,
                        email=email,
                        avatar_url=avatar,
                        is_email_verified=True,
                    )

                    auth_identity = self.auth_repo.create_auth_identity(
                        user_id=user.id,
                        provider="google",
                        provider_user_id=google_sub,
                        provider_email=email,
                        password_hash=None,
                    )

            user.last_login_at = datetime.now(UTC)

            # create session
            expires_at = datetime.now(UTC) + timedelta(
                days=TokenConstants.REFRESH_TOKEN_EXP_PERIOD_DAYS
            )
            refresh_token = generator_random_token()
            refresh_token_hash = hash_refresh_token(refresh_token)
            session = self.auth_repo.create_session(
                user_id=user.id,
                tenant_id=None,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=expires_at,
                refresh_token_hash=refresh_token_hash,
            )

            access_token = create_jwt(
                user_id=user.id, tenant_id=None, session_id=session.id
            )

            self.auth_repo.db.commit()
            self.auth_repo.db.refresh(user)

            user_data = {
                "id": str(user.id),
                "auth_id": str(auth_identity.id),
                "name": user.full_name,
                "email": user.primary_email,
                "is_email_verified": user.is_email_verified,
            }

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user_data": user_data,
            }

        except Exception:
            self.auth_repo.db.rollback()
            raise
