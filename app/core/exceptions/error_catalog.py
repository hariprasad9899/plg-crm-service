from dataclasses import dataclass


@dataclass
class ErrorDefinition:
    code: str
    message: str
    status_code: int


GENERIC_EXCEPTION = ErrorDefinition(
    code="SOMETHING_WENT_WRONG", message="Something went wrong", status_code=500
)

INVALID_CREDENTIALS = ErrorDefinition(
    code="INVALID_CREDENTIALS",
    message="Invalid email or password",
    status_code=401,
)

USER_NOT_FOUND = ErrorDefinition(
    code="USER_NOT_FOUND",
    message="User not found",
    status_code=404,
)

EMAIL_ALREADY_EXISTS = ErrorDefinition(
    code="EMAIL_ALREADY_EXISTS",
    message="Email already exists",
    status_code=409,
)


OTP_MAX_ATTEMPTS_EXCEEDED = ErrorDefinition(
    code="OTP_MAX_ATTEMPTS_EXCEEDED", message="Too many attempts", status_code=429
)

OTP_INVALID = ErrorDefinition(
    code="OTP_INVALID",
    message="Invalid OTP.",
    status_code=400,
)

OTP_EXPIRED = ErrorDefinition(
    code="OTP_EXPIRED",
    message="OTP has expired. Please request a new one.",
    status_code=400,
)

OTP_REQUEST_TOO_FREQUENT = ErrorDefinition(
    code="OTP_REQUEST_TOO_FREQUENT",
    message="OTP requests are too frequent. Please try again later.",
    status_code=429,
)
