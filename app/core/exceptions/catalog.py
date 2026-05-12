from dataclasses import dataclass


@dataclass
class ErrorDefinition:
    code: str
    message: str
    status_code: int


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

GENERIC_EXCEPTION = ErrorDefinition(
    code="SOMETHING_WENT_WRONG", message="Something went wrong", status_code=500
)
