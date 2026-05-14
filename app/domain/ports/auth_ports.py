from abc import ABC, abstractmethod
from app.infrastructure.database.models.otp_models import OTPPurposeEnum


class AuthPort(ABC):

    @abstractmethod
    def create_user(self, full_name: str, email: str, password: str):
        pass

    @abstractmethod
    def send_otp(self, auth_identity_id: str, purpose: OTPPurposeEnum):
        pass
