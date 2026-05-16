from fastapi.responses import JSONResponse


def success_response(data=None, status_code=200, cookies: list[dict] = None):
    response = JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "data": data,
            "error": None,
        },
    )

    if cookies:
        for cookie in cookies:
            response.set_cookie(**cookie)

    return response


def error_response(
    *,
    code: str,
    message: str,
    status_code: int,
    details=None,
    cookies: list[dict] = None
):

    response = JSONResponse(
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

    if cookies:
        for cookie in cookies:
            response.set_cookie(**cookie)
    return response
