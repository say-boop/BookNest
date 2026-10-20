from app.core.exceptions.base import AppError


class UserAlreadyExistsError(AppError):
    status_code = 409
    error_code = "DUPLICATE_ENTITY"


class UserNotFoundError(AppError):
    status_code = 404
    error_code = "NOT FOUND"