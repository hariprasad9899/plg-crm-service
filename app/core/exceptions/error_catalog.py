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

OTP_RESEND_LIMIT_EXCEEDED = ErrorDefinition(
    code="OTP_RESEND_LIMIT_EXCEEDED",
    message="OTP Resend limit exceeded. Please try again later.",
    status_code=429,
)

USER_NOT_FOUND = ErrorDefinition(
    code="USER_NOT_FOUND", message="User not found.", status_code=404
)

INVALID_CREDENTIALS = ErrorDefinition(
    code="INVALID_CREDENTIALS",
    message="Invalid email or password.",
    status_code=401,
)

EMAIL_NOT_VERIFIED = ErrorDefinition(
    code="EMAIL_NOT_VERIFIED",
    message="Email is not verified.",
    status_code=403,
)

USER_DISABLED = ErrorDefinition(
    code="USER_DISABLED",
    message="User account is disabled.",
    status_code=403,
)

UNAUTHORIZED = ErrorDefinition(
    code="UNAUTHORIZED",
    message="Authentication credentials were not provided.",
    status_code=401,
)

INVALID_TOKEN = ErrorDefinition(
    code="INVALID_TOKEN",
    message="Invalid access token.",
    status_code=401,
)

SESSION_NOT_FOUND = ErrorDefinition(
    code="SESSION_NOT_FOUND",
    message="Session not found.",
    status_code=404,
)

INVALID_SESSION = ErrorDefinition(
    code="INVALID_SESSION",
    message="Invalid session.",
    status_code=401,
)

SESSION_REVOKED = ErrorDefinition(
    code="SESSION_REVOKED",
    message="Session has been revoked.",
    status_code=401,
)

SESSION_EXPIRED = ErrorDefinition(
    code="SESSION_EXPIRED",
    message="Session has expired.",
    status_code=401,
)


ACCESS_TOKEN_EXPIRED = ErrorDefinition(
    code="ACCESS_TOKEN_EXPIRED",
    message="Access token has expired.",
    status_code=401,
)

REFRESH_TOKEN_EXPIRED = ErrorDefinition(
    code="REFRESH_TOKEN_EXPIRED",
    message="Refresh token has expired.",
    status_code=401,
)

LOGIN_REQUIRED = ErrorDefinition(
    code="LOGIN_REQUIRED",
    message="Login required.",
    status_code=401,
)

TOKEN_MISSING = ErrorDefinition(
    code="TOKEN_MISSING",
    message="Authentication token is missing.",
    status_code=401,
)

INVALID_AUTH_PROVIDER = ErrorDefinition(
    code="INVALID_AUTH_PROVIDER",
    message="Invalid authentication provider.",
    status_code=400,
)

USER_ALREADY_LOGGED_OUT = ErrorDefinition(
    code="USER_ALREADY_LOGGED_OUT",
    message="User already logged out.",
    status_code=400,
)

FORBIDDEN = ErrorDefinition(
    code="FORBIDDEN",
    message="You do not have permission to perform this action.",
    status_code=403,
)

INVALID_GOOGLE_TOKEN = ErrorDefinition(
    code="INVALID_GOOGLE_TOKEN", message="Invalid google token", status_code=400
)

GOOGLE_EMAIL_NOT_VERIFIED = ErrorDefinition(
    code="GOOGLE_EMAIL_NOT_VERIFIED",
    message="Google email not verified",
    status_code=400,
)
