from fastapi import FastAPI
from app.api.v1.router import router as v1_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from app.core.exceptions.base import AppException
from app.core.exceptions.handler import (
    app_exception_handler,
    validation_exception_handler,
    integrity_exception_handler,
    generic_exeption_handler,
)

app = FastAPI(title="auth-service")

origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_exception_handler)
app.add_exception_handler(Exception, generic_exeption_handler)
app.include_router(v1_router)


@app.get("/")
def root():
    return {"message": "Hello World"}
