from sqlalchemy.orm import Session
from app.infrastructure.database.models.otp_models import AuthOTP
from datetime import datetime, UTC, timedelta
from app.infrastructure.database.models.otp_models import OTPPurposeEnum


class OtpRepo:
    def __init__(self, db: Session):
        self.db = db

    def create_otp(
        self,
        auth_identity_id: str,
        otp_hash: str,
        purpose: str,
        expires_at: str,
    ):
        auth_otp = AuthOTP(
            auth_identity_id=auth_identity_id,
            otp_hash=otp_hash,
            purpose=purpose,
            expires_at=expires_at,
        )
        self.db.add(auth_otp)
        self.db.flush()
        return auth_otp

    def get_active_otps(self, auth_identity_id: str, purpose: OTPPurposeEnum):
        return (
            self.db.query(AuthOTP)
            .filter(
                AuthOTP.auth_identity_id == auth_identity_id,
                AuthOTP.purpose == purpose.value,
                AuthOTP.consumed_at.is_(None),
                AuthOTP.expires_at > datetime.now(UTC),
            )
            .order_by(AuthOTP.created_at.desc())
            .all()
        )

    def get_recent_active_otp(self, auth_identity_id: str, purpose: OTPPurposeEnum):
        return (
            self.db.query(AuthOTP)
            .filter(
                AuthOTP.auth_identity_id == auth_identity_id,
                AuthOTP.purpose == purpose.value,
                AuthOTP.consumed_at.is_(None),
                AuthOTP.created_at > datetime.now(UTC) - timedelta(seconds=30),
            )
            .order_by(AuthOTP.created_at.desc())
            .first()
        )

    def get_active_otp_for_verification(
        self, auth_identity_id: str, purpose: OTPPurposeEnum
    ):
        return (
            self.db.query(AuthOTP)
            .filter(
                AuthOTP.auth_identity_id == auth_identity_id,
                AuthOTP.purpose == purpose.value,
                AuthOTP.consumed_at.is_(None),
                AuthOTP.expires_at > datetime.now(UTC),
            )
            .order_by(AuthOTP.created_at.desc())
            .first()
        )
