from app.core.exceptions.base import AppError


class BookAlreadyExistsError(AppError):
    status_code = 409
    error_code = "DUPLICATE_ENTITY"


class BookNotFoundError(AppError):
    status_code = 404
    error_code = "NOT_FOUND"