class ApiException(Exception):
    """Raised when the API returns an error or invalid response."""
    pass


class EnrollmentException(ApiException):
    """Raised when trying to perform MFA on a user who is not enrolled in that factor."""
    pass
