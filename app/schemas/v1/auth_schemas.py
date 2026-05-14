from pydantic import BaseModel, EmailStr
from app.infrastructure.database.models.otp_models import OTPPurposeEnum


class SignUpUser(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class SignupUserResponse(BaseModel):
    id: str
    auth_id: str
    name: str
    email: EmailStr
    status: str


class ResendOtpResponse(BaseModel):
    message: str
    expires_at: int


class ResendOtp(BaseModel):
    auth_identity_id: str
    purpose: OTPPurposeEnum
