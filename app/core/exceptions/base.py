from app.core.exceptions.error_catalog import ErrorDefinition


class AppException(Exception):

    def __init__(self, error: ErrorDefinition, details=None):
        self.error = error
        self.details = details
