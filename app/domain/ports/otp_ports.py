from abc import ABC, abstractmethod
from app.infrastructure.database.models.otp_models import OTPPurposeEnum


class OptPort:

    @abstractmethod
    def create_otp(
        self,
        auth_identity_id: str,
        purpose: str,
    ):
        pass

    @abstractmethod
    def verify_otp(self, auth_identity_id: str, purpose: OTPPurposeEnum, inp_otp: str):
        pass

    @abstractmethod
    def resend_otp(self, auth_identity_id: str, purpose: OTPPurposeEnum, inp_otp: str):
        pass
