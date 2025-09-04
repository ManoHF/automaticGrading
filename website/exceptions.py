class UserInputError(Exception):
    """Bad request: missing/invalid user input (HTTP 400)."""
    pass

class UnsupportedFileError(UserInputError):
    """Unsupported upload type (HTTP 400)."""
    pass

class ProcessingError(Exception):
    """Server failed while handling a valid request (HTTP 500)."""
    pass

class ExternalServiceError(Exception):
    """Upstream dependency failure (OpenAI, docx2pdf, etc.) (HTTP 502)."""
    pass