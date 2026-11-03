from app.core.exceptions.base import AppError


class UserAlreadyExistsError(AppError):
    status_code = 409
    error_code = "DUPLICATE_ENTITY"


class UserNotFoundError(AppError):
    status_code = 404
    error_code = "NOT_FOUND"


class UserIncorrectData(AppError):
    status_code = 400
    error_code = "INCORRECT_DATA"


class UserNotVerifiedEmail(AppError):
    status_code = 403
    error_code = "NOT_VERIFIED_EMAIL"
