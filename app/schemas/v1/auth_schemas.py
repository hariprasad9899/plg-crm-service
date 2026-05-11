from pydantic import BaseModel, EmailStr


class SignUpUser(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class SignupUserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    status: str
