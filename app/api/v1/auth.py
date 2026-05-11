from fastapi import APIRouter, Depends, Response, Request, HTTPException
from app.schemas.v1.auth_schemas import SignUpUser, SignupUserResponse
from app.domain.services.auth_service import AuthService
from app.dependencies.auth_dependenies import get_auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=SignupUserResponse)
def signup(data: SignUpUser, service: AuthService = Depends(get_auth_service)):
    return service.create_user(
        full_name=data.full_name, email=data.email, password=data.password
    )
