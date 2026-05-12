from fastapi.responses import JSONResponse


def success_response(data=None, status_code=200):

    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "data": data,
            "error": None,
        },
    )


def error_response(*, code: str, message: str, status_code: int, details=None):

    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": code,
                "message": message,
                "details": details,
            },
        },
    )
