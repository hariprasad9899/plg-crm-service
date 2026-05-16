from abc import ABC, abstractmethod
from app.infrastructure.database.models.otp_models import OTPPurposeEnum
from pydantic import EmailStr


class AuthPort(ABC):

    @abstractmethod
    def create_user(self, full_name: str, email: str, password: str):
        pass

    @abstractmethod
    def send_otp(self, auth_identity_id: str, purpose: OTPPurposeEnum):
        pass

    @abstractmethod
    def verify_otp(self, auth_identity_id: str, purpose: OTPPurposeEnum, otp: int):
        pass

    @abstractmethod
    def login_user(self, email: EmailStr, password: str):
        pass
