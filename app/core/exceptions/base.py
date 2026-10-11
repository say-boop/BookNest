class AppError(Exception):
    status_code = None
    error_code = None
    
    def __init__(
        self, 
        message: str,
        details: str | None = None
    ):
        self.message = message
        self.details = details


class BookAlreadyExistsError(AppError):
    status_code = 409
    error_code = "DUPLICATE_ENTITY"


class BookNotFoundError(AppError):
    status_code = 404
    error_code = "NOT FOUND"