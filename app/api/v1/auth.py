from fastapi import APIRouter, Depends, BackgroundTasks, Request, Response
from app.schemas.v1.auth_schemas import (
    SignUpUser,
    SignupUserResponse,
    ResendOtpResponse,
    ResendOtp,
    VerifyOtp,
    SignInUser,
    SignInUserResponse,
)
from app.domain.services.auth_service import AuthService
from app.dependencies.auth_dependenies import get_auth_service
from app.core.response import success_response
from app.core.config import Settings
from app.core.middlewares.auth_middleware import authenticate_user
from app.core.exceptions.handler import AppException
from app.core.exceptions.error_catalog import (
    USER_NOT_FOUND,
    UNAUTHORIZED,
    SESSION_NOT_FOUND,
)

router = APIRouter(prefix="/auth", tags=["Auth"])

settings = Settings()


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
        auth_identity_id=data.auth_id,
        purpose=data.purpose,
        background_tasks=background_tasks,
    )


@router.post("/verify-otp", response_model=ResendOtpResponse)
def verify_otp(
    data: VerifyOtp,
    service: AuthService = Depends(get_auth_service),
):
    return service.verify_otp(
        auth_identity_id=data.auth_id,
        purpose=data.purpose,
        otp=data.otp,
    )


@router.post("/login", response_model=SignInUserResponse)
def signin_user(
    data: SignInUser,
    request: Request,
    service: AuthService = Depends(get_auth_service),
):
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent")

    login_data = service.login_user(
        email=data.email,
        password=data.password,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    user_data = login_data["user_data"]
    cookies = [
        {
            "key": "access_token",
            "value": login_data["access_token"],
            "httponly": True,
            "secure": settings.is_production,
            "samesite": "lax",
        },
        {
            "key": "refresh_token",
            "value": login_data["refresh_token"],
            "httponly": True,
            "secure": settings.is_production,
            "samesite": "lax",
        },
    ]

    return success_response(user_data, cookies=cookies)


@router.get(
    "/me",
    response_model=SignInUserResponse,
    dependencies=[Depends(authenticate_user)],
)
def me(
    request: Request,
    service: AuthService = Depends(get_auth_service),
):
    user_id = request.state.user_id

    if not user_id:
        raise AppException(USER_NOT_FOUND)
    return service.get_user(user_id=user_id)


@router.post("/refresh", response_model=None)
def refresh(request: Request, service: AuthService = Depends(get_auth_service)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise AppException(UNAUTHORIZED)
    token_data = service.rotate_refresh_token(refresh_token=refresh_token)
    cookies = [
        {
            "key": "access_token",
            "value": token_data["access_token"],
            "httponly": True,
            "secure": settings.is_production,
            "samesite": "lax",
        },
        {
            "key": "refresh_token",
            "value": token_data["refresh_token"],
            "httponly": True,
            "secure": settings.is_production,
            "samesite": "lax",
        },
    ]
    return success_response(data=None, cookies=cookies)


@router.post(
    "/logout",
    response_model=None,
    dependencies=[Depends(authenticate_user)],
)
def logout(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    session_id = request.state.session_id
    if not session_id:
        raise AppException(SESSION_NOT_FOUND)
    service.logout_user(session_id=session_id)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return success_response(None, cookies=[])
