from app.domain.ports.otp_ports import OptPort
from app.infrastructure.database.repositories.otp_repository import OtpRepo
from datetime import datetime, UTC, timedelta
from app.infrastructure.database.models.otp_models import OTPPurposeEnum
import secrets
from app.core.security.security import hash_value, verify_hash
from app.core.exceptions.base import AppException
from app.core.exceptions.error_catalog import (
    OTP_EXPIRED,
    OTP_INVALID,
    OTP_MAX_ATTEMPTS_EXCEEDED,
    OTP_REQUEST_TOO_FREQUENT,
)


class OtpService(OptPort):
    def __init__(self, repo: OtpRepo):
        self.repo = repo

    def create_otp(self, auth_identity_id: str, purpose: OTPPurposeEnum):
        try:

            latest_otp = self.repo.get_recent_active_otp(
                auth_identity_id=auth_identity_id, purpose=purpose
            )

            if latest_otp:
                raise AppException(OTP_REQUEST_TOO_FREQUENT)

            active_otps = self.repo.get_active_otps(
                auth_identity_id=auth_identity_id, purpose=purpose
            )

            if active_otps:
                for otp in active_otps:
                    otp.consumed_at = datetime.now(UTC)

            otp = str(secrets.randbelow(900000) + 100000)
            otp_hash = hash_value(otp)
            expires_at = datetime.now(UTC) + timedelta(minutes=5)

            self.repo.create_otp(
                auth_identity_id=auth_identity_id,
                otp_hash=otp_hash,
                purpose=purpose,
                expires_at=expires_at,
            )
            self.repo.db.commit()
            return {"otp": otp, "expires_at": expires_at}
        except Exception:
            self.repo.db.rollback()
            raise

    def verify_otp(self, auth_identity_id: str, purpose: OTPPurposeEnum, inp_otp: int):
        try:
            active_otp = self.repo.get_active_otp_for_verification(
                auth_identity_id=auth_identity_id, purpose=purpose
            )
            if not active_otp:
                raise AppException(OTP_EXPIRED)
            if active_otp.attempt_count >= 5:
                active_otp.consumed_at = datetime.now(UTC)
                self.repo.db.commit()
                raise AppException(OTP_MAX_ATTEMPTS_EXCEEDED)
            if verify_hash(inp_otp, active_otp.otp_hash):
                active_otp.consumed_at = datetime.now(UTC)
                self.repo.db.commit()
                return True
            else:
                active_otp.attempt_count += 1
                self.repo.db.commit()
                raise AppException(OTP_INVALID)
        except Exception:
            self.repo.db.rollback()
            raise

    def resend_otp(self, auth_identity_id: str, purpose: OTPPurposeEnum):
        return self.create_otp(auth_identity_id=auth_identity_id, purpose=purpose)
