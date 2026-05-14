from fastapi import APIRouter, Depends, BackgroundTasks
from app.schemas.v1.auth_schemas import (
    SignUpUser,
    SignupUserResponse,
    ResendOtpResponse,
    ResendOtp,
)
from app.domain.services.auth_service import AuthService
from app.dependencies.auth_dependenies import get_auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=SignupUserResponse)
def signup(
    data: SignUpUser,
    background_tasks: BackgroundTasks,
    service: AuthService = Depends(get_auth_service),
):
    return service.create_user(
        full_name=data.full_name,
        email=data.email,
        password=data.password,
        background_tasks=background_tasks,
    )


@router.post("/resend-otp", response_model=ResendOtpResponse)
def resend_otp(
    data: ResendOtp,
    background_tasks: BackgroundTasks,
    service: AuthService = Depends(get_auth_service),
):
    return service.send_otp(
        auth_identity_id=data.auth_identity_id,
        purpose=data.purpose,
        background_tasks=background_tasks,
    )
