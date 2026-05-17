from fastapi import Depends
from app.infrastructure.database.session import get_db
from app.infrastructure.database.repositories.auth_repository import AuthRepo
from app.domain.services.auth_service import AuthService
from app.infrastructure.database.repositories.otp_repository import OtpRepo
from app.infrastructure.integrations.email.ses_email_service import SeSEmailService
from app.domain.services.otp_service import OtpService
from app.infrastructure.integrations.google.google_oauth_service import (
    GoogleOAuthService,
)
from app.core.config import Settings

settings = Settings()


def get_auth_service(db=Depends(get_db)):
    auth_repo = AuthRepo(db)
    otp_repo = OtpRepo(db)
    otp_service = OtpService(otp_repo)
    ses_email_service = SeSEmailService()
    google_oauth_service = GoogleOAuthService(
        settings.google_client_id, settings.google_client_secret
    )
    return AuthService(
        auth_repo=auth_repo,
        otp_service=otp_service,
        ses_email_service=ses_email_service,
        google_oauth_service=google_oauth_service,
    )
