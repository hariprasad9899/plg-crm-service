from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from app.core.exceptions.base import AppException
from app.core.response import error_response
import logging

logger = logging.getLogger(__name__)


async def app_exception_handler(request: Request, exc: AppException):

    return error_response(
        code=exc.error.code,
        message=exc.error.message,
        status_code=exc.error.status_code,
        details=exc.details,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []

    for err in exc.errors():
        errors.append(
            {
                "field": ".".join(map(str, err["loc"])),
                "message": err["msg"],
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation Failed",
                "errors": errors,
            },
        },
    )


async def integrity_exception_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={
            "success": False,
            "error": {
                "code": "DATABASE_CONFLICT",
                "message": "Database Conflict occured",
            },
        },
    )


async def generic_exeption_handler(request: Request, exc: Exception):
    logger.exception(exc)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Something went wrong",
            },
        },
    )
